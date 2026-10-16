package com.acme.harbor.component

import org.slf4j.LoggerFactory
import org.springframework.boot.context.event.ApplicationReadyEvent
import org.springframework.context.ApplicationContext
import org.springframework.context.event.EventListener
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Component

/**
 * Applies the statistical views (the `.sql` files of `db/migration/statistical-views`, CREATE OR REPLACE VIEW) once the
 * application is up and Flyway has migrated the base tables. The files are not Flyway migrations: they can be
 * edited in place and are re-applied on every start.
 */
@Component
class StatisticalViewsInitializer(private val jdbc: JdbcTemplate, private val context: ApplicationContext) {

    private val log = LoggerFactory.getLogger(javaClass)

    @EventListener(ApplicationReadyEvent::class)
    fun applyViews() {
        context.getResources("classpath:db/migration/statistical-views/*.sql").sortedBy { it.filename }.forEach { resource ->
            jdbc.execute(resource.inputStream.use { String(it.readAllBytes(), Charsets.UTF_8) })
            log.info("Statistical view applied: {}", resource.filename)
        }
    }
}
