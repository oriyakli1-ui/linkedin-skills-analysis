-- 02_skill_scores.sql : "Which 3 skills help me most to become <role>?"
--
-- For every (role, skill):
--   DEMAND       share of that role's postings that ask for the skill  -> this is the ranking
--   SPECIFICITY  demand in this role / demand in the other two roles   -> shown for context only
-- Rank 1 is simply the skill with the highest demand_pct (within hard skills, and separately within soft skills).
-- Skills with fewer than 20 postings are dropped.

DROP TABLE IF EXISTS skill_stats;
CREATE TABLE skill_stats AS
WITH role_n AS (
    SELECT role, COUNT(*) AS n_postings FROM postings GROUP BY role
),
total AS (
    SELECT SUM(n_postings) AS total_postings FROM role_n
),
with_skill AS (
    -- tot_with is computed BEFORE the n_with >= 20 filter so rare-in-other-roles skills aren't miscounted
    SELECT p.role, m.skill, COUNT(*) AS n_with,
           SUM(COUNT(*)) OVER (PARTITION BY m.skill) AS tot_with
    FROM postings p
    JOIN job_skill_mined m ON m.job_id = p.job_id
    GROUP BY p.role, m.skill
)
SELECT w.role, w.skill,
       n.n_postings,
       w.n_with,
       1.0 * w.n_with / n.n_postings AS demand_pct,
       -- demand of the same skill in the OTHER roles
       1.0 * (w.tot_with - w.n_with) / NULLIF(t.total_postings - n.n_postings, 0) AS demand_pct_other_roles
FROM with_skill w
JOIN role_n n ON n.role = w.role
CROSS JOIN total t
WHERE w.n_with >= 20;

DROP TABLE IF EXISTS skill_scores;
CREATE TABLE skill_scores AS
WITH enriched AS (
    SELECT st.*, d.category,
           demand_pct / NULLIF(demand_pct_other_roles, 0) AS specificity_lift
    FROM skill_stats st
    JOIN skill_dict d ON d.skill = st.skill
),
scored AS (
    SELECT role, skill, category,
           -- Soft skills (communication, stakeholders...) appear in nearly every posting, so
           -- they are ranked separately and never crowd out the skills you can actually learn.
           CASE WHEN category = 'Soft / Management' THEN 'Soft' ELSE 'Hard' END AS skill_type,
           n_postings, n_with, demand_pct, specificity_lift,
           demand_pct AS score
    FROM enriched
)
SELECT *,
       ROW_NUMBER() OVER (PARTITION BY role, skill_type
                          ORDER BY demand_pct DESC, n_with DESC) AS skill_rank
FROM scored;

-- The headline answer: top 3 learnable (hard) skills per role
DROP VIEW IF EXISTS v_top3;
CREATE VIEW v_top3 AS
SELECT role, skill_rank, skill, category,
       ROUND(100 * demand_pct, 1)  AS demand_pct,
       ROUND(specificity_lift, 2)  AS specificity_lift,
       ROUND(score, 3)             AS score
FROM skill_scores
WHERE skill_type = 'Hard' AND skill_rank <= 3
ORDER BY role, skill_rank;

-- LinkedIn's own "Skills" categories (the structured field on LinkedIn job postings)
DROP TABLE IF EXISTS linkedin_skill_stats;
CREATE TABLE linkedin_skill_stats AS
SELECT p.role, l.skill_name,
       COUNT(DISTINCT p.job_id) AS n_with,
       1.0 * COUNT(DISTINCT p.job_id) / n.n_postings AS demand_pct
FROM postings p
JOIN job_skill_linkedin l ON l.job_id = p.job_id
JOIN (SELECT role, COUNT(*) AS n_postings FROM postings GROUP BY role) n ON n.role = p.role
GROUP BY p.role, l.skill_name;
