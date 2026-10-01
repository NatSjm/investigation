package com.bank.adv.loans

import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Component
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/v1/loans")
class LoanController {
    @GetMapping("/{clientId}/schedule")
    fun schedule(@PathVariable clientId: String): List<Any> = emptyList()

    @PutMapping("/{loanId}")
    fun update(@PathVariable loanId: String, @RequestBody body: Any) = Unit
}

@Component
class LoanRateRefreshJob {
    /** Nightly refresh of reference rates. @docs LOAN-RATES-JOB */
    @Scheduled(cron = "0 0 2 * * *")
    fun refresh() = Unit
}
