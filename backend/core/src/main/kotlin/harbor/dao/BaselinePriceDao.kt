package harbor.dao

import harbor.enums.ProductGroup
import harbor.model.BaselinePrice
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.time.LocalDate

/** Baseline price / transport price curve per product group (table `baseline_price`). */
@Repository
interface BaselinePriceDao : JpaRepository<BaselinePrice, Long> {

    fun findAllByProductGroupAndPeriodBetweenOrderByPeriod(productGroup: ProductGroup, from: LocalDate, to: LocalDate): List<BaselinePrice>

    fun findByProductGroupAndPeriod(productGroup: ProductGroup, period: LocalDate): BaselinePrice?

    fun findFirstByProductGroupOrderByAsOfDesc(productGroup: ProductGroup): BaselinePrice?
}
