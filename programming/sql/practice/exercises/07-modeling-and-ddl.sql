-- 07 — Designing tables and changing data
-- db: a scratch copy — run with:  sqlite3 :memory: < exercises/07-modeling-and-ddl.sql

.read data/clubdata.sql
PRAGMA foreign_keys = ON;

-- Q1. Create facility_price_history(facid, valid_from, membercost, guestcost) with a
--     composite primary key, a FK to facilities, and checks: costs >= 0, guest >= member.

-- Q2. Seed it with every facility's current prices, valid from 2012-07-01.

-- Q3. Add a new facility: facid 9, 'Spa', membercost 20, guestcost 30, outlay 100000, maintenance 800.

-- Q4. Upsert: set the Spa's prices to 25 / 35 whether or not it already exists.

-- Q5. Raise Tennis Court 2's prices to 10% above Tennis Court 1's, in one UPDATE.

-- Q6. Delete member 37 and their bookings, atomically.

-- Q7. Create a view member_usage(memid, bookings, slots).
