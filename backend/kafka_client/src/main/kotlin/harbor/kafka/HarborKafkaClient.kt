package harbor.kafka

import com.fasterxml.jackson.databind.ObjectMapper
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.kafka.common.serialization.StringSerializer
import org.springframework.kafka.core.ConsumerFactory
import org.springframework.kafka.core.DefaultKafkaConsumerFactory
import org.springframework.kafka.core.DefaultKafkaProducerFactory
import org.springframework.kafka.core.KafkaTemplate
import org.springframework.kafka.core.ProducerFactory

/**
 * Producer / consumer helper shared by every Harbor service that talks to the Harbor topics.
 *
 * Builds the factories with the agreed settings: string keys (the aggregate id), JSON values without type
 * headers ([JsonSerde]), idempotent producer with `acks=all`, consumers starting at `earliest` with commits
 * handled by the Spring listener container. The core application wires these in `KafkaConfig`; the
 * producers in `core/.../harbor/event/` then publish through the resulting `KafkaTemplate` with a [Topics] constant.
 */
object HarborKafkaClient {

    const val DEAD_LETTER_SUFFIX = ".DLT"

    fun producerProperties(bootstrapServers: String): Map<String, Any> = mapOf(
        ProducerConfig.BOOTSTRAP_SERVERS_CONFIG to bootstrapServers,
        ProducerConfig.ACKS_CONFIG to "all",
        ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG to true,
    )

    fun consumerProperties(bootstrapServers: String, groupId: String): Map<String, Any> = mapOf(
        ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG to bootstrapServers,
        ConsumerConfig.GROUP_ID_CONFIG to groupId,
        ConsumerConfig.AUTO_OFFSET_RESET_CONFIG to "earliest",
        ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG to false,
    )

    fun producerFactory(bootstrapServers: String, objectMapper: ObjectMapper): ProducerFactory<String, Any> =
        DefaultKafkaProducerFactory(
            producerProperties(bootstrapServers),
            StringSerializer(),
            JsonSerde(Any::class.java, objectMapper).serializer(),
        )

    /** Consumers read the raw JSON string; the listener container converts it to the listener parameter type. */
    fun consumerFactory(bootstrapServers: String, groupId: String): ConsumerFactory<String, String> =
        DefaultKafkaConsumerFactory(
            consumerProperties(bootstrapServers, groupId),
            StringDeserializer(),
            StringDeserializer(),
        )

    fun kafkaTemplate(bootstrapServers: String, objectMapper: ObjectMapper): KafkaTemplate<String, Any> =
        KafkaTemplate(producerFactory(bootstrapServers, objectMapper))

    fun deadLetterTopic(topic: String): String = topic + DEAD_LETTER_SUFFIX
}
