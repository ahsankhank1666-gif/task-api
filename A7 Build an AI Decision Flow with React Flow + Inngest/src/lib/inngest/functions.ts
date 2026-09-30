import { inngest } from "./client";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "",
});

interface WorkflowNode {
  id: string;
  data: {
    label: string;
    prompt: string;
  };
}

interface WorkflowEdge {
  source: string;
  target: string;
  sourceHandle?: string;
}

interface WorkflowEventData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export const executeWorkflow = inngest.createFunction(
  {
    id: "execute-ai-workflow",
    triggers: [{ event: "workflow.execute" }],
  },
  async ({ event, step }) => {
    const data = event.data as unknown as WorkflowEventData;
    const nodes = data.nodes || [];
    const edges = data.edges || [];

    if (nodes.length === 0) {
      return { status: "error", message: "No nodes provided" };
    }

    const targetNodeIds = new Set(edges.map((e) => e.target));
    let currentNode: WorkflowNode | null =
      nodes.find((n) => !targetNodeIds.has(n.id)) || nodes[0] || null;

    const executionLog = [];

    while (currentNode) {
      const activeNode: WorkflowNode = currentNode;
      const promptText = activeNode.data.prompt;

      const decision = await step.run(
        `evaluate-node-${activeNode.id}`,
        async (): Promise<"YES" | "NO"> => {
          const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
              {
                role: "system",
                content:
                  "You are an AI decision engine. Analyze the prompt and respond ONLY with 'YES' or 'NO'. No punctuation or extra words.",
              },
              {
                role: "user",
                content: promptText,
              },
            ],
            temperature: 0,
          });

          const answer = response.choices[0]?.message?.content?.trim().toUpperCase();
          return answer === "YES" ? "YES" : "NO";
        }
      );

      executionLog.push({
        nodeId: activeNode.id,
        label: activeNode.data.label,
        prompt: activeNode.data.prompt,
        decision,
      });

      const matchingEdge = edges.find(
        (e) =>
          e.source === activeNode.id &&
          e.sourceHandle?.toLowerCase() === decision.toLowerCase()
      );

      if (matchingEdge) {
        currentNode = nodes.find((n) => n.id === matchingEdge.target) || null;
      } else {
        currentNode = null;
      }
    }

    return { status: "completed", logs: executionLog };
  }
);