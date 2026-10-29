-- 04 — Joins
-- db: survey.db, then clubdata.db from Q3 on

-- Q1. Every dated radiation reading with its site's latitude and longitude.
SELECT s.lat, s.long, v.dated, sv.reading
FROM Site s
JOIN Visited v  ON v.site = s.name
JOIN Survey  sv ON sv.taken = v.id
WHERE sv.quant = 'rad' AND v.dated IS NOT NULL
ORDER BY v.dated;

-- Q2. Full names of everyone who measured at site DR-3 (no duplicates).
SELECT DISTINCT p.personal || ' ' || p.family AS name
FROM Person p
JOIN Survey sv ON sv.person = p.id
JOIN Visited v ON v.id = sv.taken
WHERE v.site = 'DR-3';

.open data/clubdata.db

-- Q3. Start times of bookings by members named 'David Farrell'.
SELECT b.starttime
FROM bookings b JOIN members m ON m.memid = b.memid
WHERE m.firstname = 'David' AND m.surname = 'Farrell'
ORDER BY b.starttime;

-- Q4. Every member with the name of who recommended them (NULL if nobody).
SELECT m.firstname, m.surname, r.firstname AS rec_first, r.surname AS rec_last
FROM members m LEFT JOIN members r ON r.memid = m.recommendedby
ORDER BY m.surname, m.firstname;

-- Q5. Members who have recommended at least one other member (no duplicates).
SELECT DISTINCT r.firstname, r.surname
FROM members m JOIN members r ON r.memid = m.recommendedby
ORDER BY r.surname, r.firstname;

-- Q6. Every facility with its number of bookings in September 2012 — including zeros.
SELECT f.name, count(b.bookid) AS n
FROM facilities f
LEFT JOIN bookings b
  ON b.facid = f.facid AND b.starttime >= '2012-09-01' AND b.starttime < '2012-10-01'
GROUP BY f.name ORDER BY f.name;

-- Q7. Members who have never made a booking (anti-join).
SELECT m.memid, m.firstname, m.surname
FROM members m LEFT JOIN bookings b ON b.memid = m.memid
WHERE b.memid IS NULL;

-- Q8. A combined list of all surnames and facility names (UNION).
SELECT surname AS label FROM members UNION SELECT name FROM facilities ORDER BY label;
