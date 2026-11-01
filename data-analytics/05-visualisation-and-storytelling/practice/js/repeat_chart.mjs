// The chart itself in D3. It only needs a DOM, so the same file runs in a browser and in Node.
import * as d3 from "d3";

export function drawRepeatChart(container, data, { order, colours, width, height }) {
  const margin = { top: 58, right: 110, bottom: 28, left: 44 };
  const rows = data.map((d) => ({ ...d, date: new Date(d.month) }));

  // 1. Scales turn data values into pixels and colours.
  const x = d3.scaleUtc(d3.extent(rows, (d) => d.date), [margin.left, width - margin.right]);
  const y = d3.scaleLinear([0, 60], [height - margin.bottom, margin.top]);
  const colour = d3.scaleOrdinal(order, colours);

  const svg = d3.select(container).append("svg")
    .attr("xmlns", "http://www.w3.org/2000/svg")
    .attr("viewBox", [0, 0, width, height]).attr("width", width).attr("height", height)
    .attr("font-family", "Helvetica, Arial, sans-serif").attr("font-size", 12);

  // 2. Axes are drawn from the scales, then styled down until they recede.
  svg.append("g").attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat(d3.utcFormat("%Y")).tickSize(0).tickPadding(8))
    .call((g) => g.select(".domain").attr("stroke", "#c3c2b7"))
    .call((g) => g.selectAll("text").attr("fill", "#52514e"));
  svg.append("g").attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(6).tickSize(-(width - margin.left - margin.right)).tickPadding(8))
    .call((g) => g.select(".domain").remove())
    .call((g) => g.selectAll("line").attr("stroke", "#e1e0d9"))
    .call((g) => g.selectAll("text").attr("fill", "#52514e"));

  svg.append("text").attr("x", margin.left).attr("y", margin.top - 12).attr("fill", "#52514e")
    .attr("text-anchor", "start").text("90-day repeat rate (%)");

  // 3. The data join: one <path> per channel.
  const line = d3.line().x((d) => x(d.date)).y((d) => y(d.rate));
  const series = d3.groups(rows, (d) => d.channel)
    .sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
  svg.append("g").selectAll("path").data(series).join("path")
    .attr("fill", "none").attr("stroke-width", 2)
    .attr("stroke", ([name]) => colour(name)).attr("d", ([, values]) => line(values));

  // 4. Direct labels at the line ends, in ink rather than the series colour.
  svg.append("g").selectAll("text").data(series).join("text")
    .attr("x", width - margin.right + 6).attr("dy", "0.32em").attr("fill", "#52514e")
    .attr("y", ([name, values]) => y(values.at(-1).rate) + (name === "Referral" ? 7 : name === "Organic search" ? -7 : 0))
    .text(([name]) => name);

  // 5. A legend row, and the event that explains the shape.
  const legend = svg.append("g").selectAll("g").data(order).join("g")
    .attr("transform", (_, i) => `translate(${margin.left + i * 120},14)`);
  legend.append("rect").attr("width", 14).attr("height", 3).attr("y", -2).attr("fill", (d) => colour(d));
  legend.append("text").attr("x", 19).attr("dy", "0.32em").attr("fill", "#0b0b0b").text((d) => d);
  const cut = x(new Date("2025-01-01"));
  svg.append("line").attr("x1", cut).attr("x2", cut).attr("y1", margin.top).attr("y2", height - margin.bottom)
    .attr("stroke", "#898781");
  svg.append("text").attr("x", cut + 5).attr("y", margin.top + 8).attr("fill", "#52514e").text("Email budget cut");

  // 6. Hover layer: a big invisible hit target per point, and one tooltip element.
  const tip = svg.append("text").attr("class", "tip").attr("fill", "#0b0b0b").attr("font-weight", 700)
    .attr("visibility", "hidden");
  svg.append("g").attr("class", "hover").selectAll("circle").data(rows).join("circle")
    .attr("cx", (d) => x(d.date)).attr("cy", (d) => y(d.rate)).attr("r", 8)
    .attr("fill", "transparent")
    .on("mouseover", (_, d) => tip.attr("visibility", "visible")
      .attr("x", x(d.date) + 8).attr("y", y(d.rate) - 8)
      .text(`${d.channel}, ${d.month.slice(0, 7)}: ${d.rate}%`))
    .on("mouseout", () => tip.attr("visibility", "hidden"));
  return svg.node();
}
