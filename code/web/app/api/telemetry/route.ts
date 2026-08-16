import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

export async function GET(request: NextRequest) {
  const upstream = await fetch(`${process.env.BACKEND_URL}/telemetry/gpu`, { headers: { authorization: `Bearer ${process.env.CLIENT_API_KEY}` }, cache: "no-store" });
  const body = await upstream.json();
  return NextResponse.json(body, { status: upstream.status });
}
