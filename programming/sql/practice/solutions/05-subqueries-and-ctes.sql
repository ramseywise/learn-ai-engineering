-- 05 — Subqueries and CTEs
-- db: clubdata.db

.open data/clubdata.db

-- Q1. Bookings with more slots than the average booking.
SELECT bookid, facid, slots FROM bookings WHERE slots > (SELECT avg(slots) FROM bookings) ORDER BY bookid LIMIT 20;

-- Q2. Each member's first booking time (correlated subquery).
SELECT m.memid, m.surname,
       (SELECT min(b.starttime) FROM bookings b WHERE b.memid = m.memid) AS first_booking
FROM members m ORDER BY m.memid;

-- Q3. Members who have used a tennis court (EXISTS).
SELECT m.firstname, m.surname FROM members m
WHERE EXISTS (
  SELECT 1 FROM bookings b JOIN facilities f ON f.facid = b.facid
  WHERE b.memid = m.memid AND f.name LIKE 'Tennis Court%'
)
ORDER BY m.surname, m.firstname;

-- Q4. Members who have never used a tennis court (NOT EXISTS).
SELECT m.firstname, m.surname FROM members m
WHERE NOT EXISTS (
  SELECT 1 FROM bookings b JOIN facilities f ON f.facid = b.facid
  WHERE b.memid = m.memid AND f.name LIKE 'Tennis Court%'
)
ORDER BY m.surname, m.firstname;

-- Q5. With a CTE: the facility (or facilities) with the most slots booked.
WITH totals AS (SELECT facid, sum(slots) AS slots FROM bookings GROUP BY facid)
SELECT f.name, t.slots
FROM totals t JOIN facilities f USING (facid)
WHERE t.slots = (SELECT max(slots) FROM totals);

-- Q6. Top 5 members by share of all member slots (exclude GUEST), with % to 1 d.p.
WITH member_slots AS (
  SELECT memid, sum(slots) AS slots FROM bookings WHERE memid > 0 GROUP BY memid
)
SELECT m.surname, m.firstname, s.slots,
       round(100.0 * s.slots / (SELECT sum(slots) FROM member_slots), 1) AS pct
FROM member_slots s JOIN members m USING (memid)
ORDER BY s.slots DESC LIMIT 5;

-- Q7. Recursive: the chain of recommenders above member 27, nearest first.
WITH RECURSIVE chain(memid, recommendedby, depth) AS (
  SELECT memid, recommendedby, 0 FROM members WHERE memid = 27
  UNION ALL
  SELECT m.memid, m.recommendedby, c.depth + 1
  FROM members m JOIN chain c ON m.memid = c.recommendedby
)
SELECT c.depth, m.firstname, m.surname
FROM chain c JOIN members m USING (memid)
WHERE c.depth > 0 ORDER BY c.depth;

-- Q8. Recursive: every member recommended directly or indirectly by member 1.
WITH RECURSIVE downline(memid, depth) AS (
  SELECT memid, 1 FROM members WHERE recommendedby = 1
  UNION ALL
  SELECT m.memid, d.depth + 1 FROM members m JOIN downline d ON m.recommendedby = d.memid
)
SELECT d.depth, m.memid, m.firstname, m.surname
FROM downline d JOIN members m USING (memid) ORDER BY d.depth, m.memid;

-- Q9. Bookings per day for every day of September 2012, zeros included (date series).
WITH RECURSIVE days(d) AS (
  SELECT '2012-09-01' UNION ALL SELECT date(d, '+1 day') FROM days WHERE d < '2012-09-30'
)
SELECT d, count(b.bookid) AS bookings
FROM days LEFT JOIN bookings b ON b.starttime >= d AND b.starttime < date(d, '+1 day')
GROUP BY d ORDER BY d;
