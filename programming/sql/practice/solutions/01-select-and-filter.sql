-- 01 — Selecting, sorting and filtering
-- db: survey.db, then clubdata.db from Q6 on
-- Run: sqlite3 -header -column data/survey.db < solutions/01-select-and-filter.sql

-- Q1. List every scientist's family name and personal name, sorted by family name.
SELECT family, personal FROM Person ORDER BY family;

-- Q2. Which distinct quantities (quant) were measured? Sort them alphabetically.
SELECT DISTINCT quant FROM Survey ORDER BY quant;

-- Q3. Show all visits to sites whose name starts with 'DR', newest first.
SELECT * FROM Visited WHERE site LIKE 'DR%' ORDER BY dated DESC;

-- Q4. Salinity readings ('sal') above 1.0 are almost certainly recorded as a percentage.
--     Return taken, person and the reading divided by 100, as `sal_fraction`.
SELECT taken, person, reading / 100.0 AS sal_fraction
FROM Survey WHERE quant = 'sal' AND reading > 1.0;

-- Q5. Readings by Lake or Roerich that are salinity. Mind the AND/OR precedence.
SELECT * FROM Survey WHERE quant = 'sal' AND person IN ('lake', 'roe');

.open data/clubdata.db

-- Q6. Facilities that charge members a fee, with the fee, cheapest first.
SELECT name, membercost FROM facilities WHERE membercost > 0 ORDER BY membercost, name;

-- Q7. Facilities whose member cost is less than 1/50th of the monthly maintenance (but > 0).
SELECT facid, name, membercost, monthlymaintenance
FROM facilities
WHERE membercost > 0 AND membercost < monthlymaintenance / 50.0;

-- Q8. Label each facility 'cheap' if monthlymaintenance < 100, else 'expensive'.
SELECT name, CASE WHEN monthlymaintenance < 100 THEN 'cheap' ELSE 'expensive' END AS cost
FROM facilities;

-- Q9. The 5 most recently joined members (excluding the GUEST account, memid 0).
SELECT memid, firstname, surname, joindate
FROM members WHERE memid > 0 ORDER BY joindate DESC LIMIT 5;
