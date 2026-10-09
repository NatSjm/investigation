-- Executed once by the postgres container on first start (docker-entrypoint-initdb.d).
-- The schema itself is created by Flyway from core/src/main/resources/db/migration (V1..V9) when the
-- application starts; this script only prepares the database and a separate one for integration tests.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER DATABASE harbor SET timezone TO 'UTC';

CREATE DATABASE harbor_test OWNER harbor;
\connect harbor_test
CREATE EXTENSION IF NOT EXISTS pgcrypto;
ALTER DATABASE harbor_test SET timezone TO 'UTC';
