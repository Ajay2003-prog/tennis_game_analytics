-- MEMBER 2: TENNIS COMPLEXES AND VENUES ANALYSIS
-- Database: data/tennis_venues.db

-- 1. List all venues along with their associated complex name
SELECT
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    c.complex_name
FROM Venues AS v
JOIN Complexes AS c
    ON v.complex_id = c.complex_id
ORDER BY c.complex_name, v.venue_name;

-- 2. Count the number of venues in each complex
SELECT
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS venue_count
FROM Complexes AS c
LEFT JOIN Venues AS v
    ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
ORDER BY venue_count DESC, c.complex_name;

-- 3. Get details of venues in a specific country (Chile example)
SELECT
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_name
FROM Venues AS v
JOIN Complexes AS c
    ON v.complex_id = c.complex_id
WHERE LOWER(v.country_name) = LOWER('Chile')
ORDER BY v.city_name, v.venue_name;

-- 4. Identify all venues and their timezones
SELECT
    venue_id,
    venue_name,
    city_name,
    country_name,
    timezone
FROM Venues
ORDER BY timezone, venue_name;

-- 5. Find complexes that have more than one venue
SELECT
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS venue_count
FROM Complexes AS c
JOIN Venues AS v
    ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY venue_count DESC, c.complex_name;

-- 6. List venues grouped by country
SELECT
    country_name,
    COUNT(*) AS venue_count,
    GROUP_CONCAT(venue_name, ' | ') AS venues
FROM Venues
GROUP BY country_name
ORDER BY venue_count DESC, country_name;

-- 7. Find all venues for a specific complex (Nacional example)
SELECT
    c.complex_name,
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name
FROM Complexes AS c
JOIN Venues AS v
    ON c.complex_id = v.complex_id
WHERE LOWER(c.complex_name) = LOWER('Nacional')
ORDER BY c.complex_name, v.venue_name;
