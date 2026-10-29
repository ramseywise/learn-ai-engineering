-- 02 — Missing data, dates and strings
-- db: survey.db, then clubdata.db from Q4 on

-- Q1. Which visits have no recorded date?
SELECT * FROM Visited WHERE dated IS NULL;

-- Q2. Every survey row not taken by 'lake' — including rows with no person recorded.
SELECT * FROM Survey WHERE person != 'lake' OR person IS NULL;

-- Q3. Show each visit with its date, or 'unknown' when missing.
SELECT id, site, COALESCE(dated, 'unknown') AS dated FROM Visited;

.open data/clubdata.db

-- Q4. Bookings that started in September 2012 (use a half-open range). How many?
SELECT count(*) FROM bookings WHERE starttime >= '2012-09-01' AND starttime < '2012-10-01';

-- Q5. Members' telephone numbers with every non-digit removed (handle '(', ')', ' ', '-').
SELECT memid, replace(replace(replace(replace(telephone, '(', ''), ')', ''), ' ', ''), '-', '') AS digits
FROM members ORDER BY memid;

-- Q6. For each member, how many days after the club opened (2012-07-01) did they join?
--     Round to whole days.
SELECT memid, surname, CAST(round(julianday(joindate) - julianday('2012-07-01')) AS INTEGER) AS days_in
FROM members ORDER BY days_in;

-- Q7. Booking start hours: how many bookings start at each hour of the day?
SELECT CAST(strftime('%H', starttime) AS INTEGER) AS hour, count(*) AS n
FROM bookings GROUP BY hour ORDER BY hour;

-- Q8. Members whose surname contains 'o' (any case), as "Surname, Firstname".
SELECT surname || ', ' || firstname AS name FROM members WHERE lower(surname) LIKE '%o%';
