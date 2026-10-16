package com.acme.harbor.client.kafka

import org.apache.avro.io.DecoderFactory
import org.apache.avro.io.EncoderFactory
import org.apache.avro.specific.SpecificData
import org.apache.avro.specific.SpecificDatumReader
import org.apache.avro.specific.SpecificDatumWriter
import org.apache.avro.specific.SpecificRecord
import org.apache.kafka.common.serialization.Deserializer
import org.apache.kafka.common.serialization.Serializer
import java.io.ByteArrayOutputStream

/**
 * Avro JSON encoding of the generated event classes of `kafka-client` (schemas in `src/main/resources/avro`):
 * the schema is the class, no registry involved. Wired by `config/KafkaConfig` for the topics Harbor publishes.
 */
class AvroJsonSerializer : Serializer<SpecificRecord> {

    override fun serialize(topic: String?, data: SpecificRecord?): ByteArray? = data?.let { record ->
        ByteArrayOutputStream().use { out ->
            val encoder = EncoderFactory.get().jsonEncoder(record.schema, out)
            SpecificDatumWriter<SpecificRecord>(record.schema).write(record, encoder)
            encoder.flush()
            out.toByteArray()
        }
    }
}

/** Counterpart of [AvroJsonSerializer] for one generated class (one instance per topic in `KafkaConfig`). */
class AvroJsonDeserializer<T : SpecificRecord>(private val type: Class<T>) : Deserializer<T> {

    private val schema = SpecificData.get().getSchema(type)

    override fun deserialize(topic: String?, data: ByteArray?): T? = data?.let { bytes ->
        SpecificDatumReader(type).read(null, DecoderFactory.get().jsonDecoder(schema, String(bytes, Charsets.UTF_8)))
    }
}
