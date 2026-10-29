-- 08 — Indexes and query plans
-- db: clubdata.db (built by setup.sh, includes the PGExercises indexes)

.open data/clubdata.db

-- Q1. Show the plan for member 5's bookings since September. Which index is used?
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE memid = 5 AND starttime >= '2012-09-01';

-- Q2. Show the plan when filtering with date(starttime) = '2012-09-14'. Why does it change?
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE date(starttime) = '2012-09-14';

-- Q3. Rewrite Q2 so it is sargable and check the plan again.
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE starttime >= '2012-09-14' AND starttime < '2012-09-15';

-- Q4. Find a query on members that does a full SCAN, add an index that turns it into a
--     SEARCH, then drop the index again.
EXPLAIN QUERY PLAN SELECT * FROM members WHERE surname = 'Smith';
CREATE INDEX members_surname ON members (surname);
EXPLAIN QUERY PLAN SELECT * FROM members WHERE surname = 'Smith';
DROP INDEX members_surname;

-- Q5. A covering index: count bookings per facility for one member without touching the table.
EXPLAIN QUERY PLAN
SELECT facid, count(*) FROM bookings WHERE memid = 5 GROUP BY facid;
