package com.acme.harbor.dao.repository

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.dao.model.BaselinePrice
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.time.LocalDate

/** Baseline price / transport price curve per product group (table `baseline_price`). */
@Repository
interface BaselinePriceRepository : JpaRepository<BaselinePrice, Long> {

    fun findAllByProductGroupAndPeriodBetweenOrderByPeriod(productGroup: ProductGroup, from: LocalDate, to: LocalDate): List<BaselinePrice>

    fun findByProductGroupAndPeriod(productGroup: ProductGroup, period: LocalDate): BaselinePrice?

    fun findFirstByProductGroupOrderByAsOfDesc(productGroup: ProductGroup): BaselinePrice?
}
