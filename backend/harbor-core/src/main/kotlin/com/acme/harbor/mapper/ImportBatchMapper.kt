package com.acme.harbor.mapper

import com.acme.harbor.api.generated.model.ImportBatchDto
import java.time.ZoneOffset
import com.acme.harbor.dao.model.ImportBatch as ImportBatchEntity

/** Maps import batches (admin import monitor) to the generated API model. */
object ImportBatchMapper {

    fun batch(b: ImportBatchEntity) = ImportBatchDto(
        batchId = b.id,
        sourceFile = b.sourceFile,
        receivedAt = b.receivedAt.atOffset(ZoneOffset.UTC),
        rowsTotal = b.rowsTotal,
        rowsRejected = b.rowsRejected,
        status = ImportBatchDto.Status.valueOf(b.status.name),
    )
}
