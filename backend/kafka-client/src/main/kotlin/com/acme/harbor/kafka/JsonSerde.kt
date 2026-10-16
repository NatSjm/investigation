package com.acme.harbor.kafka

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SerializationFeature
import org.apache.kafka.common.serialization.Deserializer
import org.apache.kafka.common.serialization.Serde
import org.apache.kafka.common.serialization.Serializer

/**
 * Jackson based [Serde] for the event payloads of `com.acme.harbor.kafka.events`.
 *
 * Payloads are plain JSON without type headers, so the external services (market-data, document-service)
 * only have to agree on the JSON shape described in `harbor-events.yaml`, not on Kotlin class names.
 */
class JsonSerde<T>(
    private val type: Class<T>,
    private val objectMapper: ObjectMapper = defaultObjectMapper(),
) : Serde<T> {

    override fun serializer(): Serializer<T> = Serializer { _, data ->
        data?.let { objectMapper.writeValueAsBytes(it) }
    }

    override fun deserializer(): Deserializer<T> = Deserializer { _, bytes ->
        bytes?.let { objectMapper.readValue(it, type) }
    }

    companion object {
        /** ObjectMapper used when the application does not pass its own: ISO dates, unknown fields ignored. */
        fun defaultObjectMapper(): ObjectMapper = ObjectMapper()
            .findAndRegisterModules()
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)

        inline fun <reified T> of(objectMapper: ObjectMapper = defaultObjectMapper()): JsonSerde<T> =
            JsonSerde(T::class.java, objectMapper)
    }
}
