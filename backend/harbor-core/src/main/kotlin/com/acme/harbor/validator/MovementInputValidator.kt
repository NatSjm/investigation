package com.acme.harbor.validator

import com.acme.harbor.enums.ProductGroup
import com.acme.harbor.exception.ValidationException
import com.acme.harbor.service.ProjectionService.MovementInputCommand
import com.acme.harbor.utils.MonthGrid
import org.springframework.stereotype.Component

/**
 * Rules for the modelled movements of the movement modal (`putProduct1Movements`, `putProduct2Movements`):
 * - every period lies inside the session horizon,
 * - the sub-product belongs to the product group of the session,
 * - quantity > 0 and unit price >= 0,
 * - Product 1 rows carry a known city hub, Product 2 rows a transport mode (the breakdown dimension).
 * @docs P1-002
 * @docs P2-002
 */
@Component
class MovementInputValidator {

    fun validate(productGroup: ProductGroup, grid: MonthGrid, inputs: List<MovementInputCommand>) {
        inputs.forEach { input ->
            ValidationException.check(grid.contains(input.period)) { "period ${input.period} is outside the session horizon" }
            ValidationException.check(input.subProduct in productGroup.subProducts) {
                "sub-product ${input.subProduct} does not belong to ${productGroup.wireValue}"
            }
            ValidationException.check(input.quantity.signum() > 0) { "quantity must be positive" }
            ValidationException.check(input.unitPrice.signum() >= 0) { "unitPrice must not be negative" }
            when (productGroup) {
                ProductGroup.PRODUCT1 -> ValidationException.check(input.city != null && input.city in ProductGroup.PRODUCT1_CITIES) {
                    "city is required for Product 1 movements and must be one of ${ProductGroup.PRODUCT1_CITIES}"
                }
                ProductGroup.PRODUCT2 -> ValidationException.check(input.transportMode != null) {
                    "transportMode is required for Product 2 movements"
                }
            }
        }
    }
}
