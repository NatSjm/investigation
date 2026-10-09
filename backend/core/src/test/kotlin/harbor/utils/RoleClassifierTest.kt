package harbor.utils

import harbor.enums.ClientRole
import harbor.enums.Direction
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

/**
 * Worked examples of calculation `client_role_classification` (quoted by docs-repo/domain/calculations).
 * Thresholds: role.min_volume = 100, role.importer_threshold = 0.65, role.exporter_threshold = 0.35.
 */
class RoleClassifierTest {

    @Test
    fun `inbound 800 outbound 200 is IMPORTER`() {
        val result = RoleClassifier.classify(bd(800), bd(200))
        assertEquals(ClientRole.IMPORTER, result.role)
        assertEquals(bd("0.8000"), result.share)
    }

    @Test
    fun `inbound 300 outbound 700 is EXPORTER`() {
        val result = RoleClassifier.classify(bd(300), bd(700))
        assertEquals(ClientRole.EXPORTER, result.role)
        assertEquals(bd("0.3000"), result.share)
    }

    @Test
    fun `inbound 500 outbound 500 is MIXED`() {
        val result = RoleClassifier.classify(bd(500), bd(500))
        assertEquals(ClientRole.MIXED, result.role)
        assertEquals(bd("0.5000"), result.share)
    }

    @Test
    fun `total below minimum volume is UNDETERMINED`() {
        // 40 + 50 = 90 < role.min_volume 100
        val result = RoleClassifier.classify(bd(40), bd(50))
        assertEquals(ClientRole.UNDETERMINED, result.role)
        assertNull(result.share)
    }

    @Test
    fun `boundary - total exactly 100 and share exactly 0_65 is IMPORTER`() {
        val result = RoleClassifier.classify(bd(65), bd(35))
        assertEquals(ClientRole.IMPORTER, result.role)
        assertEquals(bd("0.6500"), result.share)
    }

    @Test
    fun `movements are summed per direction before classification`() {
        val movements = listOf(
            RoleClassifier.Movement(Direction.IN, bd(500)),
            RoleClassifier.Movement(Direction.IN, bd(300)),
            RoleClassifier.Movement(Direction.OUT, bd(200)),
        )
        val result = RoleClassifier.classify(movements)
        assertEquals(bd(800), result.inbound)
        assertEquals(bd(200), result.outbound)
        assertEquals(ClientRole.IMPORTER, result.role)
    }
}
