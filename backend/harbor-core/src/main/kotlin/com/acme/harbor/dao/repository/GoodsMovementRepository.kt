package com.acme.harbor.dao.repository

import com.acme.harbor.dao.model.GoodsMovement
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import java.time.LocalDate
import java.util.UUID

/** Actual movement lines parsed from the daily XLS files (table `goods_movement`). */
@Repository
interface GoodsMovementRepository : JpaRepository<GoodsMovement, Long> {

    fun findAllByBatchId(batchId: UUID): List<GoodsMovement>

    @Query("select distinct m.clientId from GoodsMovement m where m.batchId = :batchId")
    fun clientIdsOfBatch(batchId: UUID): List<UUID>

    @Query("select min(m.period) from GoodsMovement m where m.batchId = :batchId")
    fun minPeriodOfBatch(batchId: UUID): LocalDate?

    @Query("select max(m.period) from GoodsMovement m where m.batchId = :batchId")
    fun maxPeriodOfBatch(batchId: UUID): LocalDate?

    /** Rolls one month of goods_movement up into movement_monthly (used by MonthlySnapshotJob). */
    @Modifying
    @Query(
        nativeQuery = true,
        value = """
            insert into movement_monthly (client_id, product_group, sub_product, city, transport_mode, direction, period, quantity, value)
            select client_id, product_group, sub_product, city, transport_mode, direction, period,
                   sum(quantity), sum(quantity * unit_price)
            from goods_movement
            where period = :period
            group by client_id, product_group, sub_product, city, transport_mode, direction, period
        """,
    )
    fun rollUpMonth(period: LocalDate): Int
}
