package harbor.model

import harbor.enums.ImportStatus
import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import java.time.Instant
import java.util.UUID

/** One imported XLS file (table `import_batch`, V3__movements.sql). Shown on the admin import monitor. */
@Entity
@Table(name = "import_batch")
class ImportBatch(
    @Id
    @Column(name = "id", nullable = false)
    val id: UUID = UUID.randomUUID(),

    @Column(name = "source_file", nullable = false)
    val sourceFile: String,

    @Column(name = "received_at", nullable = false)
    val receivedAt: Instant,

    @Column(name = "rows_total", nullable = false)
    var rowsTotal: Int = 0,

    @Column(name = "rows_rejected", nullable = false)
    var rowsRejected: Int = 0,

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    var status: ImportStatus = ImportStatus.RUNNING,
) {
    fun finish(total: Int, rejected: Int) {
        rowsTotal = total
        rowsRejected = rejected
        status = ImportStatus.DONE
    }

    fun fail() {
        status = ImportStatus.FAILED
    }
}
