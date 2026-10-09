package harbor.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.scheduling.annotation.EnableScheduling
import java.time.Clock

/**
 * Enables the scheduled jobs of `harbor.job` (daily movement import, monthly snapshot) and provides the
 * [Clock] injected everywhere instead of `Instant.now()`, so that jobs and calculations are testable.
 */
@Configuration
@EnableScheduling
class SchedulingConfig {

    @Bean
    fun clock(): Clock = Clock.systemUTC()
}
