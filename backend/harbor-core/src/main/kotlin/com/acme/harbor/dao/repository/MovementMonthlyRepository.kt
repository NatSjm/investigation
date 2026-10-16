package com.acme.harbor.dao.repository

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.MovementMonthly
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDate
import java.util.UUID

/** Monthly rollup of the actual movements (table `movement_monthly`). */
@Repository
interface MovementMonthlyRepository : JpaRepository<MovementMonthly, Long> {

    fun findAllByClientIdAndProductGroupAndPeriodBetween(
        clientId: UUID,
        productGroup: ProductGroup,
        from: LocalDate,
        to: LocalDate,
    ): List<MovementMonthly>

    /** Monthly quantities of every client of a segment (peer benchmark input). */
    @Query(
        """
        select m from MovementMonthly m
        where m.productGroup = :productGroup
          and m.period between :from and :to
          and m.clientId in (select p.id from ClientProfile p where p.segment = :segment)
        """,
    )
    fun findAllBySegment(productGroup: ProductGroup, segment: String, from: LocalDate, to: LocalDate): List<MovementMonthly>

    @Modifying
    fun deleteAllByPeriod(period: LocalDate): Int
}
