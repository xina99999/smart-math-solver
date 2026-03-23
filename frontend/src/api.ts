export type StepExplanation = {
  step_number: number;
  title: string;
  explanation: string;
  suggested_code: string | null;
};

export type DiagnosticItem = {
  rule_id: string;
  error_type: string;
  severity: "low" | "medium" | "high" | "critical";
  why_it_happens: string;
  evidence: string;
  fix_summary: string;
  step_explanations: StepExplanation[];
};

export type RuleBasedResult = {
  method: string;
  detected_topics: string[];
  diagnostics: DiagnosticItem[];
  next_learning_steps: string[];
};

export type LlmBaselineResult = {
  analysis: string;
  suggested_fixes: string[];
  confidence: string;
};

export type ComparisonResult = {
  coverage_note: string;
  interpretability_note: string;
  actionability_note: string;
};

export type DiagnoseResponse = {
  knowledge_model: string;
  code_pattern_flow: string[];
  rule_based: RuleBasedResult;
  llm_baseline: LlmBaselineResult | null;
  comparison: ComparisonResult | null;
};

const base = import.meta.env.VITE_API_BASE ?? "";

export async function diagnoseCode(input: {
  problem_title: string;
  problem_statement: string;
  source_code: string;
  language: "c" | "cpp";
  compare_with_llm: boolean;
}): Promise<DiagnoseResponse> {
  const res = await fetch(`${base}/api/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const text = await res.text();
  if (!res.ok) {
    let detail = text;
    try {
      const j = JSON.parse(text) as { detail?: unknown };
      if (typeof j.detail === "string") detail = j.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return JSON.parse(text) as DiagnoseResponse;
}
