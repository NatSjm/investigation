package harbor.dao

import harbor.model.ImportBatch
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.UUID

/** One row per imported XLS file (table `import_batch`). */
@Repository
interface ImportBatchDao : JpaRepository<ImportBatch, UUID> {

    fun findTop50ByOrderByReceivedAtDesc(): List<ImportBatch>

    fun findFirstByOrderByReceivedAtDesc(): ImportBatch?

    fun existsBySourceFile(sourceFile: String): Boolean
}
