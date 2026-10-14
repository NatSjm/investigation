// TEMPLATE - copy to harbor-backend/core/src/test/kotlin/harbor/docs/GraphExportTest.kt
// Not compiled in the investigation workspace (no Spring classpath here); verify on the real repo.
//
// Exports the *real* architectural graph from the running Spring context, which the regex maps can only
// approximate: DI edges through interfaces, exact request mappings, Kafka listeners, JPA entity -> table.
// Zero new libraries: everything below is in spring-boot-starter-test / -web / -data-jpa / spring-kafka,
// which a 2-year Spring Boot service already depends on. Output: docs/_generated/graph-export-be.json,
// consumed by the docs repo `scripts/gen-graph.py` (edges tagged source=export win over regex edges).
//
// Run in CI after the unit tests:   mvn -pl core -am -Dtest=GraphExportTest -Ddocs.graph=true test
// Guard: @EnabledIfSystemProperty so it never runs in the normal developer test loop.
package harbor.docs

import jakarta.persistence.EntityManager
import jakarta.persistence.Table
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledIfSystemProperty
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.context.ConfigurableApplicationContext
import org.springframework.kafka.config.KafkaListenerEndpointRegistry
import org.springframework.test.context.ActiveProfiles
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping
import java.io.File
import java.nio.charset.StandardCharsets

@SpringBootTest
@ActiveProfiles("graph-export")           // profile with embedded/mocked infra: no real DB/Kafka needed to wire beans
@EnabledIfSystemProperty(named = "docs.graph", matches = "true")
class GraphExportTest {

    @Autowired lateinit var ctx: ConfigurableApplicationContext
    @Autowired lateinit var mappings: RequestMappingHandlerMapping
    @Autowired(required = false) var kafkaRegistry: KafkaListenerEndpointRegistry? = null
    @Autowired(required = false) var em: EntityManager? = null

    private val nodes = LinkedHashMap<String, Map<String, Any?>>()
    private val edges = LinkedHashSet<Map<String, String>>()

    @Test
    fun export() {
        val bf = ctx.beanFactory
        val appBeans = bf.beanDefinitionNames.filter { isOurs(bf, it) }

        // 1. classes with their layer (package segment after the base package: harbor.<layer>...). The business context
        for (name in appBeans) {
            val type = bf.getType(name) ?: continue
        //    (community) is assigned by the docs repo from the class-name prefix (contexts.yml), so it is left empty here.
            node("class:${type.simpleName}", "class", type.simpleName, "", "be",
                location = "core/src/main/kotlin/" + type.name.replace('.', '/') + ".kt", note = layerOf(type))
        }
        // 2. DI edges - the ones regex cannot see through interfaces
        for (name in appBeans) {
            val from = bf.getType(name)?.simpleName ?: continue
            for (dep in bf.getDependenciesForBean(name)) {
                val to = bf.getType(dep)?.takeIf { isOurs(bf, dep) }?.simpleName ?: continue
                edge("class:$from", "class:$to", "depends-on")
            }
        }
        // 3. exact request mappings
        for ((info, method) in mappings.handlerMethods) {
            val paths = info.pathPatternsCondition?.patternValues ?: info.patternsCondition?.patterns ?: emptySet()
            val verbs = info.methodsCondition.methods.ifEmpty { setOf("ANY") }
            for (p in paths) for (v in verbs) {
                val id = "endpoint:$v $p"
                val cls = method.beanType.simpleName
                node(id, "endpoint", "$v $p", "", "be",
                    note = "handler $cls.${method.method.name}")
                edge(id, "class:$cls", "handled-by")
            }
        }
        // 4. Kafka consumers (producers stay regex-detected: KafkaTemplate.send(Topics.X, ...))
        kafkaRegistry?.listenerContainers?.forEach { c ->
            val topics = c.containerProperties.topics?.toList() ?: emptyList()
            val bean = (c.containerProperties.messageListener)?.javaClass?.simpleName ?: c.listenerId
            for (t in topics) {
                node("topic:$t", "topic", t, "external", "kafka")
                edge("topic:$t", "class:$bean", "consumed-by")
            }
        }
        // 5. JPA entity -> table (+ dao -> table via the Spring Data generic type)
        em?.metamodel?.entities?.forEach { e ->
            val table = e.javaType.getAnnotation(Table::class.java)?.name?.ifBlank { null } ?: toSnake(e.name)
            node("table:$table", "table", table, "", "be")
            edge("class:${e.javaType.simpleName}", "table:$table", "persists-to")
            appBeans.mapNotNull { bf.getType(it) }
                .filter { it.simpleName.endsWith("Dao") && repoEntity(it) == e.javaType }
                .forEach { edge("class:${it.simpleName}", "table:$table", "persists-to") }
        }

        val out = File(System.getProperty("docs.graph.out", "docs/_generated/graph-export-be.json"))
        out.parentFile.mkdirs()
        out.writeText(toJson(), StandardCharsets.UTF_8)
        println("graph-export: ${nodes.size} nodes, ${edges.size} edges -> $out")
    }

    // ---- helpers ------------------------------------------------------------------------------
    private fun isOurs(bf: ConfigurableListableBeanFactory, name: String) =
        bf.getType(name)?.name?.startsWith("harbor.") == true

    // layer = package segment after the base package (harbor.api.X -> api); empty for the package root
    private fun layerOf(type: Class<*>): String =
        type.name.removePrefix("harbor.").substringBeforeLast('.', "").substringBefore('.')

    private fun repoEntity(repo: Class<*>): Class<*>? =
        repo.genericInterfaces.filterIsInstance<java.lang.reflect.ParameterizedType>()
            .firstOrNull()?.actualTypeArguments?.firstOrNull() as? Class<*>

    private fun toSnake(s: String) = s.replace(Regex("([a-z])([A-Z])"), "$1_$2").lowercase()

    private fun node(id: String, kind: String, label: String, community: String, repo: String,
                     location: String = "", note: String = "") {
        nodes.putIfAbsent(id, mapOf("id" to id, "kind" to kind, "label" to label, "community" to community,
            "repo" to repo, "location" to location, "note" to note))
    }
    private fun edge(from: String, to: String, rel: String) { edges += mapOf("from" to from, "to" to to, "rel" to rel) }

    // Tiny JSON writer to avoid declaring a Jackson/kotlinx dependency on the test classpath explicitly.
    private fun toJson(): String {
        fun q(v: Any?) = "\"" + v.toString().replace("\\", "\\\\").replace("\"", "\\\"") + "\""
        fun obj(m: Map<String, Any?>) = m.entries.joinToString(",", "{", "}") { "${q(it.key)}:${q(it.value)}" }
        return """{"generated":{"by":"process:graph-export-be"},"nodes":[${nodes.values.joinToString(",") { obj(it) }}],"edges":[${edges.joinToString(",") { obj(it) }}]}"""
    }
}
