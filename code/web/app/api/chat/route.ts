import { NextRequest, NextResponse } from "next/server";
export async function POST(request: NextRequest) {
  const { message } = await request.json();
  if (typeof message !== "string" || !message.trim()) return NextResponse.json({error:"message required"},{status:400});
  const started = performance.now();
  const upstream = await fetch(`${process.env.BACKEND_URL}/v1/chat/completions`, {method:"POST", headers:{"content-type":"application/json",authorization:`Bearer ${process.env.CLIENT_API_KEY}`}, body:JSON.stringify({model:"aurorium",messages:[{role:"user",content:message}],temperature:0.7,max_tokens:256,chat_template_kwargs:{enable_thinking:false}})});
  const responseMs = Math.round(performance.now() - started);
  const body = await upstream.json();
  const usage = body.usage ?? {};
  const completionTokens = Number(usage.completion_tokens ?? 0);
  return NextResponse.json({
    text: body.choices?.[0]?.message?.content ?? body.error?.message ?? "Inference failed",
    metrics: upstream.ok ? {
      model: body.model ?? "aurorium",
      adapter: "aurorium",
      promptTokens: Number(usage.prompt_tokens ?? 0),
      completionTokens,
      totalTokens: Number(usage.total_tokens ?? 0),
      responseMs,
      tokensPerSecond: completionTokens && responseMs ? Math.round(completionTokens / (responseMs / 1000) * 10) / 10 : 0,
    } : undefined,
  },{status:upstream.status});
}
