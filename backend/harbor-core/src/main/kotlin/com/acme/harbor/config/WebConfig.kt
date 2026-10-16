package com.acme.harbor.config

import com.acme.harbor.context.CurrentUser
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.web.context.request.RequestContextHolder
import org.springframework.web.context.request.ServletRequestAttributes
import org.springframework.web.servlet.config.annotation.CorsRegistry
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer

/**
 * MVC configuration: CORS for the frontend dev server and the [CurrentUser] bean. The session header filter
 * is a plain `@Component` (`com.acme.harbor.component.SessionHeaderFilter`); error bodies come from
 * `com.acme.harbor.advice.GlobalExceptionAdvice`.
 */
@Configuration
class WebConfig(
    @Value("\${harbor.web.allowed-origins:http://localhost:5173}") private val allowedOrigins: List<String>,
    @Value("\${harbor.session.header:X-Harbor-Session}") private val sessionHeader: String,
) : WebMvcConfigurer {

    override fun addCorsMappings(registry: CorsRegistry) {
        registry.addMapping("/**")
            .allowedOrigins(*allowedOrigins.toTypedArray())
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("Authorization", "Content-Type", sessionHeader, CurrentUser.HEADER)
            .exposedHeaders("Content-Disposition")
    }

    /**
     * Identity of the representative. The gateway in front of this service validates the bearer token and
     * forwards the subject in `X-Harbor-User`; outside a request (jobs, listeners) the user is `system`.
     */
    @Bean
    fun currentUser(): CurrentUser = CurrentUser {
        (RequestContextHolder.getRequestAttributes() as? ServletRequestAttributes)
            ?.request
            ?.getHeader(CurrentUser.HEADER)
            ?.takeIf { it.isNotBlank() }
            ?: CurrentUser.SYSTEM
    }
}
