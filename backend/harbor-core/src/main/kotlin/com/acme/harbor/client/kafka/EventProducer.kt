package com.acme.harbor.client.kafka

import org.springframework.kafka.core.KafkaTemplate
import org.springframework.stereotype.Component

/**
 * The only outbound Kafka client of the application: the publishers in `event/` call [send] with a
 * the `TOPIC` constant of the listener or publisher class and the aggregate id as key. Wraps the [KafkaTemplate] built in `config/KafkaConfig`
 * (string keys, JSON values, idempotent producer) so that producers never depend on Spring Kafka directly.
 */
@Component
class EventProducer(private val kafkaTemplate: KafkaTemplate<String, Any>) {

    fun send(topic: String, key: String, payload: Any) {
        kafkaTemplate.send(topic, key, payload)
    }
}
