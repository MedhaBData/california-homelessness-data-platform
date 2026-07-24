-- ============================================
-- California Homelessness Data Platform
-- Basic SQL Analysis
-- ============================================


-- 1. Check total rows in the age table
SELECT COUNT(*) AS total_age_rows
FROM homelessness_by_age;


-- 2. Check total rows in the race table
SELECT COUNT(*) AS total_race_rows
FROM homelessness_by_race;


-- 3. Show available calendar years
SELECT DISTINCT calendar_year
FROM homelessness_by_age
ORDER BY calendar_year;


-- 4. Total homelessness count by year
SELECT
    calendar_year,
    SUM(experiencing_homelessness_cnt) AS total_homelessness_count
FROM homelessness_by_age
GROUP BY calendar_year
ORDER BY calendar_year;


-- 5. Total homelessness count by age group
SELECT
    age_group_public,
    SUM(experiencing_homelessness_cnt) AS total_homelessness_count
FROM homelessness_by_age
GROUP BY age_group_public
ORDER BY total_homelessness_count DESC;


-- 6. Top 10 locations by homelessness count
SELECT
    location,
    SUM(experiencing_homelessness_cnt) AS total_homelessness_count
FROM homelessness_by_age
GROUP BY location
ORDER BY total_homelessness_count DESC
LIMIT 10;


-- 7. Total homelessness count by race
SELECT
    race,
    SUM(experiencing_homelessness_cnt) AS total_homelessness_count
FROM homelessness_by_race
GROUP BY race
ORDER BY total_homelessness_count DESC;


-- 8. Total homelessness count by year and race
SELECT
    calendar_year,
    race,
    SUM(experiencing_homelessness_cnt) AS total_homelessness_count
FROM homelessness_by_race
GROUP BY calendar_year, race
ORDER BY calendar_year, total_homelessness_count DESC;