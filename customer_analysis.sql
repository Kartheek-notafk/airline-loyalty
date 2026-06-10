-- ============================================================
-- CUSTOMER ANALYTICS
-- ============================================================

-- 1. Top Frequent Travelers (by flight count)
SELECT
    f.CustomerID,
    c.LoyaltyTier,
    c.AgeGroup,
    c.Country,
    COUNT(f.FlightID)             AS TotalFlights,
    SUM(f.Revenue)                AS TotalRevenue,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2) AS AvgTicket
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY f.CustomerID, c.LoyaltyTier, c.AgeGroup, c.Country
ORDER BY TotalFlights DESC
LIMIT 20;

-- 2. Revenue by Loyalty Tier
SELECT
    c.LoyaltyTier,
    COUNT(DISTINCT f.CustomerID)  AS UniqueCustomers,
    COUNT(f.FlightID)             AS TotalFlights,
    SUM(f.Revenue)                AS TotalRevenue,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2) AS AvgTicket,
    ROUND(SUM(f.Revenue) * 100.0 / SUM(SUM(f.Revenue)) OVER ()::NUMERIC, 2) AS RevSharePct
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY c.LoyaltyTier
ORDER BY TotalRevenue DESC;

-- 3. Passenger Segmentation by Age Group & Travel Purpose
SELECT
    c.AgeGroup,
    c.TravelPurpose,
    COUNT(DISTINCT f.CustomerID) AS Passengers,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2) AS AvgTicket,
    SUM(f.Revenue) AS Revenue
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY c.AgeGroup, c.TravelPurpose
ORDER BY Revenue DESC;

-- 4. Country-level Revenue
SELECT
    c.Country,
    COUNT(DISTINCT f.CustomerID) AS Passengers,
    SUM(f.Revenue)               AS TotalRevenue,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2) AS AvgTicket
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY c.Country
ORDER BY TotalRevenue DESC;