package harbor

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.transaction.annotation.EnableTransactionManagement

/**
 * Harbor backend entry point. Component scan, JPA entities (`harbor.model`) and repositories (`harbor.dao`)
 * all live below package `harbor`, one folder per technical layer. Scheduling and Kafka are enabled in
 * `harbor.config.SchedulingConfig` / `harbor.config.KafkaConfig`; migrations are in
 * `src/main/resources/db/migration`, the REST contract in `src/main/resources/openapi/harbor-api.yaml`.
 */
@SpringBootApplication
@EnableTransactionManagement
class HarborApplication

fun main(args: Array<String>) {
    runApplication<HarborApplication>(*args)
}
