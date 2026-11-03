// The presentation layer: it fetches JSON and draws it. No clustering and no customer rows here.
import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { Legend, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";

// These types describe the JSON the API promises. They vanish at build time, so they check this
// file's use of the data and do not check what the server really sends.
type Summary = { segment: string; customers: number; avg_spend: number; avg_days_since_order: number; avg_open_rate: number };
type MapBin = { segment: string; x: number; y: number; customers: number };

// Colour and shape follow the name, so a filter can never repaint a segment.
const STYLE = {
  "Loyal regulars": { fill: "#2a78d6", shape: "circle" },
  "Discount hunters": { fill: "#eb6834", shape: "square" },
  "Lapsed email readers": { fill: "#1baf7a", shape: "triangle" },
  "One and done": { fill: "#eda100", shape: "diamond" },
} as const;
type SegmentName = keyof typeof STYLE;
const NAMES = Object.keys(STYLE) as SegmentName[];

// A demo only: the key comes from the address bar so that it is not compiled into the bundle,
// where every visitor could read it. A real app signs people in and sends a session cookie.
const KEY = new URLSearchParams(location.search).get("key") ?? "";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path, { headers: { "X-API-Key": KEY } });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json() as Promise<T>;
}

function App() {
  const [region, setRegion] = useState("");
  const [regions, setRegions] = useState<string[]>([]);
  const [summary, setSummary] = useState<Summary[]>([]);
  const [bins, setBins] = useState<MapBin[]>([]);
  const [error, setError] = useState("");

  useEffect(() => { getJson<string[]>("/v1/regions").then(setRegions, (e) => setError(String(e))); }, []);

  useEffect(() => {
    // Two quick filter changes can answer out of order, so an answer to an old filter is ignored.
    let current = true;
    const query = region ? `?region=${encodeURIComponent(region)}` : "";
    Promise.all([getJson<Summary[]>(`/v1/segments${query}`), getJson<MapBin[]>(`/v1/segments/map${query}`)])
      .then(([s, b]) => { if (current) { setSummary(s); setBins(b); setError(""); } })
      .catch((e) => { if (current) setError(String(e)); });
    return () => { current = false; };
  }, [region]);

  if (error) return <p role="alert">Could not load the segments: {error}</p>;
  const total = summary.reduce((sum, row) => sum + row.customers, 0);
  const ordered = NAMES.flatMap((name) => summary.filter((row) => row.segment === name));

  return (
    <main>
      <h1>Fernhill customer segments</h1>
      <p>Labels from the batch job, read from a table. Synthetic data.</p>
      <label>Region
        <select value={region} onChange={(e) => setRegion(e.target.value)}>
          <option value="">All regions</option>
          {regions.map((name) => <option key={name}>{name}</option>)}
        </select>
      </label>
      <figure>
        <ScatterChart width={860} height={380} margin={{ top: 12, right: 12, bottom: 4, left: 0 }}>
          <XAxis type="number" dataKey="x" name="Coordinate 1" domain={["auto", "auto"]} tick={false} label="Coordinate 1" height={36} />
          <YAxis type="number" dataKey="y" name="Coordinate 2" domain={["auto", "auto"]} tick={false} width={36}
            label={{ value: "Coordinate 2", angle: -90 }} />
          <ZAxis type="number" dataKey="customers" name="Customers" range={[12, 220]} />
          <Tooltip />
          <Legend verticalAlign="top" itemSorter={(item) => NAMES.indexOf(item.value as SegmentName)}
            formatter={(value) => <span style={{ color: "#52514e" }}>{value}</span>} />
          {NAMES.map((name) => (
            <Scatter key={name} name={name} isAnimationActive={false} fillOpacity={0.75}
              fill={STYLE[name].fill} shape={STYLE[name].shape} legendType={STYLE[name].shape} data={bins.filter((bin) => bin.segment === name)} />
          ))}
        </ScatterChart>
        <figcaption>Each mark is a grid cell of at least 5 customers, sized by count. The coordinates are for looking only: distance on this plot is not a score.</figcaption>
      </figure>
      <table>
        <caption hidden>The same segments as a table</caption>
        <thead><tr><th scope="col">Segment</th><th scope="col">Customers</th><th scope="col">Share</th><th scope="col">Average 12-month spend</th><th scope="col">Days since order</th><th scope="col">Email open rate</th></tr></thead>
        <tbody>
          {ordered.map((row) => (
            <tr key={row.segment}>
              <td>{row.segment}</td>
              <td>{row.customers.toLocaleString("en-GB")}</td>
              <td>{((row.customers / total) * 100).toFixed(0)}%</td>
              <td>£{row.avg_spend.toFixed(0)}</td>
              <td>{row.avg_days_since_order.toFixed(0)}</td>
              <td>{(row.avg_open_rate * 100).toFixed(0)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
