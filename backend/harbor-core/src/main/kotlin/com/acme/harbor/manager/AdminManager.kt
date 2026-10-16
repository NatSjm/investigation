package com.acme.harbor.manager

import com.acme.harbor.context.CurrentUser
import com.acme.harbor.enums.ImportStatus
import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.ImportBatch
import com.acme.harbor.dao.model.Parameter
import com.acme.harbor.service.MovementImportService
import com.acme.harbor.service.ParameterService
import com.acme.harbor.validator.ParameterValidator
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.Clock
import java.time.Instant
import java.time.LocalDate

/**
 * Administration outside meetings: the parameter sets (tariff rates, handling and transport costs, role
 * thresholds, defaults) and the import monitor (batches of the daily XLS import, manual trigger).
 *
 * @docs ADM-001
 */
@Service
class AdminManager(
    private val parameterService: ParameterService,
    private val parameterValidator: ParameterValidator,
    private val importService: MovementImportService,
    private val currentUser: CurrentUser,
    private val clock: Clock,
) {

    /** Request body of `upsertParameter` without the author, which is taken from [CurrentUser]. */
    data class ParameterChange(
        val scopeProductGroup: ProductGroup?,
        val scopeCountry: String?,
        val scopeValue: String?,
        val value: BigDecimal,
        val validFrom: LocalDate?,
    )

    @Transactional(readOnly = true)
    fun listParameters(productGroup: ProductGroup?): List<Parameter> = parameterService.list(productGroup)

    @Transactional
    fun upsertParameter(key: String, change: ParameterChange): Parameter {
        val parameterKey = parameterValidator.validate(key, change.value)
        return parameterService.upsert(
            parameterKey,
            ParameterService.Upsert(
                scopeProductGroup = change.scopeProductGroup,
                scopeCountry = change.scopeCountry,
                scopeValue = change.scopeValue,
                value = change.value,
                validFrom = change.validFrom,
                updatedBy = currentUser.id(),
            ),
        )
    }

    fun listImportBatches(): List<ImportBatch> = importService.recentBatches()

    /** Runs the daily import now; returns the first batch created, or a transient DONE batch when nothing was new. */
    fun triggerImport(): ImportBatch =
        importService.importNewFiles(MovementImportService.Trigger.MANUAL).firstOrNull()
            ?: ImportBatch(sourceFile = "(no new files)", receivedAt = Instant.now(clock), status = ImportStatus.DONE)
}
