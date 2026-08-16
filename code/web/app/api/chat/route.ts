import { NextRequest, NextResponse } from "next/server";
export async function POST(request: NextRequest) {
  const { message } = await request.json();
  if (typeof message !== "string" || !message.trim()) return NextResponse.json({error:"message required"},{status:400});
  const upstream = await fetch(`${process.env.BACKEND_URL}/v1/chat/completions`, {method:"POST", headers:{"content-type":"application/json",authorization:`Bearer ${process.env.CLIENT_API_KEY}`}, body:JSON.stringify({model:"aurorium",messages:[{role:"user",content:message}],temperature:0.7})});
  const body = await upstream.json();
  return NextResponse.json({text:body.choices?.[0]?.message?.content ?? body.error?.message ?? "Inference failed"},{status:upstream.status});
}
