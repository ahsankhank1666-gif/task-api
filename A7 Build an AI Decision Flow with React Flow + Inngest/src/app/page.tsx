import WorkflowCanvas from "@/components/WorkflowCanvas";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-slate-100">
      <div className="w-full max-w-6xl">
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">
            AI Decision Workflow Builder
          </h1>
          <p className="text-sm text-slate-600">
            Connect AI decision steps with dynamic YES/NO branching logic.
          </p>
        </header>
        <WorkflowCanvas />
      </div>
    </main>
  );
}