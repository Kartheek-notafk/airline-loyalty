-- ============================================================
-- OCCUPANCY ANALYSIS
-- ============================================================

-- 1. Overall Occupancy Health
SELECT
    CASE
        WHEN OccupancyRate >= 90 THEN 'Overbooked (≥90%)'
        WHEN OccupancyRate >= 70 THEN 'Healthy (70–90%)'
        WHEN OccupancyRate >= 50 THEN 'Moderate (50–70%)'
        ELSE                          'Underbooked (<50%)'
    END AS OccupancyBucket,
    COUNT(*) AS FlightCount,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()::NUMERIC, 2) AS Pct
FROM Fact_Flight_Booking
WHERE FlightStatus = 'Completed'
GROUP BY OccupancyBucket
ORDER BY FlightCount DESC;

-- 2. Consistently Underbooked Routes
SELECT
    r.Source || ' → ' || r.Destination AS Route,
    COUNT(f.FlightID)                  AS TotalFlights,
    SUM(CASE WHEN f.OccupancyRate < 50 THEN 1 ELSE 0 END) AS UnderbookedCount,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2)               AS AvgOccupancy,
    ROUND(
        SUM(CASE WHEN f.OccupancyRate < 50 THEN 1 ELSE 0 END) * 100.0
        / COUNT(f.FlightID)::NUMERIC, 2
    ) AS UnderbookedPct
FROM Fact_Flight_Booking f
JOIN Dimension_Route r ON f.RouteID = r.RouteID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.Source, r.Destination
HAVING COUNT(f.FlightID) > 10
ORDER BY UnderbookedPct DESC
LIMIT 10;

-- 3. Occupancy by Day of Week
SELECT
    d.DayOfWeek,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancy,
    COUNT(f.FlightID)                        AS Flights
FROM Fact_Flight_Booking f
JOIN Dimension_Date d ON f.DateID = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY d.DayOfWeek
ORDER BY AvgOccupancy DESC;