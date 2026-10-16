-- Statistical view, not a Flyway migration (no V/R prefix: Flyway lists it with a warning and skips it).
-- Applied by component/StatisticalViewsInitializer after every start with CREATE OR REPLACE, so the definition can
-- change in place. Read-only reporting helper; the application reads the base tables through the repositories.
CREATE OR REPLACE VIEW v_client_overview AS
SELECT p.id AS client_id,
       p.external_ref,
       p.name,
       p.country,
       count(s.id) FILTER (WHERE s.status = 'OPEN') AS open_sessions,
       max(s.started_at) AS last_session_at
FROM client_profile p
LEFT JOIN meeting_session s ON s.client_id = p.id
GROUP BY p.id, p.external_ref, p.name, p.country;
