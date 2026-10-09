-- Meeting report: JSON payload built when the session is closed and the PDF rendered by document-service.

CREATE TABLE meeting_report (
    session_id uuid PRIMARY KEY REFERENCES meeting_session(id),
    payload jsonb NOT NULL,
    pdf_path varchar(512),
    status varchar(16) NOT NULL DEFAULT 'PENDING',
    rendered_at timestamp,
    CONSTRAINT ck_meeting_report_status CHECK (status IN ('PENDING', 'REQUESTED', 'RENDERED', 'FAILED'))
);
