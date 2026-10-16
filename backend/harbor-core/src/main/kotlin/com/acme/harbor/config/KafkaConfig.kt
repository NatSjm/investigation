package com.acme.harbor.config

import com.acme.harbor.client.kafka.AvroJsonDeserializer
import com.acme.harbor.client.kafka.AvroJsonSerializer
import com.acme.harbor.event.MarketPricesListener
import com.acme.harbor.event.MovementsLoadedPublisher
import com.acme.harbor.event.ReportRenderedListener
import com.acme.harbor.event.SessionEventsPublisher
import com.acme.harbor.kafka.events.MovementsLoaded
import com.acme.harbor.kafka.events.SessionClosed
import com.acme.harbor.kafka.events.documentservice.ReportRendered
import com.acme.harbor.kafka.events.marketdata.PricesUpdated
import com.fasterxml.jackson.databind.ObjectMapper
import org.apache.avro.specific.SpecificRecord
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.common.serialization.Deserializer
import org.apache.kafka.common.serialization.Serializer
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.kafka.common.serialization.StringSerializer
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.kafka.annotation.EnableKafka
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory
import org.springframework.kafka.core.ConsumerFactory
import org.springframework.kafka.core.DefaultKafkaConsumerFactory
import org.springframework.kafka.core.DefaultKafkaProducerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.kafka.core.ProducerFactory
import org.springframework.kafka.listener.DeadLetterPublishingRecoverer
import org.springframework.kafka.listener.DefaultErrorHandler
import org.springframework.kafka.support.serializer.DelegatingByTopicDeserializer
import org.springframework.kafka.support.serializer.DelegatingByTypeSerializer
import org.springframework.kafka.support.serializer.JsonDeserializer
import org.springframework.kafka.support.serializer.JsonSerializer
import org.springframework.util.backoff.FixedBackOff
import java.util.regex.Pattern

/**
 * Kafka wiring. Keys are strings (the aggregate id). Values: the events Harbor publishes are the Avro classes
 * generated from `kafka-client/src/main/resources/avro` and travel as Avro JSON ([AvroJsonSerializer], no
 * registry); the events of the external services are plain JSON matching the JSON schemas in
 * `kafka-client/src/main/resources/json_<service>` and are read with Jackson. The topic of every record decides
 * the deserializer ([DelegatingByTopicDeserializer]); the topic names are the `TOPIC` constants of the listener and
 * publisher classes in `event/`. Failed records are retried three times and then published to `<topic>.DLT`.
 */
@Configuration
@EnableKafka
class KafkaConfig(
    @Value("\${spring.kafka.bootstrap-servers}") private val bootstrapServers: String,
    @Value("\${spring.kafka.consumer.group-id:harbor}") private val defaultGroupId: String,
    private val objectMapper: ObjectMapper,
) {

    @Bean
    fun producerFactory(): ProducerFactory<String, Any> {
        val byType: Map<Class<*>, Serializer<*>> = linkedMapOf(
            SpecificRecord::class.java to AvroJsonSerializer(),
            Any::class.java to JsonSerializer<Any>(objectMapper).apply { setAddTypeInfo(false) },
        )
        return DefaultKafkaProducerFactory(
            mapOf<String, Any>(
                ProducerConfig.BOOTSTRAP_SERVERS_CONFIG to bootstrapServers,
                ProducerConfig.ACKS_CONFIG to "all",
                ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG to true,
            ),
            StringSerializer(),
            DelegatingByTypeSerializer(byType, true),
        )
    }

    @Bean
    fun kafkaTemplate(): KafkaTemplate<String, Any> = KafkaTemplate(producerFactory())

    @Bean
    fun consumerFactory(): ConsumerFactory<String, Any> {
        val byTopic: Map<Pattern, Deserializer<*>> = linkedMapOf(
            exact(MovementsLoadedPublisher.TOPIC) to AvroJsonDeserializer(MovementsLoaded::class.java),
            exact(SessionEventsPublisher.TOPIC) to AvroJsonDeserializer(SessionClosed::class.java),
            exact(MarketPricesListener.TOPIC) to JsonDeserializer(PricesUpdated::class.java, objectMapper, false),
            exact(ReportRenderedListener.TOPIC) to JsonDeserializer(ReportRendered::class.java, objectMapper, false),
        )
        return DefaultKafkaConsumerFactory(
            mapOf<String, Any>(
                ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG to bootstrapServers,
                ConsumerConfig.GROUP_ID_CONFIG to defaultGroupId,
                ConsumerConfig.AUTO_OFFSET_RESET_CONFIG to "earliest",
                ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG to false,
            ),
            StringDeserializer(),
            DelegatingByTopicDeserializer(byTopic, JsonDeserializer<Any>(objectMapper)),
        )
    }

    @Bean
    fun kafkaListenerContainerFactory(kafkaTemplate: KafkaTemplate<String, Any>): ConcurrentKafkaListenerContainerFactory<String, Any> =
        ConcurrentKafkaListenerContainerFactory<String, Any>().apply {
            consumerFactory = consumerFactory()
            setCommonErrorHandler(
                DefaultErrorHandler(DeadLetterPublishingRecoverer(kafkaTemplate), FixedBackOff(RETRY_INTERVAL_MS, MAX_RETRIES)),
            )
            setConcurrency(1)
        }

    private fun exact(topic: String): Pattern = Pattern.compile(Pattern.quote(topic))

    companion object {
        const val RETRY_INTERVAL_MS = 1_000L
        const val MAX_RETRIES = 3L
        const val DEAD_LETTER_SUFFIX = ".DLT"
    }
}
