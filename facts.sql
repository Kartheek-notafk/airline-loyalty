-- ============================================================
-- FACT TABLE SEED DATA (Synthetic Flight Bookings)
-- ============================================================

INSERT INTO Fact_Flight_Booking (
    RouteID, CustomerID, DateID, AircraftID,
    Revenue, TicketPrice, SeatsBooked, AvailableSeats,
    BookingClass, FlightStatus, AncillaryRevenue
)
SELECT
    (random() * 14 + 1)::INT,
    (random() * 4999 + 1)::INT,
    (random() * 1095 + 1)::INT,
    (random() * 9 + 1)::INT,

    -- Revenue: base * seats with seasonal multiplier
    ROUND((
        CASE (random() * 2)::INT
            WHEN 0 THEN (150 + random() * 300)    -- Economy
            WHEN 1 THEN (500 + random() * 1000)   -- Business
            ELSE        (1200 + random() * 2000)  -- First
        END * (0.9 + random() * 0.4)             -- demand fluctuation
    )::NUMERIC, 2),

    -- Ticket price
    ROUND((150 + random() * 1800)::NUMERIC, 2),

    -- Seats booked (varies by load factor realism)
    (50 + (random() * 150))::INT,

    -- Available seats
    (ARRAY[76, 180, 189, 200, 220, 269, 296, 369, 396, 555])[(random()*9 + 1)::INT],

    -- Booking class
    (ARRAY['Economy', 'Business', 'First'])[(random()*2 + 1)::INT],

    -- Flight status (mostly completed)
    CASE WHEN random() < 0.85 THEN 'Completed'
         WHEN random() < 0.92 THEN 'Delayed'
         ELSE 'Cancelled' END,

    -- Ancillary revenue (baggage, meals, etc.)
    ROUND((random() * 80)::NUMERIC, 2)

FROM generate_series(1, 50000);