-- 06 — Window functions
-- db: clubdata.db

.open data/clubdata.db

-- Q1. Each booking alongside its member's total slots.

-- Q2. Rank facilities by total slots (rank(), so ties share a rank).

-- Q3. Top 3 longest bookings per member (deterministic tie-break on bookid).

-- Q4. Daily slots in August 2012 with a running total.

-- Q5. 7-day moving average of daily slots in August 2012.

-- Q6. Days between each of member 1's consecutive bookings (lag).

-- Q7. Each facility's share of all slots, in percent.

-- Q8. Split members (excluding GUEST) into 3 usage tiers by total slots with ntile.

-- Q9. Each member's latest booking only (dedup pattern).
