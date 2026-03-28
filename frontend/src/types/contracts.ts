export type AppMode = "fixture" | "live";
export type DataSource = "fixture" | "live";

export type OpportunityClass =
  | "RPA/Integration"
  | "Workflow automation"
  | "Assistive copilot"
  | "Monitor only";

export interface ProcessOverview {
  id: string;
  name: string;
  family: string;
  description: string;
  totalCases: number;
  avgCycleHours: number;
  manualEffortHours: number;
  automationPotential: number;
  variantCount: number;
  bottleneckStep: string;
  contextSwitchRate: number;
  copyPasteRate: number;
  dominantApps: string[];
  narrative: string;
  unassigned?: boolean;
}

export interface VariantSummary {
  id: string;
  processId: string;
  label: string;
  share: number;
  cases: number;
  avgCycleHours: number;
  medianTouches: number;
  dominantTools: string[];
  automationFit: "High" | "Medium" | "Low";
  narrative: string;
}

export interface StepInsight {
  id: string;
  processId: string;
  name: string;
  order: number;
  avgDurationMinutes: number;
  waitMinutes: number;
  handoffRisk: number;
  contextSwitches: number;
  copyPasteSignals: number;
  manualTouches: number;
  apps: string[];
  evidence: string[];
  nodeType: "start" | "task" | "decision" | "end";
}

export interface ScoreComponents {
  manual_effort: number;
  time_cost: number;
  handoff: number;
  repetition: number;
  variance: number;
  coverage_penalty: number;
}

export interface AutomationOpportunity {
  id: string;
  processId: string;
  title: string;
  class: OpportunityClass;
  summary: string;
  score: number;
  rank: number;
  annualHours: number;
  confidence: number;
  scoreComponents: ScoreComponents;
  evidence: {
    bottleneck: string;
    contextSwitch: string;
    copyPaste: string;
    manualEffort: string;
    variance: string;
  };
  primarySteps: string[];
  workflowId: string;
  recommendedOutcome: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: "trigger" | "action" | "decision" | "human_review" | "output";
  system: string;
  description: string;
}

export interface WorkflowDefinition {
  id: string;
  opportunityId: string;
  processId: string;
  title: string;
  summary: string;
  trigger: string;
  systems: string[];
  steps: WorkflowStep[];
  guardrails: string[];
  exportPayload: Record<string, unknown>;
}

export interface CopilotExplanation {
  id: string;
  opportunityId: string;
  headline: string;
  reasoning: string[];
  recommendedClass: OpportunityClass;
  nextActions: string[];
  fallback: boolean;
}

export interface GraphNode {
  id: string;
  label: string;
  tier: "start" | "task" | "decision" | "end";
  x: number;
  y: number;
  emphasis: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  label?: string;
}

export interface ProcessGraph {
  processId: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface OverviewPayload {
  mode: AppMode;
  refreshLabel: string;
  guidedProcessId: string;
  guidedOpportunityId: string;
  guidedWorkflowId: string;
  measuredUsers: number;
  expectedUsers: number;
  totalTrackedHours: number;
  opportunityHours: number;
  averageManualLoad: number;
  processCoverage: number;
  families: ProcessOverview[];
  topOpportunities: AutomationOpportunity[];
}

export interface ProcessDetailView {
  process: ProcessOverview;
  variants: VariantSummary[];
  graph: ProcessGraph;
  steps: StepInsight[];
}

export interface OpportunityDetailView {
  opportunity: AutomationOpportunity;
  process: ProcessOverview;
  explanation: CopilotExplanation;
}

export interface WorkflowStudioView {
  workflow: WorkflowDefinition;
  opportunity: AutomationOpportunity;
  process: ProcessOverview;
  explanation: CopilotExplanation;
}

export interface ResourceResult<T> {
  data: T;
  source: DataSource;
  mode: AppMode;
}
