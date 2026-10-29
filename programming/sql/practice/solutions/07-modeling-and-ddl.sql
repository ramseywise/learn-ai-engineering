-- 07 — Designing tables and changing data
-- db: a scratch copy — run with:  sqlite3 :memory: < solutions/07-modeling-and-ddl.sql

.read data/clubdata.sql
PRAGMA foreign_keys = ON;

-- Q1. Create facility_price_history(facid, valid_from, membercost, guestcost) with a
--     composite primary key, a FK to facilities, and checks: costs >= 0, guest >= member.
CREATE TABLE facility_price_history (
    facid      INTEGER NOT NULL REFERENCES facilities(facid),
    valid_from DATE    NOT NULL,
    membercost NUMERIC NOT NULL CHECK (membercost >= 0),
    guestcost  NUMERIC NOT NULL CHECK (guestcost >= membercost),
    PRIMARY KEY (facid, valid_from)
);

-- Q2. Seed it with every facility's current prices, valid from 2012-07-01.
INSERT INTO facility_price_history (facid, valid_from, membercost, guestcost)
SELECT facid, '2012-07-01', membercost, guestcost FROM facilities;
SELECT count(*) AS seeded FROM facility_price_history;

-- Q3. Add a new facility: facid 9, 'Spa', membercost 20, guestcost 30, outlay 100000, maintenance 800.
INSERT INTO facilities (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
VALUES (9, 'Spa', 20, 30, 100000, 800);

-- Q4. Upsert: set the Spa's prices to 25 / 35 whether or not it already exists.
INSERT INTO facilities (facid, name, membercost, guestcost, initialoutlay, monthlymaintenance)
VALUES (9, 'Spa', 25, 35, 100000, 800)
ON CONFLICT (facid) DO UPDATE SET membercost = excluded.membercost, guestcost = excluded.guestcost;
SELECT * FROM facilities WHERE facid = 9;

-- Q5. Raise Tennis Court 2's prices to 10% above Tennis Court 1's, in one UPDATE.
UPDATE facilities
SET membercost = (SELECT membercost * 1.1 FROM facilities WHERE facid = 0),
    guestcost  = (SELECT guestcost  * 1.1 FROM facilities WHERE facid = 0)
WHERE facid = 1;
SELECT facid, name, membercost, guestcost FROM facilities WHERE facid IN (0, 1);

-- Q6. Delete member 37 and their bookings, atomically.
BEGIN;
DELETE FROM bookings WHERE memid = 37;
DELETE FROM members  WHERE memid = 37;
COMMIT;
SELECT count(*) AS remaining FROM members WHERE memid = 37;

-- Q7. Create a view member_usage(memid, bookings, slots).
CREATE VIEW member_usage AS
SELECT memid, count(*) AS bookings, sum(slots) AS slots FROM bookings GROUP BY memid;
SELECT * FROM member_usage ORDER BY slots DESC LIMIT 3;
