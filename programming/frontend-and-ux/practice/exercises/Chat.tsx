// Exercise 3. This chat looks fine in a demo: the happy path renders and streams.
// Fix it until the browser tests pass: TARGET=exercises node --test tests/browser.test.ts
// Import ../solutions/state.ts and ../solutions/client.ts so this step does not
// depend on exercises 1 and 2, or use your own once they pass.

import { useState } from "react";
import { SseParser } from "../solutions/sse.ts";

type Source = { id: number; title: string; url: string };

export function Chat() {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);
  const [scenario, setScenario] = useState("answer");

  async function send() {
    setLoading(true);
    setFailed(false);
    setAnswer("");
    setSources([]);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({ question: input, scenario }),
      });
      const parser = new SseParser();
      const reader = res.body!.getReader();
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const e of parser.push(value)) {
          const data = JSON.parse(e.data);
          if (e.event === "delta") setAnswer((a) => a + data.text);
          if (e.event === "citation") setSources((s) => [...s, data]);
        }
      }
    } catch {
      setAnswer("");
      setFailed(true);
    }
    setLoading(false);
  }

  return (
    <div>
      <div style={{ fontSize: 24, fontWeight: 700 }}>Harbour help</div>
      <div
        role="log"
        aria-live="polite"
        style={{ color: "#999" }}
        dangerouslySetInnerHTML={{ __html: answer }}
      />
      {failed && <div style={{ color: "red" }}>Error</div>}
      {sources.map((s, i) => (
        <div key={i}><a href={s.url}>Source</a></div>
      ))}
      <textarea placeholder="Ask anything" value={input} onChange={(e) => setInput(e.target.value)} />
      <select id="scenario" aria-label="Mock scenario" value={scenario} onChange={(e) => setScenario(e.target.value)}>
        <option>answer</option>
        <option>uncertain</option>
        <option>no-evidence</option>
        <option>mid-stream-error</option>
        <option>dropped</option>
        <option>untrusted</option>
      </select>
      <div style={{ cursor: "pointer" }} onClick={() => void send()}>
        {loading ? "..." : "Send"}
      </div>
    </div>
  );
}
