-- ============================================================
-- AIRLINE LOYALTY PROGRAM DATA WAREHOUSE
-- Schema Definition (Star Schema - Loyalty Centric)
-- ============================================================

-- Drop existing tables in correct order
DROP TABLE IF EXISTS Fact_Customer_Activity CASCADE;
DROP TABLE IF EXISTS Dimension_Customer CASCADE;
DROP TABLE IF EXISTS Dimension_Date CASCADE;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE Dimension_Customer (
    CustomerID         INT PRIMARY KEY, -- Loyalty Number
    Country            VARCHAR(50) NOT NULL,
    Province           VARCHAR(50),
    City               VARCHAR(50),
    PostalCode         VARCHAR(15),
    Gender             VARCHAR(10),
    Education          VARCHAR(50),
    Salary             DECIMAL(12, 2),
    MaritalStatus      VARCHAR(20),
    LoyaltyCard        VARCHAR(20) NOT NULL CHECK (LoyaltyCard IN ('Star', 'Nova', 'Aurora')),
    CLV                DECIMAL(12, 2),
    EnrollmentType     VARCHAR(30),
    EnrollmentYear     INT,
    EnrollmentMonth    INT,
    CancellationYear   INT,
    CancellationMonth  INT
);

CREATE TABLE Dimension_Date (
    DateID    INT PRIMARY KEY, -- YYYYMM format integer
    FullDate  DATE NOT NULL UNIQUE,
    Month     INT NOT NULL,
    Year      INT NOT NULL,
    Quarter   INT NOT NULL,
    Season    VARCHAR(20) CHECK (Season IN ('Spring', 'Summer', 'Fall', 'Winter')),
    IsHoliday BOOLEAN DEFAULT FALSE,
    MonthName VARCHAR(20)
);

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE Fact_Customer_Activity (
    ActivityID               SERIAL PRIMARY KEY,
    CustomerID               INT REFERENCES Dimension_Customer(CustomerID),
    DateID                   INT REFERENCES Dimension_Date(DateID),
    TotalFlights             INT DEFAULT 0,
    Distance                 INT DEFAULT 0,
    PointsAccumulated        FLOAT DEFAULT 0.0,
    PointsRedeemed           INT DEFAULT 0,
    DollarCostPointsRedeemed DECIMAL(10, 2) DEFAULT 0.00
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_activity_customer ON Fact_Customer_Activity(CustomerID);
CREATE INDEX idx_activity_date     ON Fact_Customer_Activity(DateID);
CREATE INDEX idx_customer_tier     ON Dimension_Customer(LoyaltyCard);
CREATE INDEX idx_customer_location ON Dimension_Customer(Province, City);
CREATE INDEX idx_date_year_month   ON Dimension_Date(Year, Month);

COMMENT ON TABLE Fact_Customer_Activity IS 'Central fact table storing monthly customer loyalty activities';
COMMENT ON TABLE Dimension_Customer      IS 'Customer loyalty profiles, demographics, and status';
COMMENT ON TABLE Dimension_Date          IS 'Date dimension corresponding to monthly aggregates';