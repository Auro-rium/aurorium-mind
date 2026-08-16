"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Message = { id: string; role: "user" | "assistant"; content: string };

const starters = [
  "Map this decision using second-order effects and inversion.",
  "Stress-test this plan as a game-theory problem.",
  "Reduce this idea to first principles, then find its weak link.",
];

function Mark() {
  return <span className="mark" aria-hidden="true"><i /><i /><i /></span>;
}

function ArrowUp() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6.5 10.5 12 5l5.5 5.5" /></svg>;
}

function Plus() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>;
}

function Spark() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 1.35 5.65L19 10l-5.65 1.35L12 17l-1.35-5.65L5 10l5.65-1.35L12 3Zm6.5 12 .55 2.45L21.5 18l-2.45.55L18.5 21l-.55-2.45L15.5 18l2.45-.55.55-2.45Z" /></svg>;
}

export default function Page() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("Inference staging");
  const textarea = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const element = textarea.current;
    if (!element) return;
    element.style.height = "0px";
    element.style.height = `${Math.min(element.scrollHeight, 176)}px`;
  }, [input]);

  async function send(event?: FormEvent, preset?: string) {
    event?.preventDefault();
    const message = (preset ?? input).trim();
    if (!message || busy) return;
    const user: Message = { id: crypto.randomUUID(), role: "user", content: message };
    setMessages((current) => [...current, user]);
    setInput("");
    setBusy(true);
    setNotice("Reasoning");
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.text ?? data.error ?? "Inference failed");
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", content: data.text ?? "No response returned." }]);
      setNotice("Connected");
    } catch (error) {
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", content: error instanceof Error ? error.message : "Inference endpoint unavailable." }]);
      setNotice("Inference staging");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="context-rail">
        <div className="brand"><Mark /><span>Aurorium <b>Mind</b></span></div>
        <button className="new-thread" onClick={() => { setMessages([]); setNotice("Inference staging"); }}><Plus /> New reasoning path</button>

        <section className="rail-section">
          <p className="eyebrow">System state</p>
          <div className="system-card">
            <div><span className="signal" /><span>{notice}</span></div>
            <small>Qwen 3.5 · QLoRA</small>
          </div>
        </section>

        <section className="rail-section model-card">
          <p className="eyebrow">Reasoning lens</p>
          <ul>
            <li>First principles</li><li>Second-order effects</li><li>Inversion</li><li>Systems thinking</li>
          </ul>
        </section>
        <div className="rail-foot">Private model endpoint<br /><span>Telemetry: metadata only</span></div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="mobile-brand"><Mark /><span>Aurorium Mind</span></div>
          <div className="session-title"><span className="muted">Session</span><strong>{messages.length ? "Reasoning in progress" : "New reasoning path"}</strong></div>
          <div className="top-status"><span className="signal" />{notice}</div>
        </header>

        <div className={`conversation ${messages.length ? "has-messages" : ""}`}>
          {messages.length === 0 ? (
            <section className="empty-state">
              <p className="eyebrow">Aurorium Mind</p>
              <h1>Think farther than<br />the obvious answer.</h1>
              <p className="intro">A personal reasoning environment for first principles, inversion, systems thinking, and pragmatic futures.</p>
              <div className="starter-grid">
                {starters.map((starter, index) => <button key={starter} onClick={() => send(undefined, starter)}><span>0{index + 1}</span>{starter}<ArrowUp /></button>)}
              </div>
            </section>
          ) : (
            <div className="message-stack">
              {messages.map((message) => <article className={`message ${message.role}`} key={message.id}>
                <div className="message-label">{message.role === "assistant" ? <><Mark /> Aurorium</> : "You"}</div>
                <div className="message-content">{message.content}</div>
              </article>)}
              {busy && <article className="message assistant typing"><div className="message-label"><Mark /> Aurorium</div><div className="dots"><i /><i /><i /></div></article>}
            </div>
          )}
        </div>

        <div className="composer-wrap">
          <form className="composer" onSubmit={send}>
            <textarea ref={textarea} value={input} onChange={(event) => setInput(event.target.value)} rows={1} placeholder="Ask for a deeper look…" aria-label="Message Aurorium Mind" />
            <div className="composer-footer"><span><Spark /> Reasoning mode</span><button type="submit" disabled={busy || !input.trim()} aria-label="Send message"><ArrowUp /></button></div>
          </form>
          <p className="composer-note">Enter to send · Shift + Enter for a new line</p>
        </div>
      </section>
    </main>
  );
}
