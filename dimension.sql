-- ============================================================
-- DIMENSION SEED DATA
-- ============================================================

-- Routes
INSERT INTO Dimension_Route (Source, Destination, Distance, Region, RouteType, FlightDuration) VALUES
('New York',    'Los Angeles',  2451, 'North America', 'Domestic',      5.5),
('New York',    'London',       3459, 'Transatlantic', 'International', 7.0),
('Chicago',     'Miami',        1197, 'North America', 'Domestic',      3.0),
('Los Angeles', 'Tokyo',        5478, 'Trans-Pacific', 'International', 11.5),
('Dallas',      'Seattle',      1660, 'North America', 'Domestic',      4.0),
('Miami',       'Bogota',       1154, 'Latin America', 'International', 3.5),
('San Francisco','Singapore',   8446, 'Trans-Pacific', 'International', 17.0),
('Boston',      'Paris',        3448, 'Transatlantic', 'International', 7.2),
('Houston',     'Cancun',        935, 'Latin America', 'International', 2.5),
('Atlanta',     'London',       4281, 'Transatlantic', 'International', 8.5),
('Denver',      'Chicago',       920, 'North America', 'Domestic',      2.2),
('Phoenix',     'New York',     2145, 'North America', 'Domestic',      4.8),
('Seattle',     'Anchorage',    1448, 'North America', 'Domestic',      3.3),
('Las Vegas',   'Orlando',      2038, 'North America', 'Domestic',      4.5),
('Minneapolis', 'Dallas',       1118, 'North America', 'Domestic',      2.8);

-- Aircraft
INSERT INTO Dimension_Aircraft (AircraftType, Capacity, Manufacturer, AgeYears, ClassConfig) VALUES
('Boeing 737-800',      189, 'Boeing',   8, 'Economy/Business'),
('Airbus A320',         180, 'Airbus',   5, 'Economy/Business'),
('Boeing 777-300ER',    396, 'Boeing',  12, 'Economy/Business/First'),
('Airbus A380',         555, 'Airbus',   7, 'Economy/Business/First'),
('Boeing 787-9',        296, 'Boeing',   3, 'Economy/Business/First'),
('Airbus A321neo',      220, 'Airbus',   2, 'Economy/Business'),
('Embraer E175',         76, 'Embraer',  6, 'Economy'),
('Boeing 757-200',      200, 'Boeing',  15, 'Economy/Business'),
('Airbus A350-900',     369, 'Airbus',   4, 'Economy/Business/First'),
('Boeing 767-300',      269, 'Boeing',  18, 'Economy/Business');

-- Generate Date dimension for 3 years (2022-2024)
INSERT INTO Dimension_Date (FullDate, Day, Month, Quarter, Year, Season, IsHoliday, DayOfWeek)
SELECT
    d::DATE,
    EXTRACT(DAY FROM d)::INT,
    EXTRACT(MONTH FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(YEAR FROM d)::INT,
    CASE
        WHEN EXTRACT(MONTH FROM d) IN (12, 1, 2)  THEN 'Winter'
        WHEN EXTRACT(MONTH FROM d) IN (3, 4, 5)   THEN 'Spring'
        WHEN EXTRACT(MONTH FROM d) IN (6, 7, 8)   THEN 'Summer'
        ELSE 'Fall'
    END,
    CASE
        WHEN (EXTRACT(MONTH FROM d) = 12 AND EXTRACT(DAY FROM d) = 25) THEN TRUE
        WHEN (EXTRACT(MONTH FROM d) = 1  AND EXTRACT(DAY FROM d) = 1)  THEN TRUE
        WHEN (EXTRACT(MONTH FROM d) = 7  AND EXTRACT(DAY FROM d) = 4)  THEN TRUE
        WHEN (EXTRACT(MONTH FROM d) = 11 AND EXTRACT(DAY FROM d) IN (23,24,25,26,27)) THEN TRUE
        ELSE FALSE
    END,
    TO_CHAR(d, 'Day')
FROM generate_series('2022-01-01'::DATE, '2024-12-31'::DATE, '1 day') d;

-- Customer dimension (sample demographics)
INSERT INTO Dimension_Customer (AgeGroup, LoyaltyTier, Country, Gender, TravelPurpose)
SELECT
    (ARRAY['18-25','26-35','36-45','46-60','60+'])[floor(random()*5)::INT + 1],
    (ARRAY['Bronze','Silver','Gold','Platinum'])[floor(random()*4)::INT + 1],
    (ARRAY['USA','UK','Canada','Germany','Japan','Australia','France','Brazil','India','Mexico'])[floor(random()*10)::INT + 1],
    (ARRAY['Male','Female','Other'])[floor(random()*3)::INT + 1],
    (ARRAY['Business','Leisure','Family','Other'])[floor(random()*4)::INT + 1]
FROM generate_series(1, 5000);