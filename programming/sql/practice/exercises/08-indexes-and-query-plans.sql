-- 08 — Indexes and query plans
-- db: clubdata.db (built by setup.sh, includes the PGExercises indexes)

.open data/clubdata.db

-- Q1. Show the plan for member 5's bookings since September. Which index is used?

-- Q2. Show the plan when filtering with date(starttime) = '2012-09-14'. Why does it change?

-- Q3. Rewrite Q2 so it is sargable and check the plan again.

-- Q4. Find a query on members that does a full SCAN, add an index that turns it into a
--     SEARCH, then drop the index again.

-- Q5. A covering index: count bookings per facility for one member without touching the table.
