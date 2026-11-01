---
origin: synthesis
sources:
  - "McKinney, Python for Data Analysis, 2nd ed. (O'Reilly, 2017), ch. 11; 3rd ed. open access at https://wesmckinney.com/book/time-series"
  - "VanderPlas, Python Data Science Handbook (O'Reilly, 2016), ch. 3; https://jakevdp.github.io/PythonDataScienceHandbook/03.11-working-with-time-series.html"
  - https://pandas.pydata.org/docs/user_guide/timeseries.html
  - https://pandas.pydata.org/docs/user_guide/window.html
  - https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
confidence: high
cleaned: 2026-11-01
---
# 6 — Time Series

"How did we do last month?" sounds like a groupby, and it nearly is. But time carries rules that labels do not. Rows have a meaningful order, so "the previous value" exists. Months have different lengths, so a monthly total is not comparable to the last one without thought. A label such as "January" stands for an interval, and an interval can be labelled at either end. A date printed as `03/04/2025` means two different days depending on who wrote it. And when a value is missing from a time series, the row is often simply absent, so you cannot see the gap. This chapter gives the shop a year of daily revenue and takes it through parsing, indexing, changes over time, resampling, time zones and rolling windows. These are the tools that the forecasting chapter in pillar 06 assumes you already have.

Frequency names changed in pandas 3.0, so this is the chapter where code from older books breaks most often. All of the code below runs on pandas 3.1.0.

## Parsing dates

A date in a CSV is text until you say otherwise. `pd.to_datetime` converts it. Give it the `format` whenever you know it: this is faster and, more importantly, it stops pandas from guessing wrong on ambiguous dates.

```python
import numpy as np
import pandas as pd

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

The second and third lines parsed the same string into two different days, the 3rd of April and the 4th of March. If a file mixes both conventions, no parser can save you, so check the `min` and `max` and look for implausible values. `errors="coerce"` gives `NaT`, "not a time", the datetime version of `NaN`, and as with `to_numeric` you must count what it produces.

The printed dtype is `datetime64[us]`, microsecond resolution. Pandas 3.0 changed this: older versions parsed to nanoseconds by default, and pandas now infers the unit, with microseconds for strings like these ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). It rarely shows, except in one case the release notes warn about. Converting a datetime to an integer now gives a number 1000 times smaller than old code expected, so state the unit with `as_unit` first if you depend on it.

```python
d = pd.Series(pd.to_datetime(["2025-01-03"]))
print(d.astype("int64").iloc[0], d.dt.as_unit("ns").astype("int64").iloc[0])
```

```text
1735862400000000 1735862400000000000
```

A datetime column has a `.dt` accessor, just as a text column has `.str`, and it pulls out the calendar parts you need for grouping. Subtracting two datetimes gives a timedelta.

```python
orders = pd.DataFrame({
    "order_id": [1001, 1003, 1007, 1012],
    "date": pd.to_datetime(["2025-01-03", "2025-01-05", "2025-01-11", "2025-01-20"]),
})
orders["weekday"] = orders["date"].dt.day_name()
orders["month"] = orders["date"].dt.to_period("M")
orders["days_since_last"] = orders["date"].diff().dt.days
print(orders)
```

```text
   order_id       date   weekday    month  days_since_last
0      1001 2025-01-03    Friday  2025-01              NaN
1      1003 2025-01-05    Sunday  2025-01              2.0
2      1007 2025-01-11  Saturday  2025-01              6.0
3      1012 2025-01-20    Monday  2025-01              9.0
```

## A year of daily revenue

Put the datetimes in the index and pandas unlocks everything else in this chapter. The 11 orders from earlier chapters are too few for this, so here is the shop's whole previous year. It is synthetic, built with a fixed seed so your output matches: a slow upward trend, a weekly pattern that peaks at the weekend, a December bump, some noise, and three days missing because the checkout was down.

```python
rng = np.random.default_rng(7)
days = pd.date_range("2024-01-01", "2024-12-31", freq="D")
trend = 400 + 0.5 * np.arange(len(days))
week = np.array([0.9, 0.85, 0.9, 0.95, 1.05, 1.25, 1.1])[days.day_of_week]
december = np.where(days.month == 12, 1.4, 1.0)
noise = rng.normal(1.0, 0.08, len(days))
daily = pd.Series((trend * week * december * noise).round(2), index=days, name="revenue")
daily = daily.drop(pd.to_datetime(["2024-03-14", "2024-03-15", "2024-08-02"]))
print(daily.head(3))
print(len(daily), daily.index.dtype, daily.index.is_monotonic_increasing)
```

```text
2024-01-01    360.04
2024-01-02    348.56
2024-01-03    352.99
Name: revenue, dtype: float64
363 datetime64[us] True
```

A `DatetimeIndex` accepts **partial strings**, the most pleasant thing about it. A year or a month is a slice of the time axis, not an exact match, and slices between dates include both ends because they are label slices (chapter 3).

```python
print(daily.loc["2024-02"].shape, daily.loc["2024"].shape)
print(daily.loc["2024-02-27":"2024-03-01"])
print(daily.loc["2024-03-13":"2024-03-16"])
```

```text
(29,) (363,)
2024-02-27    383.67
2024-02-28    430.53
2024-02-29    385.97
2024-03-01    458.84
Name: revenue, dtype: float64
2024-03-13    377.86
2024-03-16    577.04
Name: revenue, dtype: float64
```

The last result has two rows for a four-day range. Nothing warned about the outage, since the days are just absent. Make gaps visible by conforming the series to a regular frequency with `asfreq`, and then decide what they mean.

```python
regular = daily.asfreq("D")
print(regular.isna().sum(), regular.index.freqstr)
print(regular.loc["2024-03-13":"2024-03-16"])
```

```text
3 D
2024-03-13    377.86
2024-03-14       NaN
2024-03-15       NaN
2024-03-16    577.04
Freq: D, Name: revenue, dtype: float64
```

Here a gap is an outage, so the true revenue was close to zero, and leaving `NaN` keeps the honest record. For a sensor, you might interpolate. For a price, you might carry forward. Chapter 2's question comes back: what does this gap mean?

## Frequencies and date ranges

`date_range` generates a regular index, and `freq` names the step using a string. These names changed. Pandas 3.0 removed `M`, `Q`, `Y` and their relatives in favour of the explicit `ME`, `QE`, `YE`, along with the uppercase `H` and `T` in favour of `h` and `min` ([pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)). The reason is a real ambiguity: `ME` says month **end**, as distinct from `MS` for month **start**. If an old notebook fails on `freq='M'`, this is why; `practice/7_Time_Series.ipynb` needed this patch.

| Alias | Meaning | Old spelling |
|---|---|---|
| `D` | calendar day | same |
| `B` | business day | same |
| `W-SUN` | weekly, ending Sunday | same |
| `MS` / `ME` | month start / month end | `MS` / `M` |
| `QE` | quarter end | `Q` |
| `YE` | year end | `A`, `Y` |
| `h` | hour | `H` |
| `min` | minute | `T` |
| `s` | second | `S` |

```python
print(pd.date_range("2024-01-31", periods=3, freq="ME"))
print(pd.date_range("2024-01-01", periods=3, freq="MS"))
print(pd.date_range("2024-01-01", periods=3, freq="W-SUN"))
print(pd.date_range("2024-01-01 09:00", periods=3, freq="90min"))
try:
    pd.date_range("2024-01-31", periods=3, freq="M")
except ValueError as e:
    print("ValueError:", str(e)[:60])
```

```text
DatetimeIndex(['2024-01-31', '2024-02-29', '2024-03-31'],
              dtype='datetime64[us]', freq='ME')
DatetimeIndex(['2024-01-01', '2024-02-01', '2024-03-01'],
              dtype='datetime64[us]', freq='MS')
DatetimeIndex(['2024-01-07', '2024-01-14', '2024-01-21'],
              dtype='datetime64[us]', freq='W-SUN')
DatetimeIndex(['2024-01-01 09:00:00', '2024-01-01 10:30:00',
               '2024-01-01 12:00:00'],
              dtype='datetime64[us]', freq='90min')
ValueError: Invalid frequency: M. Failed to parse with error message: Va
```

## Change over time: shift and pct_change

`shift` slides the values along the index and leaves the labels alone, so each row can see an earlier value. It is the one tool behind every comparison to a previous period.

```python
s = regular.loc["2024-02-01":"2024-02-05"].to_frame()
s["yesterday"] = s["revenue"].shift(1)
s["change"] = s["revenue"] - s["yesterday"]
s["pct"] = s["revenue"].pct_change()
print(s.round(3))
```

```text
            revenue  yesterday  change    pct
2024-02-01   379.64        NaN     NaN    NaN
2024-02-02   402.61     379.64   22.97  0.061
2024-02-03   486.94     402.61   84.33  0.209
2024-02-04   497.63     486.94   10.69  0.022
2024-02-05   351.48     497.63 -146.15 -0.294
```

A daily percentage change on this data mostly measures the weekly pattern, since Saturday beats Tuesday every week. Compare like with like: shift by 7 for the same weekday last week. That is the seasonal comparison every "week over week" chart makes.

```python
wow = regular / regular.shift(7) - 1
print(wow.loc["2024-06-10":"2024-06-12"].round(3))
print(round(regular.pct_change().abs().mean(), 3), round(wow.abs().mean(), 3))
```

```text
2024-06-10    0.067
2024-06-11    0.148
2024-06-12    0.000
Freq: D, Name: revenue, dtype: float64
0.13 0.091
```

The last line is the point. The typical absolute change falls from 13% day over day to about 9% week over week, because the shift removes the weekly pattern and leaves mostly the noise we built in.

`shift` is also how you build features for a model, and that creates the main hazard in time-series analysis, **leakage**. `shift(-1)` puts tomorrow's value on today's row. Used as an input to a prediction of today, it would look brilliant in testing and be impossible in production, as tomorrow is not yet known. Keep features looking backward, with positive shifts only.

## Resampling: changing the frequency

Going from daily to monthly is a groupby in which the key is a time bin. `resample` makes that a single call, and returns an object you aggregate as you would a GroupBy.

```python
monthly = regular.resample("ME").sum()
print(monthly.head(3).round(0))
print(regular.resample("ME").agg(["sum", "mean", "count"]).head(3).round(1))
```

```text
2024-01-31    11993.0
2024-02-29    12266.0
2024-03-31    12775.0
Freq: ME, Name: revenue, dtype: float64
                sum   mean  count
2024-01-31  11992.8  386.9     31
2024-02-29  12266.4  423.0     29
2024-03-31  12775.1  440.5     29
```

Read the `count` column. February has 29 days and March 29 observations once the two outage days drop out, and January has 31. A monthly `sum` compares unequal lengths; December looks big partly for having 31 days and February small partly for having 29. Mean daily revenue per month is often the fairer comparison, and it is why the table shows both.

A bin is an interval, and two choices define it. **`closed`** says which edge belongs inside. **`label`** says which edge names the bin. For month-end bins, pandas defaults to closed on the right and labelled on the right, so January is labelled `2024-01-31`. For a 5-minute bin the defaults are left and left. The difference matters at the boundaries, and it is easiest to see on a small example.

```text
   minutes:   0   1   2   3   4   5   6   7   8   9   10
              |-------------------|-------------------|
  closed=left, label=left:
              [ 0, 1, 2, 3, 4 )     labelled 00:00
                                  [ 5, 6, 7, 8, 9 )   labelled 00:05
  closed=right, label=right:
                ( 1, 2, 3, 4, 5 ]   labelled 00:05  (minute 0 falls in the bin before)
```

```python
mins = pd.Series(range(12), index=pd.date_range("2024-01-01 09:00", periods=12, freq="min"))
print(mins.resample("5min").sum())
print(mins.resample("5min", closed="right", label="right").sum())
```

```text
2024-01-01 09:00:00    10
2024-01-01 09:05:00    35
2024-01-01 09:10:00    21
Freq: 5min, dtype: int64
2024-01-01 09:00:00     0
2024-01-01 09:05:00    15
2024-01-01 09:10:00    40
2024-01-01 09:15:00    11
Freq: 5min, dtype: int64
```

Both versions are right, and they answer slightly different questions. In finance and logging, whether the value stamped 09:05 is included in the 09:05 bar is a real decision, so make it on purpose. Weekly bins need the same care: `W-SUN` ends the week on Sunday, and a retail team that reports Monday-to-Sunday wants exactly that.

Going the other way, **upsampling**, creates rows with nothing in them, and you must choose how to fill them. Carrying a value forward assumes it held until the next one, which suits a monthly price list and misrepresents a monthly sales total.

```python
price_list = pd.Series([48.0, 52.0], index=pd.to_datetime(["2024-01-01", "2024-04-01"]))
print(price_list.resample("MS").asfreq())
print(price_list.resample("MS").ffill())
```

```text
2024-01-01    48.0
2024-02-01     NaN
2024-03-01     NaN
2024-04-01    52.0
Freq: MS, dtype: float64
2024-01-01    48.0
2024-02-01    48.0
2024-03-01    48.0
2024-04-01    52.0
Freq: MS, dtype: float64
```

## Periods: when you mean the whole month

A timestamp is a moment and a **period** is a span, such as all of March 2024. For monthly reporting, a period label says what you mean: there is no argument about whether the row is labelled by the 1st or the 31st. Convert with `to_period`, and group by the result as you would any key. This also gives the seasonal view, with one row per month.

```python
by_month = regular.groupby(regular.index.to_period("M")).agg(["sum", "mean"])
print(by_month.head(2).round(1))
print(pd.Period("2024-03").start_time, pd.Period("2024-03").end_time.date())
print(regular.groupby(regular.index.day_name()).mean().round(0).sort_values(ascending=False).head(3))
```

```text
             sum   mean
2024-01  11992.8  386.9
2024-02  12266.4  423.0
2024-03-01 00:00:00 2024-03-31
Saturday    626.0
Sunday      568.0
Friday      536.0
Name: revenue, dtype: float64
```

Saturday leads, as the weekly pattern we built in says it should. Grouping by weekday is how you check for a pattern like that on real data, before you trust any comparison across days.

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

The zone also changes the answer to "which day was this sale?". The second stamp is 22:00 on March 31 in UTC, but it is already April 1 in Oslo, so a daily or even a monthly total by local date differs from one by UTC date. Choose the reporting zone before you resample. The last line shows the other hazard: March 31 was the day the clocks went forward in Oslo, so that local day lasted 23 hours.

## Rolling windows

A rolling window slides a fixed span along the series and computes a statistic at each step. This is the case Wickham's split-apply-combine excludes, as pieces overlap ([Wickham, JSS 2011](https://doi.org/10.18637/jss.v040.i01)). A 7-day rolling mean removes the weekly pattern in one line, because each window holds one of every weekday.

```python
smooth = pd.DataFrame({
    "daily": regular,
    "ma7": regular.rolling(7, min_periods=5).mean(),
    "ma7_time": regular.rolling("7D").mean(),
    "expanding": regular.expanding().mean(),
    "ewm": regular.ewm(span=7).mean(),
})
print(smooth.loc["2024-01-01":"2024-01-08"].round(1))
print(smooth.loc["2024-03-13":"2024-03-16", ["daily", "ma7", "ewm"]].round(1))
```

```text
            daily    ma7  ma7_time  expanding    ewm
2024-01-01  360.0    NaN     360.0      360.0  360.0
2024-01-02  348.6    NaN     354.3      354.3  353.5
2024-01-03  353.0    NaN     353.9      353.9  353.3
2024-01-04  354.2    NaN     354.0      354.0  353.6
2024-01-05  406.8  364.5     364.5      364.5  371.0
2024-01-06  463.2  381.0     381.0      381.0  399.1
2024-01-07  445.4  390.2     390.2      390.2  412.4
2024-01-08  402.1  396.2     396.2      391.7  409.6
            daily    ma7    ewm
2024-03-13  377.9  424.5  399.3
2024-03-14    NaN  421.7  399.3
2024-03-15    NaN  406.7  399.3
2024-03-16  577.0  425.1  465.4
```

Each column tells you something different.

- **`rolling(7)`** counts seven rows, and requires seven non-missing values by default. `min_periods` relaxes that; here the first four rows stay empty and the mean starts on row five.
- **`rolling("7D")`** covers seven days of the calendar. On a series with absent rows, a count-based window spans more calendar time than you think: on the original `daily`, which has no rows for the outage, `rolling(7)` on March 16 reaches back nine days. Prefer the time-based form on irregular data.
- **`expanding`** uses everything so far, which suits a running total or a mean to date.
- **`ewm`** is an exponentially weighted mean, which gives recent days more weight, so it responds faster to a change than a flat window of similar span.

By default a rolling window is **trailing**: the value on a date uses that date and earlier ones, so it could have been known at the time. `center=True` looks nicer on a chart, since it removes the lag, but it uses future values, so it is off limits for anything you feed to a model. That is the leakage hazard again.

```python
compare = pd.DataFrame({"trailing": regular.rolling(7).mean(), "centered": regular.rolling(7, center=True).mean()})
dec = compare.loc["2024-11-29":"2024-12-03"].round(0)
print(dec)
```

```text
            trailing  centered
2024-11-29     565.0     614.0
2024-11-30     564.0     636.0
2024-12-01     585.0     676.0
2024-12-02     614.0     727.0
2024-12-03     636.0     762.0
```

The December bump starts on the 1st. The centred column rises early, on November 29, days before the jump took place, by reading from the future, and the trailing column reacts only after the event. For a chart the centred line is acceptable. For a forecast, or anything claiming to predict, it is cheating.

Rolling works on any statistic. A rolling standard deviation is a quick volatility chart, and `rolling(...).corr(other)` gives a rolling correlation, which is the example McKinney builds on stock data in `practice/mckinney/ch11.ipynb`.

## Pitfalls

- **Dates left as text.** They sort alphabetically and do not resample. Check `dtypes` and pass `parse_dates`.
- **Ambiguous day and month.** State `format=`. Check `min` and `max`.
- **Absent rows taken for complete data.** Use `asfreq`, and compare `count` against the calendar.
- **Old frequency aliases.** `M`, `Q`, `Y`, `H` and `T` now raise an error. Use `ME`, `QE`, `YE`, `h`, `min`.
- **Comparing raw monthly sums.** Months have 28 to 31 days. Check per-day means too.
- **Leakage.** A negative `shift` and `center=True` both read the future. Fine on a chart, and not in a model.
- **Unsorted index.** Sort before you slice or take rolling windows: `sort_index()`. Check with `index.is_monotonic_increasing`.
- **Local-time arithmetic across daylight saving.** Store in UTC and convert for display.

## Try it

1. What was the best week of the year by total revenue, with weeks ending on Sunday?

<details><summary>Answer</summary>

```python
weekly = regular.resample("W-SUN").sum()
print(weekly.idxmax().date(), round(weekly.max(), 2))
```

```text
2024-12-08 5959.75
```

</details>

2. Compute month-over-month percentage change using mean daily revenue, so that month length does not distort it. Which month rose most, and does it make sense?

<details><summary>Answer</summary>

```python
m = regular.resample("ME").mean()
mom = m / m.shift(1) - 1
print(mom.idxmax().strftime("%B"), round(mom.max(), 3))
```

```text
December 0.444
```

It is December, which is the bump built into the data.

</details>

3. How many orders fall in the 30-day window ending at each order, counting that order itself? Given `dates = pd.Series(1, index=pd.to_datetime(["2024-01-01", "2024-01-20", "2024-02-05", "2024-03-20"]))`, use a time-based rolling window.

<details><summary>Answer</summary>

```python
dates = pd.Series(1, index=pd.to_datetime(["2024-01-01", "2024-01-20", "2024-02-05", "2024-03-20"]))
print(dates.rolling("30D").sum())
```

```text
2024-01-01    1.0
2024-01-20    2.0
2024-02-05    2.0
2024-03-20    1.0
dtype: float64
```

A count-based window could not answer this, as the gaps between orders vary.

</details>

4. Work through `practice/7_Time_Series.ipynb`, which repeats these moves on synthetic series and ends with rolling means and correlations on stock prices (`data/stock_px_2.csv`, which `fetch_data.sh` downloads). `practice/mckinney/ch11.ipynb` has the book's full chapter, with some old frequency aliases that the README's table translates.

## Interview checklist

| Question | What a good answer covers |
|---|---|
| Timestamp or period? | A timestamp is a moment, a period is a span. Use periods when the row stands for a whole month or quarter. |
| What does `resample` do? | Time-based groupby. Downsampling aggregates into bins with `closed` and `label` choices; upsampling makes empty rows that you must fill on purpose. |
| Why did `freq="M"` start failing? | Pandas 3.0 removed it for the explicit `ME` and `MS`. Similarly `QE`, `YE`, `h`, `min`. |
| How do you do a seasonal comparison? | `shift` by the season length, such as 7 for daily data with a weekly cycle, and compare like with like. |
| What is the difference between `rolling(7)` and `rolling("7D")`? | Seven rows against seven calendar days. They differ when rows are missing or irregular. |
| What is leakage, and how can a time series leak? | Using information not known at prediction time: negative shifts, centred windows, or filling backward. |
| How do you handle time zones? | Store in UTC, convert for display, pick the reporting zone before daily aggregation. Local days can be 23 or 25 hours long. |
| How do you find missing days? | `asfreq("D")` then `isna().sum()`, or compare `count` per month with the calendar. |
| What does `ewm` do differently from a rolling mean? | It weights recent values more, decaying exponentially, so it responds faster and has no hard window edge. |

## Next

You now have all the numbers. A table of 12 months hides a shape that a single chart reveals at a glance. Next: [Plotting](07-plotting.md).
