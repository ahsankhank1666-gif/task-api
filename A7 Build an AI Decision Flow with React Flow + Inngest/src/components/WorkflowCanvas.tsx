"use client";

import { useState, useRef } from "react";
import { ReactFlow, Controls, Background, NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useWorkflowStore } from "@/store/useWorkflowStore";
import { DecisionNode } from "./DecisionNode";

const nodeTypes: NodeTypes = {
  decisionNode: DecisionNode,
};

export default function WorkflowCanvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode, setFlow } =
    useWorkflowStore();
  const [isRunning, setIsRunning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleRunWorkflow = async () => {
    setIsRunning(true);
    try {
      const res = await fetch("/api/workflow/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nodes, edges }),
      });

      if (res.ok) {
        alert("Workflow triggered! Check Inngest Dev Server dashboard.");
      } else {
        alert("Failed to trigger workflow execution.");
      }
    } catch (err) {
      console.error(err);
      alert("Error starting workflow.");
    } finally {
      setIsRunning(false);
    }
  };

  // --- PHASE 4: JSON EXPORT ---
  const exportToJson = () => {
    const flow = { nodes, edges };
    const blob = new Blob([JSON.stringify(flow, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ai-workflow.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  // --- PHASE 4: JSON IMPORT ---
  const importFromJson = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const flow = JSON.parse(e.target?.result as string);
        if (flow.nodes && flow.edges) {
          setFlow(flow.nodes, flow.edges);
        } else {
          alert("Invalid workflow file format.");
        }
      } catch (err) {
        alert("Error parsing JSON file.");
      }
    };
    reader.readAsText(file);
    // Reset input so the same file can be uploaded again if needed
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="w-full h-[80vh] flex flex-col border rounded-xl shadow-sm bg-slate-50 overflow-hidden">
      <div className="p-3 bg-white border-b flex justify-between items-center">
        <div className="flex gap-2 items-center">
          <h2 className="font-semibold text-sm text-slate-700 mr-4">Workflow Canvas</h2>
          
          {/* Hidden File Input for Import */}
          <input 
            type="file" 
            accept=".json" 
            ref={fileInputRef} 
            onChange={importFromJson} 
            className="hidden" 
          />
          
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-1.5 bg-slate-100 text-slate-600 text-xs font-medium rounded-md hover:bg-slate-200 transition border"
          >
            📂 Load JSON
          </button>
          <button
            onClick={exportToJson}
            className="px-3 py-1.5 bg-slate-100 text-slate-600 text-xs font-medium rounded-md hover:bg-slate-200 transition border"
          >
            💾 Save JSON
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={addNode}
            type="button"
            className="px-3 py-1.5 bg-slate-800 text-white text-xs font-medium rounded-md hover:bg-slate-900 transition shadow-sm"
          >
            + Add Decision Node
          </button>
          <button
            onClick={handleRunWorkflow}
            disabled={isRunning}
            type="button"
            className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-md hover:bg-green-700 transition disabled:opacity-50 shadow-sm"
          >
            {isRunning ? "Starting..." : "▶ Run Workflow"}
          </button>
        </div>
      </div>

      <div className="flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}