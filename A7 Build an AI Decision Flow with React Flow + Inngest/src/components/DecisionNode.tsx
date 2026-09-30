"use client";
import React, { memo } from "react";
import { Handle, Position, NodeProps, Node } from "@xyflow/react";
import { useWorkflowStore, DecisionNodeData } from "@/store/useWorkflowStore";

export const DecisionNode = memo(({ id, data }: NodeProps<Node<DecisionNodeData>>) => {
  const { updateNodePrompt, updateNodeLabel } = useWorkflowStore();

  const getStatusColor = () => {
    switch (data.status) {
      case "running":
        return "border-blue-500 bg-blue-50 shadow-blue-100";
      case "yes":
        return "border-green-500 bg-green-50 shadow-green-100";
      case "no":
        return "border-red-500 bg-red-50 shadow-red-100";
      case "error":
        return "border-amber-500 bg-amber-50 shadow-amber-100";
      default:
        return "border-slate-200 bg-white";
    }
  };

  return (
    <div
      className={`w-72 border-2 rounded-xl p-4 shadow-md transition-all ${getStatusColor()}`}
    >
      {/* Target Handle: Incoming connections */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-slate-500 border-2 border-white"
      />

      {/* Header / Node Label */}
      <div className="mb-2">
        <input
          type="text"
          value={data.label}
          onChange={(e) => updateNodeLabel(id, e.target.value)}
          className="font-bold text-slate-800 text-sm bg-transparent outline-none w-full border-b border-transparent focus:border-slate-300"
        />
      </div>

      {/* Decision Prompt Textarea */}
      <div className="mb-3">
        <label className="text-xs text-slate-500 font-medium block mb-1">
          AI Decision Prompt
        </label>
        <textarea
          value={data.prompt}
          onChange={(e) => updateNodePrompt(id, e.target.value)}
          rows={3}
          placeholder="Is this condition met?"
          className="w-full text-xs p-2 rounded-md border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-slate-400 resize-none"
        />
      </div>

      {/* Output Handles */}
      <div className="flex justify-between items-center pt-2 border-t border-slate-100 text-xs font-semibold">
        {/* YES Output */}
        <div className="relative flex items-center gap-1 text-green-600">
          <span>YES</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="yes"
            className="w-3 h-3 bg-green-500 border-2 border-white !left-3"
          />
        </div>

        {/* NO Output */}
        <div className="relative flex items-center gap-1 text-red-600">
          <span>NO</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="no"
            className="w-3 h-3 bg-red-500 border-2 border-white !left-auto !right-3"
          />
        </div>
      </div>
    </div>
  );
});

DecisionNode.displayName = "DecisionNode";