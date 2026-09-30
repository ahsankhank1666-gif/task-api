import { NextResponse } from "next/server";
import { inngest } from "@/lib/inngest/client";

export async function POST(req: Request) {
  try {
    const { nodes, edges } = await req.json();

    // Send execution event to Inngest
    await inngest.send({
      name: "workflow.execute",
      data: { nodes, edges },
    });

    return NextResponse.json({ success: true });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Internal Server Error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}