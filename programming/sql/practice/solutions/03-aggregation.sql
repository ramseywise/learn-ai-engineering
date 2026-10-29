-- 03 — Aggregation
-- db: survey.db, then clubdata.db from Q3 on

-- Q1. For each person and quantity, the number of readings and their mean (2 d.p.).
SELECT person, quant, count(*) AS n, round(avg(reading), 2) AS mean
FROM Survey WHERE person IS NOT NULL
GROUP BY person, quant ORDER BY person, quant;

-- Q2. Which people took more than 3 readings in total?
SELECT person, count(*) AS n FROM Survey GROUP BY person HAVING count(*) > 3;

.open data/clubdata.db

-- Q3. Total slots booked per facility, highest first.
SELECT facid, sum(slots) AS total_slots FROM bookings GROUP BY facid ORDER BY total_slots DESC;

-- Q4. Facilities with more than 1000 slots booked.
SELECT facid, sum(slots) AS total_slots FROM bookings GROUP BY facid HAVING sum(slots) > 1000 ORDER BY facid;

-- Q5. Number of members recommended by each recommender (ignore members with no recommender).
SELECT recommendedby, count(*) AS n FROM members
WHERE recommendedby IS NOT NULL GROUP BY recommendedby ORDER BY recommendedby;

-- Q6. Slots per facility per month in 2012, one row per (facility, month).
SELECT facid, strftime('%m', starttime) AS month, sum(slots) AS slots
FROM bookings WHERE starttime >= '2012-01-01' AND starttime < '2013-01-01'
GROUP BY facid, month ORDER BY facid, month;

-- Q7. Pivot: one row per facility, columns jul / aug / sep with slots booked that month.
SELECT facid,
       sum(CASE WHEN strftime('%m', starttime) = '07' THEN slots ELSE 0 END) AS jul,
       sum(CASE WHEN strftime('%m', starttime) = '08' THEN slots ELSE 0 END) AS aug,
       sum(CASE WHEN strftime('%m', starttime) = '09' THEN slots ELSE 0 END) AS sep
FROM bookings WHERE starttime >= '2012-07-01' AND starttime < '2012-10-01'
GROUP BY facid ORDER BY facid;

-- Q8. Revenue per facility. A slot costs membercost for members and guestcost for the
--     GUEST account (memid 0). Show facilities with revenue under 1000.
SELECT f.name,
       sum(b.slots * CASE WHEN b.memid = 0 THEN f.guestcost ELSE f.membercost END) AS revenue
FROM bookings b JOIN facilities f ON f.facid = b.facid
GROUP BY f.name
HAVING revenue < 1000
ORDER BY revenue;
