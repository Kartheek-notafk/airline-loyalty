-- ============================================================
-- REVENUE ANALYSIS QUERIES
-- ============================================================

-- 1. Top 10 Earning Routes
SELECT
    r.Source || ' → ' || r.Destination AS Route,
    r.Region,
    r.RouteType,
    COUNT(f.FlightID)               AS TotalFlights,
    SUM(f.Revenue)                  AS TotalRevenue,
    ROUND(AVG(f.Revenue)::NUMERIC, 2) AS AvgRevPerFlight,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancy
FROM Fact_Flight_Booking f
JOIN Dimension_Route r ON f.RouteID = r.RouteID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.Source, r.Destination, r.Region, r.RouteType
ORDER BY TotalRevenue DESC
LIMIT 10;

-- 2. Revenue by Season (all years)
SELECT
    d.Season,
    SUM(f.Revenue)                  AS TotalRevenue,
    COUNT(f.FlightID)               AS TotalFlights,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancy
FROM Fact_Flight_Booking f
JOIN Dimension_Date d ON f.DateID = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY d.Season
ORDER BY TotalRevenue DESC;

-- 3. Revenue by Region
SELECT
    r.Region,
    SUM(f.Revenue)                  AS TotalRevenue,
    COUNT(f.FlightID)               AS Flights,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2) AS AvgTicket,
    ROUND(SUM(f.Revenue) * 100.0 / SUM(SUM(f.Revenue)) OVER ()::NUMERIC, 2) AS RevenuePct
FROM Fact_Flight_Booking f
JOIN Dimension_Route r ON f.RouteID = r.RouteID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.Region
ORDER BY TotalRevenue DESC;

-- 4. Year-over-Year Revenue Growth
SELECT
    d.Year,
    SUM(f.Revenue) AS TotalRevenue,
    LAG(SUM(f.Revenue)) OVER (ORDER BY d.Year) AS PrevYearRevenue,
    ROUND(
        (SUM(f.Revenue) - LAG(SUM(f.Revenue)) OVER (ORDER BY d.Year))
        / NULLIF(LAG(SUM(f.Revenue)) OVER (ORDER BY d.Year), 0) * 100
    ::NUMERIC, 2) AS GrowthPct
FROM Fact_Flight_Booking f
JOIN Dimension_Date d ON f.DateID = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY d.Year
ORDER BY d.Year;

-- 5. Revenue by Booking Class
SELECT
    f.BookingClass,
    COUNT(f.FlightID)                 AS Bookings,
    SUM(f.Revenue)                    AS TotalRevenue,
    ROUND(AVG(f.TicketPrice)::NUMERIC,2) AS AvgTicket,
    ROUND(SUM(f.Revenue)*100.0/SUM(SUM(f.Revenue)) OVER ()::NUMERIC,2) AS RevSharePct
FROM Fact_Flight_Booking f
WHERE f.FlightStatus = 'Completed'
GROUP BY f.BookingClass
ORDER BY TotalRevenue DESC;