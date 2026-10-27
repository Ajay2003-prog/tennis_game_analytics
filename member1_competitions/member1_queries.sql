
-- MEMBER 1: TENNIS COMPETITIONS ANALYSIS
-- Database: data/tennis_competitions.db

-- 1. List competitions with their category names
SELECT
    c.competition_id,
    c.competition_name,
    cat.category_name,
    c.type,
    c.gender
FROM Competitions AS c
JOIN Categories AS cat
    ON c.category_id = cat.category_id
ORDER BY cat.category_name, c.competition_name;

-- 2. Count competitions per category
SELECT
    cat.category_name,
    COUNT(c.competition_id) AS competition_count
FROM Categories AS cat
LEFT JOIN Competitions AS c
    ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY competition_count DESC;

-- 3. Find doubles competitions
SELECT
    competition_id,
    competition_name,
    type,
    gender,
    category_id
FROM Competitions
WHERE LOWER(type) = 'doubles'
ORDER BY competition_name;

-- 4. Find competitions in a specific category (ITF Men example)
SELECT
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    cat.category_name
FROM Competitions AS c
JOIN Categories AS cat
    ON c.category_id = cat.category_id
WHERE LOWER(cat.category_name) = LOWER('ITF Men')
ORDER BY c.competition_name;

-- 5. List parent competitions and their sub-competitions
SELECT
    parent.competition_id AS parent_id,
    parent.competition_name AS parent_competition,
    child.competition_id AS child_id,
    child.competition_name AS sub_competition
FROM Competitions AS parent
JOIN Competitions AS child
    ON child.parent_id = parent.competition_id
ORDER BY parent.competition_name, child.competition_name;

-- 6. Distribution of competition types by category
SELECT
    cat.category_name,
    c.type,
    COUNT(*) AS competition_count
FROM Competitions AS c
JOIN Categories AS cat
    ON c.category_id = cat.category_id
GROUP BY cat.category_id, cat.category_name, c.type
ORDER BY cat.category_name, competition_count DESC;

-- 7. Competitions without a parent
SELECT
    competition_id,
    competition_name,
    type,
    gender,
    category_id
FROM Competitions
WHERE parent_id IS NULL
ORDER BY competition_name;
