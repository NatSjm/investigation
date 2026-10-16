package com.acme.harbor.config

import com.fasterxml.jackson.databind.ObjectMapper
import com.acme.harbor.kafka.HarborKafkaClient
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.kafka.annotation.EnableKafka
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory
import org.springframework.kafka.core.ConsumerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.kafka.core.ProducerFactory
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer
import org.springframework.kafka.listener.DefaultErrorHandler
import org.springframework.kafka.support.converter.StringJsonMessageConverter
import org.springframework.util.backoff.FixedBackOff

/**
 * Kafka wiring on top of the shared `kafka-client` library ([HarborKafkaClient]). Payloads are JSON without
 * type headers: producers serialize the classes of `com.acme.harbor.kafka.events`, consumers convert by the
 * listener parameter type, so the external services (market-data, document-service) only have to agree
 * on the JSON shape in `openapi/harbor-events.yaml`. Failed records are retried three times and then published
 * to `<topic>.DLT`.
 */
@Configuration
@EnableKafka
class KafkaConfig(
    @Value("\${spring.kafka.bootstrap-servers}") private val bootstrapServers: String,
    @Value("\${spring.kafka.consumer.group-id:harbor}") private val defaultGroupId: String,
    private val objectMapper: ObjectMapper,
) {

    @Bean
    fun producerFactory(): ProducerFactory<String, Any> = HarborKafkaClient.producerFactory(bootstrapServers, objectMapper)

    @Bean
    fun kafkaTemplate(): KafkaTemplate<String, Any> = KafkaTemplate(producerFactory())

    @Bean
    fun consumerFactory(): ConsumerFactory<String, String> = HarborKafkaClient.consumerFactory(bootstrapServers, defaultGroupId)

    @Bean
    fun kafkaListenerContainerFactory(kafkaTemplate: KafkaTemplate<String, Any>): ConcurrentKafkaListenerContainerFactory<String, String> =
        ConcurrentKafkaListenerContainerFactory<String, String>().apply {
            consumerFactory = consumerFactory()
            setRecordMessageConverter(StringJsonMessageConverter(objectMapper))
            setCommonErrorHandler(
                DefaultErrorHandler(DeadLetterPublishingRecoverer(kafkaTemplate), FixedBackOff(RETRY_INTERVAL_MS, MAX_RETRIES)),
            )
            setConcurrency(1)
        }

    companion object {
        const val RETRY_INTERVAL_MS = 1_000L
        const val MAX_RETRIES = 3L
    }
}
