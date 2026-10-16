package com.acme.harbor.config

import net.javacrumbs.shedlock.core.LockProvider
import net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateLockProvider
import net.javacrumbs.shedlock.spring.annotation.EnableSchedulerLock
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.scheduling.annotation.EnableScheduling
import java.time.Clock
import javax.sql.DataSource

/**
 * Enables the scheduled jobs of `com.acme.harbor.job` (daily movement import, monthly snapshot), guarded by
 * ShedLock so that a job runs on one instance at a time (`@SchedulerLock` on the job method, lock rows in table
 * `shedlock`, V10__shedlock.sql), and provides the [Clock] injected everywhere instead of `Instant.now()`.
 */
@Configuration
@EnableScheduling
@EnableSchedulerLock(defaultLockAtMostFor = "PT30M")
class SchedulingConfig {

    @Bean
    fun clock(): Clock = Clock.systemUTC()

    @Bean
    fun lockProvider(dataSource: DataSource): LockProvider = JdbcTemplateLockProvider(
        JdbcTemplateLockProvider.Configuration.builder()
            .withJdbcTemplate(JdbcTemplate(dataSource))
            .usingDbTime()
            .build(),
    )
}
