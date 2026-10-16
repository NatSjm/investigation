package com.acme.harbor

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.transaction.annotation.EnableTransactionManagement

/**
 * Harbor backend entry point. Component scan, JPA entities (`com.acme.harbor.dao.model`) and repositories
 * (`com.acme.harbor.dao.repository`) all live below package `com.acme.harbor`, one folder per technical layer
 * (`api`, `manager`, `service`, `dao`, `event`, `job`, `utils`, ...). Scheduling and Kafka are enabled in
 * `config/SchedulingConfig` / `config/KafkaConfig`; migrations are in `src/main/resources/db/migration`,
 * the REST contract in `src/main/resources/openapi/openapi_harbor.yaml`.
 */
@SpringBootApplication
@EnableTransactionManagement
class HarborBackendApplication

fun main(args: Array<String>) {
    runApplication<HarborBackendApplication>(*args)
}
