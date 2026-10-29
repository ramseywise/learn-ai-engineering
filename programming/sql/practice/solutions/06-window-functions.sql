-- 06 — Window functions
-- db: clubdata.db

.open data/clubdata.db

-- Q1. Each booking alongside its member's total slots.
SELECT bookid, memid, slots, sum(slots) OVER (PARTITION BY memid) AS member_total
FROM bookings ORDER BY memid, bookid LIMIT 20;

-- Q2. Rank facilities by total slots (rank(), so ties share a rank).
SELECT facid, sum(slots) AS total, rank() OVER (ORDER BY sum(slots) DESC) AS rnk
FROM bookings GROUP BY facid ORDER BY rnk;

-- Q3. Top 3 longest bookings per member (deterministic tie-break on bookid).
WITH ranked AS (
  SELECT memid, bookid, slots,
         row_number() OVER (PARTITION BY memid ORDER BY slots DESC, bookid) AS rn
  FROM bookings
)
SELECT * FROM ranked WHERE rn <= 3 ORDER BY memid, rn;

-- Q4. Daily slots in August 2012 with a running total.
SELECT date(starttime) AS day, sum(slots) AS slots,
       sum(sum(slots)) OVER (ORDER BY date(starttime)) AS running_total
FROM bookings WHERE starttime >= '2012-08-01' AND starttime < '2012-09-01'
GROUP BY day ORDER BY day;

-- Q5. 7-day moving average of daily slots in August 2012.
SELECT date(starttime) AS day, sum(slots) AS slots,
       round(avg(sum(slots)) OVER (ORDER BY date(starttime) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS ma7
FROM bookings WHERE starttime >= '2012-08-01' AND starttime < '2012-09-01'
GROUP BY day ORDER BY day;

-- Q6. Days between each of member 1's consecutive bookings (lag).
SELECT starttime,
       round(julianday(starttime) - julianday(lag(starttime) OVER (ORDER BY starttime)), 2) AS days_since_prev
FROM bookings WHERE memid = 1 ORDER BY starttime LIMIT 15;

-- Q7. Each facility's share of all slots, in percent.
SELECT facid, sum(slots) AS slots,
       round(100.0 * sum(slots) / sum(sum(slots)) OVER (), 1) AS pct_of_all
FROM bookings GROUP BY facid ORDER BY pct_of_all DESC;

-- Q8. Split members (excluding GUEST) into 3 usage tiers by total slots with ntile.
SELECT m.surname, m.firstname, t.slots,
       CASE ntile(3) OVER (ORDER BY t.slots DESC) WHEN 1 THEN 'high' WHEN 2 THEN 'average' ELSE 'low' END AS tier
FROM (SELECT memid, sum(slots) AS slots FROM bookings WHERE memid > 0 GROUP BY memid) t
JOIN members m USING (memid) ORDER BY t.slots DESC;

-- Q9. Each member's latest booking only (dedup pattern).
WITH latest AS (
  SELECT memid, bookid, starttime,
         row_number() OVER (PARTITION BY memid ORDER BY starttime DESC, bookid DESC) AS rn
  FROM bookings
)
SELECT memid, bookid, starttime FROM latest WHERE rn = 1 ORDER BY memid;
