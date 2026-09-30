# Visual AI Decision Workflow System

An interactive visual AI decision workflow engine built with **Next.js (App Router)**, **React Flow**, **Inngest**, and **OpenAI**. Each node represents an AI decision step that evaluates prompts in real-time and returns strict `YES` or `NO` dynamic branching logic.

---

## 🚀 Features

- **Interactive Workflow Builder:** Drag-and-drop node graph canvas powered by React Flow (`@xyflow/react`) and Zustand.
- **Dynamic AI Decision Nodes:** Prompt nodes configured with custom `YES` (green) and `NO` (red) handles and visual execution states.
- **Durable Orchestration:** Step-by-step workflow execution, retry handling, and status persistence powered by **Inngest**.
- **Strict LLM Output:** Integrated OpenAI GPT models forced to output binary decision branches (`YES` / `NO`).
- **Workflow Persistence:** Native JSON Export/Import functionality to save, share, and reload custom workflow blueprints.

---

## 🛠️ Tech Stack

- **Framework:** Next.js 15+ (App Router, TypeScript)
- **Visual Canvas:** React Flow (`@xyflow/react`)
- **State Management:** Zustand
- **Background Orchestration:** Inngest
- **AI SDK:** OpenAI API (`gpt-4o-mini`)
- **Styling:** Tailwind CSS

---

## ⚙️ Environment Variables

Create a `.env.local` file in the root folder with the following configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
INNGEST_DEV=1

📦 Getting Started
1. Install Dependencies
npm install

2. Start Next.js Development Server
npm run dev

The frontend will be running at http://localhost:3000.

3. Start Inngest Local Dev Server
In a separate terminal tab, run:

npx inngest-cli@latest dev

The Inngest Dev Dashboard will be accessible at http://localhost:8288.

📖 System Architecture & Execution Flow
Graph Construction: The user builds a visual workflow on the React Flow canvas. The node graph state (nodes, edges, prompt data) is managed via a Zustand store.

Execution Trigger: Clicking ▶ Run Workflow sends the serialized graph JSON to /api/workflow/run.

Inngest Worker Queue: The Next.js API dispatches the workflow.execute event to Inngest.

Graph Traversal & Atomic Steps:

Inngest identifies the root decision node.

For each node, an atomic step.run() sends the prompt to OpenAI.

System instructions ensure OpenAI returns only YES or NO.

Inngest evaluates the decision, finds the matching outgoing edge (sourceHandle), and navigates to the next connected target node until the leaf node is reached.

