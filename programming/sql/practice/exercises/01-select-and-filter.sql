-- 01 — Selecting, sorting and filtering
-- db: survey.db, then clubdata.db from Q6 on
-- Run: sqlite3 -header -column data/survey.db < exercises/01-select-and-filter.sql

-- Q1. List every scientist's family name and personal name, sorted by family name.

-- Q2. Which distinct quantities (quant) were measured? Sort them alphabetically.

-- Q3. Show all visits to sites whose name starts with 'DR', newest first.

-- Q4. Salinity readings ('sal') above 1.0 are almost certainly recorded as a percentage.
--     Return taken, person and the reading divided by 100, as `sal_fraction`.

-- Q5. Readings by Lake or Roerich that are salinity. Mind the AND/OR precedence.

.open data/clubdata.db
-- Q6. Facilities that charge members a fee, with the fee, cheapest first.

-- Q7. Facilities whose member cost is less than 1/50th of the monthly maintenance (but > 0).

-- Q8. Label each facility 'cheap' if monthlymaintenance < 100, else 'expensive'.

-- Q9. The 5 most recently joined members (excluding the GUEST account, memid 0).
