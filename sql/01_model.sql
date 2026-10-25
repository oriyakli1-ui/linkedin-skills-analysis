-- 01_model.sql : star-schema tables for Power BI
-- Input tables (created by pipeline.py): postings, job_skill_mined, job_skill_linkedin, skill_dict

CREATE INDEX IF NOT EXISTS ix_post_role ON postings(role);
CREATE INDEX IF NOT EXISTS ix_ms_job    ON job_skill_mined(job_id);
CREATE INDEX IF NOT EXISTS ix_ms_skill  ON job_skill_mined(skill);

DROP TABLE IF EXISTS dim_role;
CREATE TABLE dim_role AS
SELECT role,
       CASE role WHEN 'Product Manager' THEN 1 WHEN 'Project Manager' THEN 2 ELSE 3 END AS role_order
FROM (SELECT DISTINCT role FROM postings);

DROP TABLE IF EXISTS dim_skill;
CREATE TABLE dim_skill AS SELECT skill, category FROM skill_dict;

DROP TABLE IF EXISTS fact_postings;
CREATE TABLE fact_postings AS
SELECT job_id, role, title, company_name, location, work_type, remote_allowed, listed_date, source
FROM postings;

DROP TABLE IF EXISTS fact_job_skill;
CREATE TABLE fact_job_skill AS SELECT job_id, skill FROM job_skill_mined;
