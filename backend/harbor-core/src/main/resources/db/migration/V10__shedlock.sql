-- ShedLock lock table: one row per scheduled job name (SchedulingConfig / @SchedulerLock), so a job runs on one
-- instance at a time. Managed by the library; never written by application code.
CREATE TABLE shedlock (
    name varchar(64) NOT NULL PRIMARY KEY,
    lock_until timestamp NOT NULL,
    locked_at timestamp NOT NULL,
    locked_by varchar(255) NOT NULL
);
