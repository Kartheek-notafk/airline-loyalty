-- ============================================================
-- ANALYTICAL VIEWS
-- ============================================================

-- 1. Revenue by Route (Top earning routes)
CREATE OR REPLACE VIEW vw_route_revenue AS
SELECT
    r.RouteID,
    r.Source,
    r.Destination,
    r.Region,
    r.RouteType,
    COUNT(f.FlightID)               AS TotalFlights,
    SUM(f.Revenue)                  AS TotalRevenue,
    ROUND(AVG(f.Revenue)::NUMERIC, 2) AS AvgRevenuePerFlight,
    SUM(f.SeatsBooked)              AS TotalPassengers,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancyRate
FROM Fact_Flight_Booking f
JOIN Dimension_Route r ON f.RouteID = r.RouteID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.RouteID, r.Source, r.Destination, r.Region, r.RouteType
ORDER BY TotalRevenue DESC;

-- 2. Revenue by Season
CREATE OR REPLACE VIEW vw_seasonal_revenue AS
SELECT
    d.Year,
    d.Season,
    COUNT(f.FlightID)                     AS TotalFlights,
    SUM(f.Revenue)                        AS TotalRevenue,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancyRate,
    SUM(f.SeatsBooked)                    AS TotalPassengers
FROM Fact_Flight_Booking f
JOIN Dimension_Date d ON f.DateID = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY d.Year, d.Season
ORDER BY d.Year, TotalRevenue DESC;

-- 3. Monthly Revenue Trend
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    d.Year,
    d.Month,
    TO_CHAR(d.FullDate, 'Mon YYYY') AS MonthLabel,
    SUM(f.Revenue)                  AS TotalRevenue,
    COUNT(f.FlightID)               AS TotalFlights,
    SUM(f.SeatsBooked)              AS TotalPassengers,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2) AS AvgOccupancy
FROM Fact_Flight_Booking f
JOIN Dimension_Date d ON f.DateID = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY d.Year, d.Month, d.FullDate
ORDER BY d.Year, d.Month;

-- 4. Occupancy Analysis (Underbooked flights)
CREATE OR REPLACE VIEW vw_occupancy_analysis AS
SELECT
    r.Source || ' → ' || r.Destination AS Route,
    r.Region,
    d.Season,
    COUNT(f.FlightID)                      AS TotalFlights,
    ROUND(AVG(f.OccupancyRate)::NUMERIC,2) AS AvgOccupancy,
    SUM(CASE WHEN f.OccupancyRate < 50 THEN 1 ELSE 0 END) AS UnderbookedFlights,
    SUM(CASE WHEN f.OccupancyRate > 90 THEN 1 ELSE 0 END) AS OverbookedFlights,
    ROUND(
        (SUM(CASE WHEN f.OccupancyRate < 50 THEN 1 ELSE 0 END)::FLOAT
         / NULLIF(COUNT(f.FlightID), 0) * 100)::NUMERIC, 2
    ) AS UnderbookedPct
FROM Fact_Flight_Booking f
JOIN Dimension_Route r ON f.RouteID = r.RouteID
JOIN Dimension_Date  d ON f.DateID  = d.DateID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.Source, r.Destination, r.Region, d.Season
ORDER BY UnderbookedPct DESC;

-- 5. Customer Segmentation
CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT
    c.LoyaltyTier,
    c.AgeGroup,
    c.TravelPurpose,
    COUNT(DISTINCT f.CustomerID)               AS UniquePassengers,
    COUNT(f.FlightID)                          AS TotalFlights,
    SUM(f.Revenue)                             AS TotalRevenue,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2)      AS AvgTicketPrice,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2)    AS AvgOccupancy
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY c.LoyaltyTier, c.AgeGroup, c.TravelPurpose
ORDER BY TotalRevenue DESC;

-- 6. Aircraft Performance
CREATE OR REPLACE VIEW vw_aircraft_performance AS
SELECT
    a.AircraftType,
    a.Manufacturer,
    a.Capacity,
    COUNT(f.FlightID)                          AS TotalFlights,
    ROUND(AVG(f.OccupancyRate)::NUMERIC, 2)    AS AvgOccupancy,
    SUM(f.Revenue)                             AS TotalRevenue,
    ROUND(AVG(f.Revenue)::NUMERIC, 2)          AS AvgRevenuePerFlight,
    SUM(CASE WHEN f.FlightStatus = 'Delayed'   THEN 1 ELSE 0 END) AS DelayedFlights,
    SUM(CASE WHEN f.FlightStatus = 'Cancelled' THEN 1 ELSE 0 END) AS CancelledFlights
FROM Fact_Flight_Booking f
JOIN Dimension_Aircraft a ON f.AircraftID = a.AircraftID
GROUP BY a.AircraftType, a.Manufacturer, a.Capacity
ORDER BY TotalRevenue DESC;

-- 7. Loyalty Revenue Contribution
CREATE OR REPLACE VIEW vw_loyalty_revenue AS
SELECT
    c.LoyaltyTier,
    COUNT(DISTINCT f.CustomerID)                   AS Customers,
    SUM(f.Revenue)                                 AS TotalRevenue,
    ROUND(SUM(f.Revenue) * 100.0 /
          SUM(SUM(f.Revenue)) OVER ()::NUMERIC, 2) AS RevenuePct,
    ROUND(AVG(f.TicketPrice)::NUMERIC, 2)          AS AvgTicket
FROM Fact_Flight_Booking f
JOIN Dimension_Customer c ON f.CustomerID = c.CustomerID
WHERE f.FlightStatus = 'Completed'
GROUP BY c.LoyaltyTier
ORDER BY TotalRevenue DESC;