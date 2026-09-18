// API client module for interacting with the Amica FastAPI backend.
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

export interface RepoMetadata {
  id: string;
  url: string;
  owner: string;
  name: string;
  description: string | null;
  default_branch: string;
  language: string | null;
  stars: number;
  open_issues_count: number;
  clone_path: string;
  file_count: number;
  status: string;
  error_message: string | null;
  has_readme: boolean;
  has_contributing: boolean;
  readme_content?: string | null;
  contributing_content?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IngestResponse {
  success: boolean;
  message: string;
  repository: RepoMetadata;
}

// Ingests a repository by its GitHub URL or shorthand and returns metadata.
export async function ingestRepository(
  url: string,
  forceRefresh: boolean = false
): Promise<IngestResponse> {
  const response = await fetch(`${BACKEND_URL}/api/repos/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url,
      force_refresh: forceRefresh,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `Server returned error (${response.status})`;
    throw new Error(message);
  }

  return response.json();
}

// Fetches the metadata and documentation of an ingested repository.
export async function getRepository(
  owner: string,
  repo: string
): Promise<RepoMetadata> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch repository");
  }

  return response.json();
}

// Fetches a list of recently ingested repositories.
export async function listRepositories(): Promise<RepoMetadata[]> {
  const response = await fetch(`${BACKEND_URL}/api/repos`);
  if (!response.ok) {
    return [];
  }
  return response.json();
}

export interface CodeSymbol {
  name: string;
  type: string;
  start_line: number;
  end_line: number;
  docstring?: string | null;
}

export interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  language: string;
  line_count: number;
  symbols: CodeSymbol[];
  in_degree: number;
  out_degree: number;
  centrality: number;
  cluster: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface TopCentralFile {
  file: string;
  score: number;
  in_degree: number;
  out_degree: number;
}

export interface GraphMetrics {
  total_nodes: number;
  total_edges: number;
  density: number;
  top_central_files: TopCentralFile[];
  clusters_count: number;
}

export interface GraphResponse {
  repo_id: string;
  metrics: GraphMetrics;
  nodes: GraphNode[];
  edges: GraphEdge[];
  updated_at: string;
}

// Initiates AST parsing and builds the NetworkX dependency graph for a repository.
export async function buildRepoGraph(
  owner: string,
  repo: string
): Promise<GraphResponse> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/graph/build`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to build dependency graph");
  }

  return response.json();
}

// Fetches the existing dependency graph for a repository if already computed.
export async function getRepoGraph(
  owner: string,
  repo: string
): Promise<GraphResponse | null> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/graph`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch dependency graph");
  }

  return response.json();
}

export interface FeatureItem {
  name: string;
  description: string;
  files: string[];
}

export interface ArchitectureFlow {
  component: string;
  role: string;
  central_file: string;
  connections: string[];
}

export interface RepoUnderstanding {
  repo_id: string;
  overview: string;
  architecture_summary: string;
  feature_map: FeatureItem[];
  flows: ArchitectureFlow[];
  model_used: string;
  is_fallback: boolean;
  digest?: string | null;
  created_at: string;
}

// Generates plain-English repository understanding from digest context.
export async function generateRepoUnderstanding(
  owner: string,
  repo: string
): Promise<RepoUnderstanding> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/understand`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate repository understanding");
  }

  return response.json();
}

// Fetches cached repository understanding if already computed.
export async function getRepoUnderstanding(
  owner: string,
  repo: string
): Promise<RepoUnderstanding | null> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/understand`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch repository understanding");
  }

  return response.json();
}

export interface FileContentResponse {
  path: string;
  language: string;
  line_count: number;
  content: string;
  is_truncated: boolean;
  error?: string | null;
}

// Fetches the source code content of a file in the repository workspace.
export async function fetchFileContent(
  owner: string,
  repo: string,
  path: string
): Promise<FileContentResponse> {
  const params = new URLSearchParams({ path });
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/files/content?${params.toString()}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to load file content");
  }
  return response.json();
}

export interface IssueLabel {
  name: string;
  color: string;
  description?: string | null;
}

export interface IssueSummary {
  id: string;
  number: number;
  title: string;
  body?: string;
  state: string;
  author: string;
  labels: IssueLabel[];
  comments_count: number;
  html_url: string;
  created_at: string;
}

export interface RelevantFileItem {
  file: string;
  reason: string;
  symbols_to_inspect: string[];
}

export interface IssueExplanation {
  issue_id: string;
  repo_id: string;
  issue_number: number;
  plain_english_summary: string;
  real_world_analogy: string;
  relevant_files: RelevantFileItem[];
  implementation_steps: string[];
  estimated_complexity: string;
  model_used: string;
  is_fallback: boolean;
  created_at: string;
}

export interface IssueListResponse {
  repo_id: string;
  total_count: number;
  available_labels: IssueLabel[];
  issues: IssueSummary[];
}

// Fetches open issues for a repository with optional label filtering.
export async function fetchRepoIssues(
  owner: string,
  repo: string,
  label?: string,
  forceRefresh: boolean = false,
  state: string = "open"
): Promise<IssueListResponse> {
  const params = new URLSearchParams();
  if (label && label.toLowerCase() !== "all") {
    params.set("label", label);
  }
  if (forceRefresh) {
    params.set("force_refresh", "true");
  }
  if (state) {
    params.set("state", state);
  }

  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues${query}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to fetch issues");
  }
  return response.json();
}

// Generates or retrieves an on-demand plain-English explanation for a specific issue.
export async function explainIssue(
  owner: string,
  repo: string,
  issueNumber: number
): Promise<IssueExplanation> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/${issueNumber}/explain`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate issue explanation");
  }
  return response.json();
}

// Seeds a demo issue for testing when a repository has 0 open GitHub issues.
export async function seedDemoIssue(
  owner: string,
  repo: string
): Promise<IssueSummary> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/seed`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to seed demo issue");
  }
  return response.json();
}

export interface DiffStats {
  line_count: number;
  files_touched: string[];
  validation_passed: boolean;
  pre_routed?: boolean;
  reason?: string;
}

export interface PullRequestResult {
  status: string;
  action: string;
  pr_url: string;
  pr_number: number;
  branch: string;
  fork_ref: string;
}

export interface PlanArtifact {
  title: string;
  summary: string;
  steps: string[];
  estimated_risk: string;
  recommended_reviewers: string[];
  issue_context?: string;
  problem_statement?: string;
  affected_modules?: string[];
  quality_assurance?: string[];
  markdown_content?: string;
  diff_metrics?: {
    line_count: number;
    num_files: number;
    threshold_lines: number;
    threshold_files: number;
  };
}

export interface AgentHandoffResponse {
  status: "success" | "declined" | "error";
  authorized: boolean;
  repo_id?: string;
  issue_number?: number;
  fork?: {
    fork_ref: string;
    fork_url: string;
    provisioned: boolean;
  };
  diff?: string;
  diff_stats?: DiffStats;
  decision?: "pr" | "plan";
  pr?: PullRequestResult | null;
  plan?: PlanArtifact | null;
  message: string;
  created_at?: string;
  updated_at?: string;
}

export interface AgentStatusResponse {
  status: string;
  agent: string;
  framework: string;
  sdk: string;
  model: string;
  models?: {
    cheap: string;
    strong: string;
  };
  has_api_key: boolean;
  github?: {
    authenticated: boolean;
    user: string | null;
    limit: number;
    remaining: number;
    reset: number | null;
  };
  capabilities: string[];
}

// Retrieves cached agent handoff results for an issue if previously executed.
export async function getHandoffResult(
  owner: string,
  repo: string,
  issueNumber: number
): Promise<AgentHandoffResponse | null> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/${issueNumber}/handoff`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

// Executes the Google ADK Agent Handoff workflow for a specific issue.
export async function triggerAgentHandoff(

  owner: string,
  repo: string,
  issueNumber: number,
  optIn: boolean = true,
  userNotes?: string
): Promise<AgentHandoffResponse> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/${issueNumber}/handoff`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      opt_in: optIn,
      user_notes: userNotes || null,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to execute agent handoff");
  }

  return response.json();
}

// Publishes a verified code patch as a GitHub Pull Request after developer review.
export async function publishPullRequest(
  owner: string,
  repo: string,
  issueNumber: number,
  data?: { diff?: string; fork_ref?: string }
): Promise<{ status: string; action: string; pr: PullRequestResult; message: string }> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/${issueNumber}/publish-pr`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data || {}),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to publish Pull Request");
  }

  return response.json();
}

// Discards local workspace modifications and rolls back the temporary fix branch.
export async function rollbackHandoff(
  owner: string,
  repo: string,
  issueNumber: number
): Promise<{ status: string; repo_id: string; issue_number: number; message: string }> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/issues/${issueNumber}/rollback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to rollback handoff changes");
  }

  return response.json();
}

// Fetches Google ADK agent system status and model capabilities.
export async function getAgentStatus(): Promise<AgentStatusResponse> {
  const response = await fetch(`${BACKEND_URL}/api/agent/status`);
  if (!response.ok) {
    throw new Error("Failed to fetch agent status");
  }
  return response.json();
}

// Sends a message to the interactive Google ADK agent chat endpoint.
export async function chatWithAgent(
  message: string,
  sessionId?: string
): Promise<{ status: string; session_id: string; response: string }> {
  const response = await fetch(`${BACKEND_URL}/api/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to chat with agent");
  }

  return response.json();
}


// ========================================
// CAPSULE System API Functions
// ========================================

export interface CapsuleMetadata {
  capsule_id: string;
  project_name: string;
  project_repo?: string;
  version: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  total_components: number;
  total_tasks: number;
  total_decisions: number;
}

export interface CodePointer {
  file_path: string;
  line_start?: number;
  line_end?: number;
  function_name?: string;
  class_name?: string;
  commit_hash?: string;
}

export interface ComponentContract {
  component_id: string;
  component_type: string;
  name: string;
  inputs: string[];
  outputs: string[];
  dependencies: string[];
  guarantees: string[];
  constraints: string[];
  code_pointer: CodePointer;
}

export interface StateRegistryEntry {
  task_id: string;
  task_description: string;
  state: "done" | "in_progress" | "stubbed" | "blocked";
  current_attempt?: string;
  last_attempt?: string;
  blockers: string[];
  progress_notes: string[];
  related_components: string[];
  created_at: string;
  updated_at: string;
}

export interface DecisionLogEntry {
  decision_id: string;
  title: string;
  context: string;
  decision: string;
  rationale: string;
  consequences: string[];
  alternatives_considered: string[];
  decided_at: string;
  decided_by?: string;
  status: string;
}

export interface ArchitectureGraph {
  nodes: any[];
  edges: any[];
  clusters: any[];
  centrality_metrics: Record<string, number>;
  community_structure: Record<string, string[]>;
}

export interface Capsule {
  metadata: CapsuleMetadata;
  project_intent: string;
  architecture: ArchitectureGraph;
  components: ComponentContract[];
  tech_stack: Record<string, string>;
  state_registry: StateRegistryEntry[];
  decisions: DecisionLogEntry[];
  known_issues: any[];
  code_index: Record<string, CodePointer>;
}

export interface CapsuleResponse {
  status: string;
  repository: { owner: string; name: string };
  capsule: Capsule;
  size_info: {
    total_components: number;
    total_tasks: number;
    total_decisions: number;
    total_issues: number;
  };
}

// Generates a CAPSULE for the specified repository
export async function generateCapsule(
  owner: string,
  repo: string,
  options: {
    regenerate?: boolean;
    include_subsystems?: string[];
  } = {}
): Promise<CapsuleResponse> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/capsule`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      regenerate: options.regenerate || false,
      include_subsystems: options.include_subsystems || null,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate CAPSULE");
  }

  return response.json();
}

// Retrieves existing CAPSULE for repository
export async function getCapsule(owner: string, repo: string): Promise<CapsuleResponse> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/capsule`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to retrieve CAPSULE");
  }

  return response.json();
}

// Updates the state registry in a repository's CAPSULE
export async function updateCapsuleState(
  owner: string,
  repo: string,
  taskUpdates: Array<{
    task_id: string;
    task_description?: string;
    state?: "done" | "in_progress" | "stubbed" | "blocked";
    current_attempt?: string;
    last_attempt?: string;
    blockers?: string[];
    progress_notes?: string[];
    related_components?: string[];
  }>
): Promise<{ status: string; message: string; updated_at: string }> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/capsule/state`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task_updates: taskUpdates,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to update CAPSULE state");
  }

  return response.json();
}

// Exports CAPSULE as JSON for manual paste into AI tools
export async function exportCapsuleJson(owner: string, repo: string): Promise<{
  status: string;
  format: string;
  size_bytes: number;
  capsule_json: string;
  usage_instructions: string[];
}> {
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/capsule/export`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to export CAPSULE");
  }

  return response.json();
}

// ========================================
// MCP Server API Functions
// ========================================

export interface MCPServerStatus {
  status: "running" | "stopped";
  tools: Array<{
    name: string;
    description: string;
  }>;
  cached_repos: string[];
}

// Starts the MCP server for AI tool integration
export async function startMCPServer(port: number = 3001): Promise<{
  status: string;
  port: number;
  tools: any[];
}> {
  const response = await fetch(`${BACKEND_URL}/api/mcp/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ port }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to start MCP server");
  }

  return response.json();
}

// Stops the MCP server
export async function stopMCPServer(): Promise<{ status: string; message: string }> {
  const response = await fetch(`${BACKEND_URL}/api/mcp/stop`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to stop MCP server");
  }

  return response.json();
}

// Gets MCP server status
export async function getMCPServerStatus(): Promise<MCPServerStatus> {
  const response = await fetch(`${BACKEND_URL}/api/mcp/status`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to get MCP server status");
  }

  return response.json();
}

// Retrieves specific code from repository (MCP tool)
export async function getCode(
  owner: string,
  repo: string,
  filePath: string,
  options: {
    line_start?: number;
    line_end?: number;
    function_name?: string;
  } = {}
): Promise<{
  status: string;
  code: {
    file_path: string;
    content: string;
    line_count: number;
    line_range: { start: number; end: number };
    encoding: string;
  };
}> {
  const params = new URLSearchParams({
    file_path: filePath,
    ...(options.line_start && { line_start: options.line_start.toString() }),
    ...(options.line_end && { line_end: options.line_end.toString() }),
    ...(options.function_name && { function_name: options.function_name }),
  });

  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/code?${params.toString()}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to retrieve code");
  }

  return response.json();
}

// Gets current task state registry from CAPSULE (MCP tool)
export async function getStateRegistry(
  owner: string,
  repo: string,
  taskFilter: "all" | "in_progress" | "blocked" = "all"
): Promise<{
  status: string;
  state_registry: {
    repo_id: string;
    task_filter: string;
    total_tasks: number;
    filtered_count: number;
    tasks: StateRegistryEntry[];
    state_summary: Record<string, number>;
  };
}> {
  const params = new URLSearchParams({ task_filter: taskFilter });
  const response = await fetch(`${BACKEND_URL}/api/repos/${owner}/${repo}/state-registry?${params.toString()}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to retrieve state registry");
  }

  return response.json();
}