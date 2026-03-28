import { fixtureStore } from "../fixtures/demoData";
import { apiBaseUrl, appMode } from "./env";
import type {
  AutomationOpportunity,
  CopilotExplanation,
  DataSource,
  OverviewPayload,
  OpportunityDetailView,
  ProcessDetailView,
  ProcessGraph,
  ProcessOverview,
  ResourceResult,
  ScoreComponents,
  StepInsight,
  VariantSummary,
  WorkflowDefinition,
  WorkflowStudioView,
} from "../types/contracts";

const REQUEST_TIMEOUT = 3000;

const processAliases: Record<string, string> = {
  "coding-activities": "coding",
  "youtrack-production": "production",
  "youtrack-support": "support",
  collector: "other",
  unassigned: "other",
};

const opportunityAliases: Record<string, string> = {
  "opp-comm-sharepoint": "status-triage-automation",
  "opp-youtrack-triage": "progress-sync",
  "opp-coding-copypaste": "review-brief-copilot",
  "opp-collector-search": "interruptions-monitor",
  "opp-youtrack-support": "interruptions-monitor",
  "opp-unassigned-excel": "interruptions-monitor",
};

type OverviewApi = {
  total_processes: number;
  total_cases: number;
  total_events: number;
  total_hours: number;
  total_users: number;
  observation_period: string;
  process_families: Array<{
    id: string;
    name: string;
    total_cases: number;
    total_events: number;
    total_hours: number;
    user_count: number;
    top_apps: string[];
  }>;
  top_applications: Array<{ name: string; hours: number }>;
};

type ProcessApi = {
  id: string;
  name: string;
  description?: string | null;
  total_cases: number;
  total_events: number;
  total_hours: number;
  active_hours: number;
  passive_hours: number;
  user_count: number;
  avg_case_duration_ms: number;
  top_apps: string[];
  top_steps: string[];
  variant_count: number;
  copy_paste_count: number;
  app_switch_count: number;
};

type VariantsApi = {
  process_id: string;
  process_name: string;
  total_cases: number;
  variant_count: number;
  happy_path?: string | null;
  variants: Array<{
    variant_id: string;
    steps: string[];
    frequency: number;
    avg_duration_ms: number;
    percentage: number;
  }>;
};

type GraphApi = {
  process_id: string;
  process_name: string;
  nodes: Array<{
    id: string;
    label: string;
    app?: string | null;
    avg_duration_ms?: number | null;
    frequency?: number | null;
    type: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
    frequency: number;
    label?: string | null;
  }>;
};

type StepApi = {
  step_name: string;
  app?: string | null;
  frequency: number;
  avg_duration_ms: number;
  total_duration_ms: number;
  user_count: number;
  click_count: number;
  text_entry_count: number;
  copy_count: number;
  paste_count: number;
  automation_signals: Array<{
    signal_type: string;
    description: string;
    severity: string;
    evidence?: string | null;
  }>;
};

type OpportunityApi = {
  id: string;
  process_id: string;
  process_name: string;
  title: string;
  description: string;
  score: number;
  score_components: ScoreComponents;
  recommendation: AutomationOpportunity["class"];
  affected_steps: string[];
  estimated_hours_saved?: number | null;
  evidence: string[];
};

type WorkflowApi = {
  process_id: string;
  process_name: string;
  title: string;
  description?: string | null;
  steps: Array<{
    id: string;
    type: "start" | "action" | "decision" | "end" | "parallel";
    label: string;
    description?: string | null;
    app?: string | null;
    next_steps: string[];
    condition?: string | null;
  }>;
  generated_by: string;
  source_variant?: string | null;
};

type ExplainApi = {
  question: string;
  answer: string;
  evidence: string[];
  generated_by: string;
  process_id?: string | null;
  confidence?: number | null;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const hasString = (value: unknown, key: string) =>
  isRecord(value) && typeof value[key] === "string";

const hasNumber = (value: unknown, key: string) =>
  isRecord(value) && typeof value[key] === "number";

const msToHours = (value: number) => Number((value / 3_600_000).toFixed(1));
const msToMinutes = (value: number) => Number((value / 60_000).toFixed(1));
const toPercent = (value: number) => Number((value * 100).toFixed(1));

const slugify = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

const resolveFixtureProcessId = (processId: string) =>
  processAliases[processId] ?? processId;

const resolveFixtureOpportunityId = (opportunityId: string) =>
  opportunityAliases[opportunityId] ?? opportunityId;

const extractFirstNumber = (value?: string | null) => {
  if (!value) {
    return null;
  }

  const match = value.match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
};

async function requestUnknown(path: string, init?: RequestInit): Promise<unknown | null> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as unknown;
  } catch {
    return null;
  } finally {
    window.clearTimeout(timeout);
  }
}

function asResult<T>(data: T, source: DataSource): ResourceResult<T> {
  return {
    data,
    source,
    mode: appMode,
  };
}

const isOverviewApi = (value: unknown): value is OverviewApi =>
  hasNumber(value, "total_processes") &&
  isRecord(value) &&
  Array.isArray(value.process_families);

const isProcessApi = (value: unknown): value is ProcessApi =>
  hasString(value, "id") &&
  hasString(value, "name") &&
  hasNumber(value, "total_cases");

const isProcessesApi = (value: unknown): value is ProcessApi[] =>
  Array.isArray(value) && value.every(isProcessApi);

const isVariantsApi = (value: unknown): value is VariantsApi =>
  hasString(value, "process_id") &&
  isRecord(value) &&
  Array.isArray(value.variants);

const isGraphApi = (value: unknown): value is GraphApi =>
  hasString(value, "process_id") &&
  isRecord(value) &&
  Array.isArray(value.nodes) &&
  Array.isArray(value.edges);

const isStepApi = (value: unknown): value is StepApi =>
  hasString(value, "step_name") &&
  hasNumber(value, "frequency") &&
  Array.isArray((value as StepApi).automation_signals);

const isStepsApi = (value: unknown): value is StepApi[] =>
  Array.isArray(value) && value.every(isStepApi);

const isOpportunityApi = (value: unknown): value is OpportunityApi =>
  hasString(value, "id") &&
  hasString(value, "process_id") &&
  hasString(value, "title");

const isOpportunitiesApi = (value: unknown): value is OpportunityApi[] =>
  Array.isArray(value) && value.every(isOpportunityApi);

const isWorkflowApi = (value: unknown): value is WorkflowApi =>
  hasString(value, "process_id") &&
  hasString(value, "title") &&
  isRecord(value) &&
  Array.isArray(value.steps);

const isExplainApi = (value: unknown): value is ExplainApi =>
  hasString(value, "question") &&
  hasString(value, "answer") &&
  isRecord(value) &&
  Array.isArray(value.evidence);

function genericNarrative(name: string, apps: string[]) {
  if (apps.length === 0) {
    return `${name} shows repeated work patterns with measurable handoffs and friction.`;
  }

  return `${name} repeatedly moves through ${apps.slice(0, 3).join(", ")}, making the handoff pattern easy to explain in a demo.`;
}

function mapProcess(process: ProcessApi, opportunities: OpportunityApi[] = []): ProcessOverview {
  const matchingOpportunity = opportunities
    .filter((opportunity) => opportunity.process_id === process.id)
    .sort((left, right) => right.score - left.score)[0];

  const contextSwitchRate = process.app_switch_count / Math.max(process.total_cases, 1);
  const copyPasteRate = process.copy_paste_count / Math.max(process.total_cases, 1);
  const manualEffortHours = Number(
    (process.active_hours * 0.24 + process.copy_paste_count / 120).toFixed(1),
  );

  return {
    id: process.id,
    name: process.name,
    family: process.name,
    description: process.description ?? `${process.name} process family`,
    totalCases: process.total_cases,
    avgCycleHours: msToHours(process.avg_case_duration_ms),
    manualEffortHours,
    automationPotential: matchingOpportunity
      ? toPercent(matchingOpportunity.score)
      : clamp(Math.round(40 + contextSwitchRate * 8 + copyPasteRate * 18), 25, 88),
    variantCount: process.variant_count,
    bottleneckStep: process.top_steps[0] ?? "Most frequent step",
    contextSwitchRate: Number(contextSwitchRate.toFixed(1)),
    copyPasteRate: Number(copyPasteRate.toFixed(1)),
    dominantApps: process.top_apps,
    narrative: process.description ?? genericNarrative(process.name, process.top_apps),
    unassigned: process.id === "unassigned",
  };
}

function mapOpportunity(opportunity: OpportunityApi): AutomationOpportunity {
  return {
    id: opportunity.id,
    processId: opportunity.process_id,
    title: opportunity.title,
    class: opportunity.recommendation,
    summary: opportunity.description,
    score: toPercent(opportunity.score),
    rank: 0,
    annualHours: Number(((opportunity.estimated_hours_saved ?? 0) * 52).toFixed(1)),
    confidence: clamp(1 - opportunity.score_components.coverage_penalty * 0.6, 0.45, 0.95),
    scoreComponents: {
      manual_effort: toPercent(opportunity.score_components.manual_effort),
      time_cost: toPercent(opportunity.score_components.time_cost),
      handoff: toPercent(opportunity.score_components.handoff),
      repetition: toPercent(opportunity.score_components.repetition),
      variance: toPercent(opportunity.score_components.variance),
      coverage_penalty: toPercent(opportunity.score_components.coverage_penalty),
    },
    evidence: {
      bottleneck: opportunity.evidence[0] ?? "Repeated high-friction work is visible in the process.",
      contextSwitch:
        opportunity.evidence[1] ?? "Users bounce across tools to complete the same unit of work.",
      copyPaste:
        opportunity.evidence[2] ?? "Cross-tool copying and manual carry-over remain visible.",
      manualEffort:
        opportunity.evidence[3] ?? "The path still depends on repeated manual assembly and routing.",
      variance:
        opportunity.evidence[4] ??
        `Recommendation stays in the ${opportunity.recommendation} class to respect process variability.`,
    },
    primarySteps: opportunity.affected_steps,
    workflowId: `workflow-${opportunity.id}`,
    recommendedOutcome:
      opportunity.recommendation === "Assistive copilot"
        ? "Use a copilot to draft or summarize, with a human still approving the result."
        : opportunity.recommendation === "Monitor only"
          ? "Keep this process visible and measurable before investing in heavier automation."
          : "Use workflow and integration steps to remove repeated handoffs and manual transfer work.",
  };
}

function rankOpportunities(opportunities: OpportunityApi[]): AutomationOpportunity[] {
  return opportunities
    .map(mapOpportunity)
    .sort((left, right) => right.score - left.score)
    .map((opportunity, index) => ({
      ...opportunity,
      rank: index + 1,
    }));
}

function mapVariants(payload: VariantsApi): VariantSummary[] {
  return payload.variants.map((variant, index) => ({
    id: variant.variant_id,
    processId: payload.process_id,
    label:
      index === 0
        ? "Happy path"
        : variant.steps.slice(0, 3).join(" -> "),
    share: Number((variant.percentage / 100).toFixed(3)),
    cases: variant.frequency,
    avgCycleHours: msToHours(variant.avg_duration_ms),
    medianTouches: variant.steps.length,
    dominantTools: variant.steps.slice(0, 3),
    automationFit:
      variant.percentage >= 20 ? "High" : variant.percentage >= 8 ? "Medium" : "Low",
    narrative: `Observed ${variant.frequency.toLocaleString()} times across ${variant.steps.length} visible steps.`,
  }));
}

function mapGraph(payload: GraphApi): ProcessGraph {
  const sortedNodes = [...payload.nodes].sort((left, right) => {
    if (left.type === "start") {
      return -1;
    }

    if (right.type === "start") {
      return 1;
    }

    if (left.type === "end") {
      return 1;
    }

    if (right.type === "end") {
      return -1;
    }

    return (right.frequency ?? 0) - (left.frequency ?? 0);
  });

  const maxFrequency = Math.max(
    1,
    ...sortedNodes.map((node) => node.frequency ?? 1),
    ...payload.edges.map((edge) => edge.frequency),
  );

  const nodes = sortedNodes.map((node, index) => ({
    id: node.id,
    label: node.label,
    tier: (
      node.type === "start"
        ? "start"
        : node.type === "end"
          ? "end"
          : node.type === "decision"
            ? "decision"
            : "task"
    ) as "start" | "end" | "decision" | "task",
    x: 10 + index * (78 / Math.max(sortedNodes.length - 1, 1)),
    y: node.type === "decision" ? 18 : index % 2 === 0 ? 30 : 26,
    emphasis: Math.round(((node.frequency ?? 1) / maxFrequency) * 100),
  }));

  const edges = payload.edges.map((edge) => ({
    source: edge.source,
    target: edge.target,
    weight: Math.round((edge.frequency / maxFrequency) * 100),
    label: edge.label ?? undefined,
  }));

  return {
    processId: payload.process_id,
    nodes,
    edges,
  };
}

function signalSeverity(signal: StepApi["automation_signals"][number] | undefined) {
  if (!signal) {
    return 0;
  }

  switch (signal.severity) {
    case "high":
      return 82;
    case "medium":
      return 56;
    default:
      return 28;
  }
}

function mapSteps(processId: string, steps: StepApi[]): StepInsight[] {
  return steps.map((step, index) => {
    const appSwitchSignal = step.automation_signals.find(
      (signal) => signal.signal_type === "app_switch",
    );
    const copySignal = step.automation_signals.find(
      (signal) => signal.signal_type === "copy_paste",
    );
    const durationSignal = step.automation_signals.find(
      (signal) => signal.signal_type === "high_duration",
    );
    const manualSignal = step.automation_signals.find(
      (signal) => signal.signal_type === "manual_entry",
    );

    const contextSwitches = appSwitchSignal
      ? Math.max(
          1,
          Math.round(
            (extractFirstNumber(appSwitchSignal.evidence) ?? step.click_count / 10) /
              Math.max(step.frequency, 1),
          ),
        )
      : Math.max(1, Math.round(step.click_count / Math.max(step.frequency, 1) / 2));

    const copyPasteSignals = Math.max(
      0,
      Math.round((step.copy_count + step.paste_count) / Math.max(step.frequency, 1)),
    );

    return {
      id: `${processId}-${slugify(step.step_name)}`,
      processId,
      name: step.step_name,
      order: index + 1,
      avgDurationMinutes: msToMinutes(step.avg_duration_ms),
      waitMinutes: Number((msToMinutes(step.avg_duration_ms) * 0.35).toFixed(1)),
      handoffRisk: Math.max(
        signalSeverity(appSwitchSignal),
        signalSeverity(copySignal),
        signalSeverity(durationSignal),
      ),
      contextSwitches,
      copyPasteSignals,
      manualTouches: Math.max(
        1,
        Math.round((step.click_count + step.text_entry_count) / Math.max(step.frequency, 1)),
      ),
      apps: step.app ? [step.app] : ["Unknown"],
      evidence:
        step.automation_signals.length > 0
          ? step.automation_signals.map((signal) => signal.description)
          : [
              manualSignal?.description ??
                `${step.step_name} appears repeatedly enough to keep in the automation evidence panel.`,
            ],
      nodeType:
        index === 0 ? "start" : index === steps.length - 1 ? "end" : "task",
    };
  });
}

function nextActionsFor(opportunity: AutomationOpportunity): string[] {
  switch (opportunity.class) {
    case "RPA/Integration":
      return [
        "Freeze the source fields and handoff point for the integration.",
        "Prototype the connector with one stable happy path first.",
        "Keep exception handling visible instead of burying it in background logic.",
      ];
    case "Assistive copilot":
      return [
        "Define the evidence bundle the copilot must expose.",
        "Keep human approval in the loop before anything is sent outward.",
        "Measure edit distance so the team can judge whether the assist is really saving time.",
      ];
    case "Monitor only":
      return [
        "Improve naming and ownership around this process family first.",
        "Track growth and stability before promising automation value.",
        "Use the signal to choose the next fixture or mining pass.",
      ];
    default:
      return [
        "Start with the most frequent happy path.",
        "Add a clear exception branch for missing context or stale evidence.",
        "Log which source signals were used so the workflow stays explainable.",
      ];
  }
}

function mapWorkflow(
  opportunity: AutomationOpportunity,
  payload: WorkflowApi,
): WorkflowDefinition {
  return {
    id: `workflow-${opportunity.id}`,
    opportunityId: opportunity.id,
    processId: payload.process_id,
    title: payload.title,
    summary: payload.description ?? `${payload.process_name} workflow draft`,
    trigger:
      payload.steps.find((step) => step.type === "start")?.description ??
      `Workflow starts from the ${payload.process_name} happy path.`,
    systems: Array.from(
      new Set(payload.steps.map((step) => step.app).filter(Boolean)),
    ) as string[],
    steps: payload.steps.map((step) => ({
      id: step.id,
      name: step.label,
      type:
        step.type === "start"
          ? "trigger"
          : step.type === "end"
            ? "output"
            : step.type === "decision"
              ? "decision"
              : "action",
      system: step.app ?? "Workflow engine",
      description:
        step.description ??
        (step.condition
          ? `Branch when ${step.condition}.`
          : `Proceed to ${step.next_steps.join(", ") || "completion"}.`),
    })),
    guardrails: [
      `Generated by ${payload.generated_by}.`,
      payload.source_variant
        ? `Based on source variant ${payload.source_variant}.`
        : "Based on the most representative path available.",
      "Keep the exception path explicit before automating the whole flow.",
    ],
    exportPayload: payload as unknown as Record<string, unknown>,
  };
}

function mapExplanation(
  opportunity: AutomationOpportunity,
  payload: ExplainApi,
): CopilotExplanation {
  return {
    id: `explain-${opportunity.id}`,
    opportunityId: opportunity.id,
    headline: payload.answer,
    reasoning: payload.evidence.length > 0 ? payload.evidence : [payload.answer],
    recommendedClass: opportunity.class,
    nextActions: nextActionsFor(opportunity),
    fallback: payload.generated_by !== "llm",
  };
}

export async function getOverview(): Promise<ResourceResult<OverviewPayload>> {
  if (appMode !== "live") {
    return asResult(fixtureStore.overview, "fixture");
  }

  const [overviewRaw, processesRaw, opportunitiesRaw] = await Promise.all([
    requestUnknown("/overview"),
    requestUnknown("/processes"),
    requestUnknown("/opportunities"),
  ]);

  if (!isOverviewApi(overviewRaw)) {
    return asResult(fixtureStore.overview, "fixture");
  }

  const liveOpportunities = isOpportunitiesApi(opportunitiesRaw)
    ? rankOpportunities(opportunitiesRaw)
    : fixtureStore.opportunities;
  const processLookup = new Map(
    (isProcessesApi(processesRaw) ? processesRaw.map((process) => mapProcess(process, opportunitiesRaw as OpportunityApi[])) : fixtureStore.processes).map(
      (process) => [process.id, process],
    ),
  );

  const families = overviewRaw.process_families.map((summary) => {
    const detailed = processLookup.get(summary.id);
    if (detailed) {
      return {
        ...detailed,
        totalCases: summary.total_cases,
        dominantApps: summary.top_apps,
      };
    }

    return {
      id: summary.id,
      name: summary.name,
      family: summary.name,
      description: `${summary.name} process family`,
      totalCases: summary.total_cases,
      avgCycleHours: Number((summary.total_hours / Math.max(summary.total_cases, 1)).toFixed(1)),
      manualEffortHours: Number((summary.total_hours * 0.18).toFixed(1)),
      automationPotential: 55,
      variantCount: 0,
      bottleneckStep: "Observed high-volume flow",
      contextSwitchRate: 0,
      copyPasteRate: 0,
      dominantApps: summary.top_apps,
      narrative: genericNarrative(summary.name, summary.top_apps),
      unassigned: summary.id === "unassigned",
    };
  });

  return asResult(
    {
      mode: "live",
      refreshLabel: overviewRaw.observation_period,
      guidedProcessId: families[0]?.id ?? fixtureStore.overview.guidedProcessId,
      guidedOpportunityId:
        liveOpportunities[0]?.id ?? fixtureStore.overview.guidedOpportunityId,
      guidedWorkflowId:
        liveOpportunities[0]?.workflowId ?? fixtureStore.overview.guidedWorkflowId,
      measuredUsers: overviewRaw.total_users,
      expectedUsers: 96,
      totalTrackedHours: overviewRaw.total_hours,
      opportunityHours: liveOpportunities
        .slice(0, 3)
        .reduce((sum, opportunity) => sum + opportunity.annualHours, 0),
      averageManualLoad:
        liveOpportunities.length > 0
          ? Number(
              (
                liveOpportunities.reduce(
                  (sum, opportunity) => sum + opportunity.scoreComponents.manual_effort,
                  0,
                ) / liveOpportunities.length
              ).toFixed(1),
            )
          : 60,
      processCoverage: clamp(overviewRaw.total_users / 96, 0, 1),
      families,
      topOpportunities: liveOpportunities.slice(0, 3),
    },
    "live",
  );
}

export async function getProcesses(): Promise<ResourceResult<ProcessOverview[]>> {
  if (appMode !== "live") {
    return asResult(fixtureStore.processes, "fixture");
  }

  const [processesRaw, opportunitiesRaw] = await Promise.all([
    requestUnknown("/processes"),
    requestUnknown("/opportunities"),
  ]);

  if (!isProcessesApi(processesRaw)) {
    return asResult(fixtureStore.processes, "fixture");
  }

  const mapped = processesRaw.map((process) =>
    mapProcess(process, isOpportunitiesApi(opportunitiesRaw) ? opportunitiesRaw : []),
  );
  return asResult(mapped, "live");
}

export async function getVariants(
  processId: string,
): Promise<ResourceResult<VariantSummary[]>> {
  const fixtureProcessId = resolveFixtureProcessId(processId);

  if (appMode !== "live") {
    return asResult(fixtureStore.variants[fixtureProcessId] ?? [], "fixture");
  }

  const payload = await requestUnknown(`/processes/${processId}/variants`);
  if (!isVariantsApi(payload)) {
    return asResult(fixtureStore.variants[fixtureProcessId] ?? [], "fixture");
  }

  return asResult(mapVariants(payload), "live");
}

export async function getProcessGraph(
  processId: string,
): Promise<ResourceResult<ProcessGraph>> {
  const fixtureProcessId = resolveFixtureProcessId(processId);

  if (appMode !== "live") {
    return asResult(fixtureStore.graphs[fixtureProcessId], "fixture");
  }

  const payload = await requestUnknown(`/processes/${processId}/graph`);
  if (!isGraphApi(payload)) {
    return asResult(fixtureStore.graphs[fixtureProcessId], "fixture");
  }

  return asResult(mapGraph(payload), "live");
}

export async function getStepInsights(
  processId: string,
): Promise<ResourceResult<StepInsight[]>> {
  const fixtureProcessId = resolveFixtureProcessId(processId);

  if (appMode !== "live") {
    return asResult(fixtureStore.steps[fixtureProcessId] ?? [], "fixture");
  }

  const payload = await requestUnknown(`/processes/${processId}/steps`);
  if (!isStepsApi(payload)) {
    return asResult(fixtureStore.steps[fixtureProcessId] ?? [], "fixture");
  }

  return asResult(mapSteps(processId, payload), "live");
}

export async function getOpportunities(): Promise<
  ResourceResult<AutomationOpportunity[]>
> {
  if (appMode !== "live") {
    return asResult(fixtureStore.opportunities, "fixture");
  }

  const payload = await requestUnknown("/opportunities");
  if (!isOpportunitiesApi(payload)) {
    return asResult(fixtureStore.opportunities, "fixture");
  }

  return asResult(rankOpportunities(payload), "live");
}

const resolveSource = (...sources: DataSource[]): DataSource =>
  sources.every((source) => source === "live") ? "live" : "fixture";

export async function getProcessDetail(
  processId: string,
): Promise<ResourceResult<ProcessDetailView>> {
  const fixtureProcessId = resolveFixtureProcessId(processId);
  const [processes, variants, graph, steps] = await Promise.all([
    getProcesses(),
    getVariants(processId),
    getProcessGraph(processId),
    getStepInsights(processId),
  ]);

  const process =
    processes.data.find((candidate) => candidate.id === processId) ??
    fixtureStore.processes.find((candidate) => candidate.id === fixtureProcessId);

  if (!process) {
    throw new Error("Process not found");
  }

  return {
    data: {
      process,
      variants: variants.data,
      graph: graph.data,
      steps: steps.data,
    },
    source: resolveSource(
      processes.source,
      variants.source,
      graph.source,
      steps.source,
    ),
    mode: appMode,
  };
}

export async function getOpportunityDetail(
  opportunityId: string,
): Promise<ResourceResult<OpportunityDetailView>> {
  const fixtureOpportunityId = resolveFixtureOpportunityId(opportunityId);
  const [opportunities, processes] = await Promise.all([
    getOpportunities(),
    getProcesses(),
  ]);

  const opportunity =
    opportunities.data.find((candidate) => candidate.id === opportunityId) ??
    fixtureStore.opportunities.find(
      (candidate) => candidate.id === fixtureOpportunityId,
    );

  if (!opportunity) {
    throw new Error("Opportunity not found");
  }

  const process =
    processes.data.find((candidate) => candidate.id === opportunity.processId) ??
    fixtureStore.processes.find((candidate) => candidate.id === opportunity.processId);

  if (!process) {
    throw new Error("Process not found");
  }

  if (appMode !== "live") {
    return {
      data: {
        opportunity,
        process,
        explanation: fixtureStore.explanations[fixtureOpportunityId],
      },
      source: "fixture",
      mode: appMode,
    };
  }

  const explainPayload = await requestUnknown("/copilot/explain", {
    method: "POST",
    body: JSON.stringify({
      context: opportunity.processId,
      question: `Why is ${opportunity.title} a good automation candidate?`,
      include_evidence: true,
    }),
  });

  const explanation = isExplainApi(explainPayload)
    ? mapExplanation(opportunity, explainPayload)
    : fixtureStore.explanations[fixtureOpportunityId];

  return {
    data: {
      opportunity,
      process,
      explanation,
    },
    source: isExplainApi(explainPayload)
      ? resolveSource(opportunities.source, processes.source, "live")
      : resolveSource(opportunities.source, processes.source, "fixture"),
    mode: appMode,
  };
}

export async function getWorkflowStudio(
  opportunityId: string,
): Promise<ResourceResult<WorkflowStudioView>> {
  const fixtureOpportunityId = resolveFixtureOpportunityId(opportunityId);
  const opportunityView = await getOpportunityDetail(opportunityId);

  if (appMode !== "live") {
    return {
      data: {
        workflow: fixtureStore.workflows[fixtureOpportunityId],
        opportunity: opportunityView.data.opportunity,
        process: opportunityView.data.process,
        explanation: opportunityView.data.explanation,
      },
      source: "fixture",
      mode: appMode,
    };
  }

  const workflowPayload = await requestUnknown("/workflow/generate", {
    method: "POST",
    body: JSON.stringify({
      process_id: opportunityView.data.opportunity.processId,
      variant_id: null,
      include_descriptions: true,
    }),
  });

  const workflow = isWorkflowApi(workflowPayload)
    ? mapWorkflow(opportunityView.data.opportunity, workflowPayload)
    : fixtureStore.workflows[fixtureOpportunityId];

  return {
    data: {
      workflow,
      opportunity: opportunityView.data.opportunity,
      process: opportunityView.data.process,
      explanation: opportunityView.data.explanation,
    },
    source: isWorkflowApi(workflowPayload)
      ? resolveSource(opportunityView.source, "live")
      : resolveSource(opportunityView.source, "fixture"),
    mode: appMode,
  };
}
