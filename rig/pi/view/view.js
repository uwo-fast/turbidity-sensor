"use strict";

const REFRESH_MS = 30000;
// Three missed cycles at the default 15 minutes: long enough not to cry wolf.
const STALE_MINUTES = 45;
const VERDICTS = {
  ok: "Good",
  thin: "Check: culture barely reached the sensor this burst",
  no_sample: "Check: no culture seen, check the tube and the level",
  no_motion: "Check: the signal did not move, the motor may have stalled",
  aborted: "Check: lost the sensor during this cycle",
};

function parseSummary(text) {
  const lines = text.split("\n").filter((line) => line.trim() !== "");
  if (lines.length === 0) return [];
  const columns = lines[0].split(",");
  const rows = [];
  for (const line of lines.slice(1)) {
    const fields = line.split(",");
    if (fields.length !== columns.length) continue; // a torn last line
    const row = Object.fromEntries(columns.map((name, index) => [name, fields[index]]));
    const time = new Date(row.time_utc);
    if (Number.isNaN(time.getTime())) continue;
    const level = row.sample_level === "" ? NaN : Number(row.sample_level);
    rows.push({ time, verdict: row.verdict, still: Number.isFinite(level) ? level : null });
  }
  return rows;
}

function verdictLabel(verdict) {
  return VERDICTS[verdict] || `Check: ${verdict}`;
}

function minutesText(minutes) {
  const whole = Math.max(0, Math.round(minutes));
  if (whole < 120) return `${whole} min ago`;
  return `${Math.round(whole / 60)} h ago`;
}

function goodRows(rows) {
  return rows.filter((row) => row.verdict === "ok" && row.still !== null);
}

// The state nothing else can be trusted without: is new data arriving, and was the last cycle good?
function summarize(rows, nowMs) {
  if (rows.length === 0) {
    return { kind: "none", title: "No data yet", detail: "Nothing has been logged." };
  }
  const last = rows[rows.length - 1];
  const age = (nowMs - last.time.getTime()) / 60000;
  if (age > STALE_MINUTES) {
    return {
      kind: "stale",
      title: "Not updating",
      detail: `Last cycle ${minutesText(age)}. The logger may have stopped.`,
    };
  }
  if (last.verdict !== "ok") {
    return { kind: "check", title: verdictLabel(last.verdict), detail: `Last cycle ${minutesText(age)}.` };
  }
  return { kind: "good", title: "Running normally", detail: `Last cycle ${minutesText(age)}.` };
}

// ---- the page ----

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function timeText(date) {
  return date.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function svgElement(name, attributes, text) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  if (text !== undefined) element.textContent = text;
  return element;
}

function drawChart(good) {
  const holder = document.getElementById("chart");
  holder.replaceChildren();
  setText("hover", " ");
  if (good.length < 2) {
    const note = document.createElement("p");
    note.className = "label";
    note.textContent = "The chart starts after two good readings.";
    holder.append(note);
    return;
  }
  const width = 720;
  const height = 280;
  const margin = { left: 48, right: 12, top: 12, bottom: 28 };
  const times = good.map((row) => row.time.getTime());
  const values = good.map((row) => row.still);
  const t0 = times[0];
  const t1 = times[times.length - 1];
  const low = Math.min(...values);
  const high = Math.max(...values);
  const pad = Math.max((high - low) * 0.1, 5);
  const yLow = low - pad;
  const yHigh = high + pad;
  const x = (t) => margin.left + ((t - t0) / Math.max(t1 - t0, 1)) * (width - margin.left - margin.right);
  const y = (v) => margin.top + ((yHigh - v) / (yHigh - yLow)) * (height - margin.top - margin.bottom);

  const svg = svgElement("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": `${good.length} good readings, from ${Math.round(low)} to ${Math.round(high)} counts`,
  });
  for (const v of [yLow, (yLow + yHigh) / 2, yHigh]) {
    svg.append(svgElement("line", { class: "grid", x1: margin.left, x2: width - margin.right, y1: y(v), y2: y(v) }));
    svg.append(svgElement("text", { x: margin.left - 6, y: y(v) + 4, "text-anchor": "end" }, String(Math.round(v))));
  }
  svg.append(svgElement("text", { x: margin.left, y: height - 8 }, timeText(good[0].time)));
  svg.append(svgElement("text", { x: width - margin.right, y: height - 8, "text-anchor": "end" }, timeText(good[good.length - 1].time)));
  svg.append(svgElement("polyline", { class: "line", points: good.map((row, i) => `${x(times[i])},${y(row.still)}`).join(" ") }));
  svg.append(svgElement("circle", { class: "point", r: 4, cx: x(t1), cy: y(values[values.length - 1]) }));
  const cursor = svgElement("line", { class: "cursor", y1: margin.top, y2: height - margin.bottom, visibility: "hidden" });
  svg.append(cursor);

  svg.addEventListener("pointermove", (event) => {
    const box = svg.getBoundingClientRect();
    const px = ((event.clientX - box.left) / box.width) * width;
    let nearest = 0;
    for (let i = 1; i < times.length; i++) {
      if (Math.abs(x(times[i]) - px) < Math.abs(x(times[nearest]) - px)) nearest = i;
    }
    const at = x(times[nearest]);
    cursor.setAttribute("x1", at);
    cursor.setAttribute("x2", at);
    cursor.setAttribute("visibility", "visible");
    setText("hover", `${timeText(good[nearest].time)}: ${good[nearest].still.toFixed(1)} counts`);
  });
  svg.addEventListener("pointerleave", () => {
    cursor.setAttribute("visibility", "hidden");
    setText("hover", " ");
  });
  holder.append(svg);
}

function drawTable(rows) {
  const body = document.getElementById("rows");
  body.replaceChildren();
  for (const row of rows.slice(-10).reverse()) {
    const line = document.createElement("tr");
    const when = document.createElement("td");
    when.textContent = timeText(row.time);
    const reading = document.createElement("td");
    reading.className = "number";
    // Thin readings are shown, in brackets, because they are all a thin burst has. Flagged ones are not.
    if (row.still === null || !["ok", "thin"].includes(row.verdict)) reading.textContent = "–";
    else reading.textContent = row.verdict === "ok" ? row.still.toFixed(1) : `(${row.still.toFixed(1)})`;
    const result = document.createElement("td");
    result.textContent = verdictLabel(row.verdict);
    line.append(when, reading, result);
    body.append(line);
  }
}

function showStatus(state) {
  document.getElementById("status").className = `status ${state.kind}`;
  setText("status-title", state.title);
  setText("status-detail", state.detail);
}

async function refresh() {
  const checked = new Date();
  try {
    const response = await fetch("summary.csv", { cache: "no-store" });
    if (response.status === 404) {
      draw([]);
    } else if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    } else {
      draw(parseSummary(await response.text()));
    }
    setText("checked", `Page last checked ${checked.toLocaleTimeString()}. Checks every ${REFRESH_MS / 1000} s.`);
  } catch (error) {
    showStatus({ kind: "error", title: "Cannot reach the data", detail: "The viewer may have stopped. This does not affect logging." });
    setText("checked", `Last attempt ${checked.toLocaleTimeString()}.`);
  }
}

function draw(rows) {
  showStatus(summarize(rows, Date.now()));
  const good = goodRows(rows);
  const latest = good[good.length - 1];
  setText("reading", latest ? latest.still.toFixed(1) : "–");
  setText("reading-time", latest ? `${timeText(latest.time)}, ADC counts` : "");
  drawChart(good);
  drawTable(rows);
}

if (typeof document !== "undefined") {
  refresh();
  setInterval(refresh, REFRESH_MS);
}
if (typeof module !== "undefined") {
  module.exports = { parseSummary, summarize, goodRows, verdictLabel, STALE_MINUTES };
}
