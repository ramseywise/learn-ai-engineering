// An incremental parser for the event-stream format, written from the HTML
// Living Standard section 9.2.6. Network chunks do not respect event, line or
// even character boundaries, so everything here survives being cut anywhere.

export type SseEvent = { event: string; data: string; id?: string };

export class SseParser {
  #decoder = new TextDecoder("utf-8"); // stream mode holds a split character
  #buffer = "";
  #data: string[] = [];
  #event = "";
  #id: string | undefined;
  #started = false;

  push(chunk: Uint8Array | string): SseEvent[] {
    // The decoder already drops a leading byte order mark. A string skips it.
    let text = typeof chunk === "string" ? chunk : this.#decoder.decode(chunk, { stream: true });
    if (!this.#started && text.length > 0) {
      this.#started = true;
      if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
    }
    this.#buffer += text;
    return this.#drain();
  }

  // The spec discards an event that has no closing blank line. That is what
  // makes a cut-off stream detectable: the half-sent event never appears.
  end(): SseEvent[] {
    this.#buffer += this.#decoder.decode();
    const events = this.#drain(true);
    this.#data = [];
    this.#event = "";
    this.#buffer = "";
    return events;
  }

  #drain(atEnd = false): SseEvent[] {
    const events: SseEvent[] = [];
    let start = 0;
    for (let i = 0; i < this.#buffer.length; i++) {
      const ch = this.#buffer[i];
      if (ch !== "\n" && ch !== "\r") continue;
      // A CR as the last byte seen may be half of a CRLF. Wait for more.
      if (ch === "\r" && i === this.#buffer.length - 1 && !atEnd) break;
      const line = this.#buffer.slice(start, i);
      if (ch === "\r" && this.#buffer[i + 1] === "\n") i++;
      start = i + 1;
      const event = this.#line(line);
      if (event) events.push(event);
    }
    this.#buffer = this.#buffer.slice(start);
    return events;
  }

  #line(line: string): SseEvent | undefined {
    if (line === "") return this.#dispatch();
    if (line.startsWith(":")) return undefined; // comment, used as keep-alive
    const colon = line.indexOf(":");
    const field = colon === -1 ? line : line.slice(0, colon);
    let value = colon === -1 ? "" : line.slice(colon + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "data") this.#data.push(value);
    else if (field === "event") this.#event = value;
    else if (field === "id" && !value.includes("\0")) this.#id = value;
    return undefined; // unknown fields are ignored
  }

  #dispatch(): SseEvent | undefined {
    if (this.#data.length === 0) {
      this.#event = "";
      return undefined;
    }
    const out: SseEvent = { event: this.#event || "message", data: this.#data.join("\n") };
    if (this.#id !== undefined) out.id = this.#id;
    this.#data = [];
    this.#event = "";
    return out;
  }
}
