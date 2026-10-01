// TEMPLATE - copy to <be-repo>/<app-module>/src/test/kotlin/com/bank/adv/docs/GraphExportTest.kt
// Not compiled in the investigation workspace (be-mini has no Spring classpath); verify on the real repo.
//
// Exports the *real* architectural graph from the running Spring context, which the regex maps can only
// approximate: DI edges through interfaces, exact request mappings, Kafka listeners, JPA entity -> table.
// Zero new libraries: everything below is in spring-boot-starter-test / -web / -data-jpa / spring-kafka,
// which a 2-year Spring Boot service already depends on. Output: docs/_generated/graph-export-be.json,
// consumed by the docs repo `scripts/gen-graph.ps1` (edges tagged source=export win over regex edges).
//
// Run in CI after the unit tests:   mvn -pl app -Dtest=GraphExportTest -Ddocs.graph=true test
// Guard: @EnabledIfSystemProperty so it never runs in the normal developer test loop.
package com.bank.adv.docs

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

        // 1. classes + module (community) from the package: com.bank.adv.<module>...
        for (name in appBeans) {
            val type = bf.getType(name) ?: continue
            node("class:${type.simpleName}", "class", type.simpleName, moduleOf(type), "be",
                location = type.name.replace('.', '/') + ".kt", note = roleOf(type))
            edge("module:${moduleOf(type)}", "class:${type.simpleName}", "contains")
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
                node(id, "endpoint", "$v $p", moduleOf(method.beanType), "be",
                    note = "handler $cls.${method.method.name}")
                edge(id, "class:$cls", "handled-by")
                edge("module:${moduleOf(method.beanType)}", id, "exposes")
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
        // 5. JPA entity -> table (+ repository -> table via generic type)
        em?.metamodel?.entities?.forEach { e ->
            val table = e.javaType.getAnnotation(Table::class.java)?.name?.ifBlank { null } ?: toSnake(e.name)
            node("table:$table", "table", table, moduleOf(e.javaType), "be")
            edge("class:${e.javaType.simpleName}", "table:$table", "persists-to")
            appBeans.mapNotNull { bf.getType(it) }
                .filter { it.simpleName.endsWith("Repository") && repoEntity(it) == e.javaType }
                .forEach { edge("class:${it.simpleName}", "table:$table", "persists-to") }
        }

        val out = File(System.getProperty("docs.graph.out", "docs/_generated/graph-export-be.json"))
        out.parentFile.mkdirs()
        out.writeText(toJson(), StandardCharsets.UTF_8)
        println("graph-export: ${nodes.size} nodes, ${edges.size} edges -> $out")
    }

    // ---- helpers ------------------------------------------------------------------------------
    private fun isOurs(bf: ConfigurableListableBeanFactory, name: String) =
        bf.getType(name)?.name?.startsWith("com.bank.adv.") == true

    private fun moduleOf(type: Class<*>): String =
        type.name.removePrefix("com.bank.adv.").substringBefore('.').ifBlank { "be-root" }

    private fun roleOf(type: Class<*>): String = when {
        type.simpleName.endsWith("Controller") -> "controller"
        type.simpleName.endsWith("Facade") -> "facade"
        type.simpleName.endsWith("Repository") -> "repository"
        type.simpleName.endsWith("Calculator") -> "calculator"
        type.simpleName.contains("Publisher") -> "producer"
        type.simpleName.contains("Listener") || type.simpleName.endsWith("Events") -> "listener"
        else -> ""
    }

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
