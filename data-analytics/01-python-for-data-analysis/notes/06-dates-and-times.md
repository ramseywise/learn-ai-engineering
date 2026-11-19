---
origin: synthesis
sources:
  - "McKinney, Python for Data Analysis, 2nd ed. (O'Reilly, 2017), ch. 11; 3rd ed. open access at https://wesmckinney.com/book/time-series"
  - "VanderPlas, Python Data Science Handbook (O'Reilly, 2016), ch. 3; https://jakevdp.github.io/PythonDataScienceHandbook/03.11-working-with-time-series.html"
  - https://pandas.pydata.org/docs/user_guide/timeseries.html
  - https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
confidence: high
cleaned: 2026-11-17
tier: practitioner
depth: core
---
# 6 — Dates and Times

A date in a file is text. It looks like a date to you, and to pandas it is a string that sorts by its first character, cannot be subtracted and has no month. Turning it into a date type is a cleaning step like turning `$48.00` into a number, and it has the same trap: the conversion can succeed and still be wrong. `03/04/2025` is the 3rd of April to one person and the 4th of March to another. "9 o'clock" is a different moment in Oslo and in New York. "January" is a span of 31 days and not a moment at all. This chapter covers the type decisions a date needs: how to parse it and check the parse, what a duration is, when you mean a period, and what a time zone changes. What you then do along the time axis (change over time, resampling, rolling windows) is summarising, and it waits until [chapter 8](08-time-series.md).

Pandas has three types for time, and most confusion goes away once you know which one a column holds.

```text
  Timestamp   a moment          2025-01-03 10:00        "when did it happen?"
                                        |
  ----------------------------------------------------------------> time
                                |<---- 4 days ---->|
  Timedelta   a length of time, with no start         "how long did it take?"

                    [======== 2025-01 ========]
  Period      a whole span with a start and an end    "which month was it in?"
```

A column of each prints its dtype as `datetime64`, `timedelta64` and `period`. All of the code below runs on pandas 3.1.0.

## Parsing dates

The first reason to parse is that text does not behave like time. Sort three dates as text and then as dates.

```python
import pandas as pd

txt = pd.Series(["9/1/2025", "10/1/2025", "11/12/2024"])
print(txt.sort_values().tolist())
print(pd.to_datetime(txt, format="%m/%d/%Y").sort_values().dt.date.astype(str).tolist())
```

```text
['10/1/2025', '11/12/2024', '9/1/2025']
['2024-11-12', '2025-09-01', '2025-10-01']
```

As text, October 2025 comes before November 2024, because `1` sorts before `9`. Any "latest order" or "first purchase" computed on the text column is wrong, and nothing says so.

`pd.to_datetime` converts a column, and `parse_dates` in `read_csv` does the same at load time. Give it the `format` whenever you know it: this is faster and, more importantly, it stops pandas from guessing wrong on ambiguous dates.

```python
print(pd.to_datetime(["2025-01-03", "2025-01-08"]))
print(pd.to_datetime(["03/04/2025"], format="%d/%m/%Y"))
print(pd.to_datetime(["03/04/2025"], format="%m/%d/%Y"))
print(pd.to_datetime(["2025-01-03", "not a date"], errors="coerce"))
```

```text
DatetimeIndex(['2025-01-03', '2025-01-08'], dtype='datetime64[us]', freq=None)
DatetimeIndex(['2025-04-03'], dtype='datetime64[us]', freq=None)
DatetimeIndex(['2025-03-04'], dtype='datetime64[us]', freq=None)
DatetimeIndex(['2025-01-03', 'NaT'], dtype='datetime64[us]', freq=None)
```

The second and third lines parsed the same string into two different days, the 3rd of April and the 4th of March. `errors="coerce"` gives `NaT`, "not a time", the datetime version of `NaN`, and as with `to_numeric` in chapter 5 you must count what it produces.

The printed dtype is `datetime64[us]`, microsecond resolution. Pandas 3.0 changed this: older versions parsed to nanoseconds by default, and pandas now infers the unit, with microseconds for strings like these ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). It rarely shows, except in one case the release notes warn about. Converting a datetime to an integer now gives a number 1000 times smaller than old code expected, so state the unit with `as_unit` first if you depend on it.

```python
d = pd.Series(pd.to_datetime(["2025-01-03"]))
print(d.astype("int64").iloc[0], d.dt.as_unit("ns").astype("int64").iloc[0])
```

```text
1735862400000000 1735862400000000000
```

Resolution also sets the range. A 64-bit nanosecond timestamp spans only about 292 years, so `pd.Timestamp.min` and `max` are 1677-09-21 and 2262-04-11, the span the book quotes as 1678 to 2262 (*Python Data Science Handbook*, ch. 3). Coarser units widen it, which matters for historical dates.

## Check the parse

A parse that ran is not a parse that is right. Three numbers catch most problems: how many values failed, the earliest date and the latest date.

```python
col = pd.Series(["2025-01-03", "2025-01-08", "2052-01-09", "not a date"])
dates = pd.to_datetime(col, errors="coerce")
print(dates.isna().sum(), dates.min().date(), dates.max().date())
```

```text
1 2025-01-03 2052-01-09
```

One value failed, and the latest order is in 2052. That date parsed perfectly. It is a typing error for 2025, and only the `max` shows it. For an export that should cover one month, assert the range, as the second exercise in chapter 5 did.

A column that mixes two formats is harder. With no `format`, pandas takes the format from the first value and refuses the rest.

```python
mixed = pd.Series(["2025-01-03", "03/01/2025"])
try:
    pd.to_datetime(mixed)
except ValueError as e:
    print("ValueError:", str(e)[:75])
print(pd.to_datetime(mixed, format="mixed").dt.date.astype(str).tolist())
print(pd.to_datetime(mixed, format="mixed", dayfirst=True).dt.date.astype(str).tolist())
```

```text
ValueError: time data "03/01/2025" doesn't match format "%Y-%m-%d". You might want to t
['2025-01-03', '2025-03-01']
['2025-03-01', '2025-01-03']
```

The error is the good outcome, because it tells you the column is not what you assumed. `format="mixed"` parses each value on its own and gets rid of the error, but look at what it did. Without `dayfirst` it read `03/01/2025` as the 1st of March. With `dayfirst=True` it read that value as the 3rd of January, and it also turned the first value, written year-month-day, into the 1st of March. Neither call can know what the writer meant. When a column mixes conventions, find out where each batch of rows came from, and parse each batch with its own explicit `format`.

## Calendar parts and durations

A datetime column has a `.dt` accessor, just as a text column has `.str`, and it pulls out the calendar parts you need for grouping. Subtracting two datetimes gives a **timedelta**, a length of time. Say the shop also records when each order shipped.

```python
orders = pd.DataFrame({
    "order_id": [1001, 1003, 1007, 1012],
    "date": pd.to_datetime(["2025-01-03", "2025-01-05", "2025-01-11", "2025-01-20"]),
})
orders["shipped"] = pd.to_datetime(["2025-01-04", "2025-01-09", "2025-01-12", "2025-01-27"])
orders["weekday"] = orders["date"].dt.day_name()
orders["wait"] = orders["shipped"] - orders["date"]
print(orders[["order_id", "weekday", "wait"]])
print(orders["wait"].dt.days.tolist(), orders["wait"].mean(), orders["wait"].dtype)
```

```text
   order_id   weekday   wait
0      1001    Friday 1 days
1      1003    Sunday 4 days
2      1007  Saturday 1 days
3      1012    Monday 7 days
[1, 4, 1, 7] 3 days 06:00:00 timedelta64[us]
```

`wait` is a column of its own type, `timedelta64`. You can take its mean (3 days and 6 hours), compare it with `pd.Timedelta(days=2)`, or turn it into a plain number with `.dt.days` when a chart or a model needs one.

A timedelta is a fixed length of time. A month is not a fixed length, so adding "one month" needs a different tool, `pd.DateOffset`, which moves along the calendar.

```python
d = pd.Timestamp("2025-01-31")
print(d + pd.Timedelta(days=30), d + pd.DateOffset(months=1))
```

```text
2025-03-02 00:00:00 2025-02-28 00:00:00
```

Thirty days after 31 January is 2 March. One calendar month after it is 28 February, the last day that exists. A subscription that renews "monthly" means the second, and code that adds 30 days drifts away from it.

## Periods: when you mean the whole month

A timestamp is a moment and a **period** is a span, such as all of March 2024. For monthly reporting, a period label says what you mean: there is no argument about whether the row is labelled by the 1st or the 31st.

```python
p = pd.Period("2024-03")
print(p, p.start_time, p.end_time.date(), p + 1)
```

```text
2024-03 2024-03-01 00:00:00 2024-03-31 2024-04
```

A period knows its start and its end, and adding 1 moves it by one whole period. On a column, convert with `.dt.to_period`, and group by the result as you would any key.

```python
orders["month"] = orders["date"].dt.to_period("M")
orders["week"] = orders["date"].dt.to_period("W-SUN")
print(orders[["order_id", "date", "month", "week"]])
print(orders.groupby("week")["order_id"].count())
```

```text
   order_id       date    month                   week
0      1001 2025-01-03  2025-01  2024-12-30/2025-01-05
1      1003 2025-01-05  2025-01  2024-12-30/2025-01-05
2      1007 2025-01-11  2025-01  2025-01-06/2025-01-12
3      1012 2025-01-20  2025-01  2025-01-20/2025-01-26
week
2024-12-30/2025-01-05    2
2025-01-06/2025-01-12    1
2025-01-20/2025-01-26    1
Freq: W-SUN, Name: order_id, dtype: int64
```

The week label prints both ends, so nobody has to ask which day a week starts on. `W-SUN` is a week that ends on Sunday, which makes it run Monday to Sunday. The first week starts in 2024: a week does not respect the year boundary, so "week 1" needs a definition before two people compare numbers. Notice also that the week of 13 January has no row. No order fell in it, and a groupby only shows groups that have rows. Chapter 8 shows how to make such gaps visible.

Periods also express fiscal calendars. With a year ending in January, the fourth quarter of fiscal 2012 runs from 1 November 2011 to 31 January 2012, and with a year ending in June, August 2007 belongs to fiscal 2008 (*Python for Data Analysis*, ch. 11).

```python
q = pd.Period("2012Q4", freq="Q-JAN")
print(q.start_time.date(), q.end_time.date())
print(pd.Timestamp("2007-08-15").to_period("Y-JUN"))
```

```text
2011-11-01 2012-01-31
2008
```

The book writes the yearly frequency as `A-JUN`. Pandas 3.0 spells it `Y-JUN`.

## Time zones

A timestamp with no zone is **naive**: 09:00 where? The sensible rule for stored data is to keep it in UTC and convert only for display. `tz_localize` declares what zone a naive timestamp is in, and `tz_convert` changes the zone of one that already has it. Daylight-saving changes make local hours irregular: on a spring-forward day, a local day has 23 hours. That is another reason to do arithmetic in UTC.

```python
ts = pd.Series([1, 2], index=pd.to_datetime(["2024-03-30 22:00", "2024-03-31 22:00"]))
utc = ts.tz_localize("UTC")
oslo = utc.tz_convert("Europe/Oslo")
print(oslo.index)
print(pd.date_range("2024-03-31", periods=2, freq="D", tz="Europe/Oslo").to_series().diff().iloc[1])
```

```text
DatetimeIndex(['2024-03-30 23:00:00+01:00', '2024-04-01 00:00:00+02:00'],
              dtype='datetime64[us, Europe/Oslo]', freq=None)
0 days 23:00:00
```

A zone-aware timestamp stores UTC nanoseconds since the epoch, so `tz_convert` changes only how it is displayed: the stored integer (1299902400000000000 in McKinney's example) does not move (*Python for Data Analysis*, ch. 11). The zone also changes the answer to "which day was this sale?". The second stamp is 22:00 on March 31 in UTC, but it is already April 1 in Oslo, so a daily or even a monthly total by local date differs from one by UTC date. Choose the reporting zone before you group by day. The last line shows the other hazard: March 31 was the day the clocks went forward in Oslo, so that local day lasted 23 hours.

Going the other way, from local times to UTC, has two traps of its own.

```python
local = pd.Series(pd.to_datetime(["2024-03-30 09:00", "2024-03-31 09:00"])).dt.tz_localize("Europe/Oslo")
print(local.dt.tz_convert("UTC").tolist())
try:
    pd.Timestamp("2024-03-31 02:30").tz_localize("Europe/Oslo")
except ValueError as e:
    print("ValueError:", str(e)[:70])
print(pd.to_datetime(["2025-01-03T10:00:00+01:00", "2025-01-03T10:00:00Z"], utc=True))
```

```text
[Timestamp('2024-03-30 08:00:00+0000', tz='UTC'), Timestamp('2024-03-31 07:00:00+0000', tz='UTC')]
ValueError: 2024-03-31 02:30:00 is a nonexistent time due to daylight savings time
DatetimeIndex(['2025-01-03 09:00:00+00:00', '2025-01-03 10:00:00+00:00'],
              dtype='datetime64[us, UTC]', freq=None)
```

The shop opens at 09:00 Oslo time on both days, and those are two different UTC hours, 08:00 and 07:00, because the offset changed overnight. A fixed "subtract one hour" would have been wrong for half the year. The second line is a local time that never happened: the clocks jumped from 02:00 to 03:00, and pandas raises rather than invent a moment. The last call handles text that carries its own offsets. `utc=True` converts every value to UTC, so two strings that both say 10:00 come out an hour apart, which is what they were.

## Pitfalls

- **Dates left as text.** They sort alphabetically, cannot be subtracted and have no month. Check `dtypes` and pass `parse_dates`.
- **Ambiguous day and month.** State `format=`. Never let `dayfirst` or a guess decide for a whole column.
- **`errors="coerce"` without counting.** Print `isna().sum()`, and read `min` and `max`. A date in 2052 parses without complaint.
- **`format="mixed"` as a fix.** It removes the error and keeps the ambiguity. Parse each source with its own format.
- **Adding 30 days when you mean a month.** Use `pd.DateOffset(months=1)`, or work in periods.
- **Labelling a month with a timestamp.** Readers will ask whether `2024-01-31` means that day or the month. A period says which.
- **Naive timestamps from two sources.** If one is UTC and the other is local, every join and every daily total is off by hours. Localize each on arrival.
- **Local-time arithmetic across daylight saving.** Local days can be 23 or 25 hours long. Store in UTC and convert for display.
- **Old spellings.** `A-JUN` is now `Y-JUN`, and `PeriodIndex(year=, quarter=)` is deprecated.

## Try it

1. A European export writes dates as day/month/year: `pd.Series(["31/12/2024", "01/02/2025"])`. Parse it, then print the month names and the number of days between the two dates.

<details><summary>Answer</summary>

```python
a = pd.to_datetime(pd.Series(["31/12/2024", "01/02/2025"]), format="%d/%m/%Y")
print(a.dt.month_name().tolist(), (a.iloc[1] - a.iloc[0]).days)
```

```text
['December', 'February'] 32
```

With no format, the first value could only be day-first, and pandas would have applied that to the column. Had the file started with `01/02/2025`, it would have guessed month-first and failed on the 31st, or worse, on a file with no day above 12, succeeded.

</details>

2. How long was 27 October 2024 in Oslo, the day the clocks went back?

<details><summary>Answer</summary>

```python
day = pd.date_range("2024-10-27", periods=2, freq="D", tz="Europe/Oslo")
print(day[1] - day[0])
```

```text
1 days 01:00:00
```

Twenty-five hours. An hourly average for that day divides by 25 and not 24.

</details>

3. Two sales are stamped in UTC: `2025-01-31 23:30` and `2025-02-01 00:30`. Which month does each belong to by UTC, and which by New York local time?

<details><summary>Answer</summary>

```python
stamps = pd.Series(pd.to_datetime(["2025-01-31 23:30", "2025-02-01 00:30"])).dt.tz_localize("UTC")
print(stamps.dt.tz_localize(None).dt.to_period("M").astype(str).tolist())
ny = stamps.dt.tz_convert("America/New_York")
print(ny.dt.tz_localize(None).dt.to_period("M").astype(str).tolist())
```

```text
['2025-01', '2025-02']
['2025-01', '2025-01']
```

By UTC the second sale is in February, and in New York it is still the evening of 31 January. `tz_localize(None)` drops the zone and keeps the wall-clock time, which is what a period should be built from. January's total depends on the zone you report in.

</details>

4. Work through the Datetime Basics and Periods sections of `practice/7_Time_Series.ipynb`. `practice/mckinney/ch11.ipynb` has the book's full chapter, with some old frequency aliases that chapter 8's table translates.

## Interview checklist

| Question | What a good answer covers |
|---|---|
| A date column loaded as text. Why does it matter? | Text sorts by character, so `10/1` comes before `9/1`. It cannot be subtracted, grouped by month or resampled. |
| How do you parse a date column safely? | State `format`. Use `errors="coerce"` and count the `NaT`. Read `min` and `max` for implausible dates. |
| What do you do with `03/04/2025`? | It is ambiguous. Find out the source's convention and state the format. A column that mixes conventions has to be split by source. |
| Timestamp, timedelta or period? | A moment, a length of time, and a span with a start and an end. Use periods when a row stands for a whole month or quarter. |
| How do you add one month to a date? | `pd.DateOffset(months=1)`, which follows the calendar. `Timedelta(days=30)` is a fixed length and drifts. |
| What is a naive timestamp? | One with no time zone. `tz_localize` declares its zone and `tz_convert` changes the zone of an aware one. |
| How do you handle time zones? | Store in UTC, convert for display, and pick the reporting zone before grouping by day or month. Local days can be 23 or 25 hours long. |
| Why did converting a datetime to an integer change? | Pandas 3.0 infers the resolution, usually microseconds and no longer nanoseconds. State the unit with `as_unit`. |

## Next

Every column is now a type you can trust, dates included. The export is ready to be summarised. Next: [Groupby and aggregation](07-groupby-and-aggregation.md).
