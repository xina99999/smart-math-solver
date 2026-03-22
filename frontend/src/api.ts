export type SolveStep = {
  step_number: number;
  title: string;
  latex: string | null;
  explanation: string;
};

export type SolveResponse = {
  method: string;
  steps: SolveStep[];
  result: string;
};

const base = import.meta.env.VITE_API_BASE ?? "";

export async function solveProblem(problem: string, gradeLevel: 1 | 2): Promise<SolveResponse> {
  const res = await fetch(`${base}/api/solve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ problem, grade_level: gradeLevel }),
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
  return JSON.parse(text) as SolveResponse;
}
