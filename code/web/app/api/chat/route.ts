import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

export async function POST(request: NextRequest) {
  const { message } = await request.json();
  if (typeof message !== "string" || !message.trim()) return NextResponse.json({ error: "message required" }, { status: 400 });
  const started = performance.now();
  const upstream = await fetch(`${process.env.BACKEND_URL}/v1/chat/completions`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${process.env.CLIENT_API_KEY}` },
    body: JSON.stringify({ model: "aurorium", messages: [{ role: "user", content: message }], temperature: 0.2, max_tokens: 512, stream: true, stream_options: { include_usage: true }, chat_template_kwargs: { enable_thinking: false } }),
  });
  if (!upstream.ok || !upstream.body) {
    const body = await upstream.text();
    return NextResponse.json({ error: body || "Inference failed" }, { status: upstream.status });
  }

  const reader = upstream.body.getReader();
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();
  let buffer = "";
  let firstByteMs: number | null = null;
  let usage: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number } = {};

  const stream = new ReadableStream<Uint8Array>({
    async pull(controller) {
      const { done, value } = await reader.read();
      if (done) {
        const responseMs = Math.round(performance.now() - started);
        const completionTokens = Number(usage.completion_tokens ?? 0);
        const ttftMs = firstByteMs ?? responseMs;
        const decodeMs = Math.max(responseMs - ttftMs, 1);
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ aurorium_metrics: { model: "aurorium", adapter: "aurorium", promptTokens: Number(usage.prompt_tokens ?? 0), completionTokens, totalTokens: Number(usage.total_tokens ?? 0), ttftMs, responseMs, tokensPerSecond: completionTokens ? Math.round(completionTokens / (decodeMs / 1000) * 10) / 10 : 0 } })}\n\n`));
        controller.close();
        return;
      }
      if (firstByteMs === null) firstByteMs = Math.round(performance.now() - started);
      const text = decoder.decode(value, { stream: true });
      buffer += text;
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const data = line.slice(5).trim();
        if (data === "[DONE]") continue;
        try {
          const parsed = JSON.parse(data);
          if (parsed.usage) usage = parsed.usage;
        } catch { /* incomplete or non-JSON SSE line */ }
      }
      controller.enqueue(value);
    },
    async cancel() { await reader.cancel(); },
  });
  return new Response(stream, { status: 200, headers: { "content-type": "text/event-stream; charset=utf-8", "cache-control": "no-cache, no-transform", connection: "keep-alive" } });
}
