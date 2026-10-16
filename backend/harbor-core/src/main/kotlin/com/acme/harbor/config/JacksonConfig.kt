package com.acme.harbor.config

import com.fasterxml.jackson.databind.module.SimpleModule
import com.acme.harbor.databind.MoneySerializer
import com.acme.harbor.databind.PeriodDeserializer
import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import java.math.BigDecimal
import java.time.YearMonth

/**
 * Jackson setup shared by REST and Kafka: amounts are written as plain JSON numbers keeping their scale
 * ([MoneySerializer]) and months accept `YYYY-MM` as well as `YYYY-MM-DD` ([PeriodDeserializer]).
 * Dates are ISO strings (`spring.jackson.serialization.write-dates-as-timestamps: false`).
 */
@Configuration
class JacksonConfig {

    @Bean
    fun harborJacksonCustomizer(): Jackson2ObjectMapperBuilderCustomizer = Jackson2ObjectMapperBuilderCustomizer { builder ->
        builder.modulesToInstall(
            SimpleModule("harbor")
                .addSerializer(BigDecimal::class.java, MoneySerializer())
                .addDeserializer(YearMonth::class.java, PeriodDeserializer()),
        )
    }
}
