-- Top-ranked competitors in every ranking snapshot.
SELECT
    s.ranking_name,
    s.gender,
    r.rank,
    c.competitor_name,
    r.points,
    r.movement
FROM DoublesRankings AS r
JOIN RankingSnapshots AS s
  ON s.ranking_snapshot_id = r.ranking_snapshot_id
JOIN Competitors AS c
  ON c.competitor_id = r.competitor_id
WHERE r.rank <= 10
ORDER BY s.gender, r.rank;

-- Ranking size and points by snapshot.
SELECT
    s.ranking_name,
    s.gender,
    s.year,
    s.week,
    COUNT(*) AS competitor_count,
    MAX(r.points) AS highest_points,
    MIN(r.points) AS lowest_points
FROM RankingSnapshots AS s
JOIN DoublesRankings AS r
  ON r.ranking_snapshot_id = s.ranking_snapshot_id
GROUP BY s.ranking_snapshot_id
ORDER BY s.gender;

-- Competitors appearing in more than one ranking snapshot.
SELECT
    c.competitor_name,
    c.country,
    COUNT(DISTINCT r.ranking_snapshot_id) AS snapshot_count,
    MIN(r.rank) AS best_rank
FROM Competitors AS c
JOIN DoublesRankings AS r
  ON r.competitor_id = c.competitor_id
GROUP BY c.competitor_id
HAVING COUNT(DISTINCT r.ranking_snapshot_id) > 1
ORDER BY snapshot_count DESC, best_rank;

-- Countries represented in the ranking data.
SELECT
    c.country,
    c.country_code,
    COUNT(DISTINCT c.competitor_id) AS competitor_count
FROM Competitors AS c
JOIN DoublesRankings AS r
  ON r.competitor_id = c.competitor_id
GROUP BY c.country, c.country_code
ORDER BY competitor_count DESC, c.country;
