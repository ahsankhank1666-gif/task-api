import { create } from "zustand";
import {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
} from "@xyflow/react";

export interface DecisionNodeData {
  label: string;
  prompt: string;
  status?: "idle" | "running" | "yes" | "no" | "error";
  [key: string]: unknown;
}

interface WorkflowState {
  nodes: Node<DecisionNodeData>[];
  edges: Edge[];
  onNodesChange: (changes: NodeChange<Node<DecisionNodeData>>[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: () => void;
  updateNodePrompt: (id: string, prompt: string) => void;
  updateNodeLabel: (id: string, label: string) => void;
  setFlow: (nodes: Node<DecisionNodeData>[], edges: Edge[]) => void; 
}

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [
    {
      id: "node-1",
      type: "decisionNode",
      position: { x: 250, y: 100 },
      data: {
        label: "Check Request Type",
        prompt: "Is this a customer support request?",
        status: "idle",
      },
    },
  ],
  edges: [],

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    // Custom edge styling depending on whether source handle is YES or NO
    const isYes = connection.sourceHandle === "yes";
    const newEdge: Edge = {
      ...connection,
      id: `e-${connection.source}-${connection.target}-${connection.sourceHandle}`,
      animated: true,
      label: isYes ? "YES" : "NO",
      style: {
        stroke: isYes ? "#22c55e" : "#ef4444",
        strokeWidth: 2,
      },
      labelStyle: {
        fill: isYes ? "#15803d" : "#b91c1c",
        fontWeight: 700,
      },
    };
    set({
      edges: addEdge(newEdge, get().edges),
    });
  },

  addNode: () => {
    const id = `node-${Date.now()}`;
    const newNode: Node<DecisionNodeData> = {
      id,
      type: "decisionNode",
      position: {
        x: Math.random() * 300 + 100,
        y: Math.random() * 300 + 100,
      },
      data: {
        label: `Decision Node ${get().nodes.length + 1}`,
        prompt: "Enter your prompt here...",
        status: "idle",
      },
    };
    set({ nodes: [...get().nodes, newNode] });
  },

  updateNodePrompt: (id, prompt) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, prompt } } : node
      ),
    });
  },

  updateNodeLabel: (id, label) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, label } } : node
      ),
    });
  },

  setFlow: (nodes, edges) => {
    set({ nodes, edges });
  },
}));