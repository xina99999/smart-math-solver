import { useState } from "react";
import "./App.css";
import { solveProblem, type SolveResponse } from "./api";
import { LatexBlock } from "./components/LatexBlock";

export default function App() {
  const [problem, setProblem] = useState(
    "Tính diện tích tam giác có cạnh đáy 10 cm và chiều cao 5 cm.",
  );
  const [grade, setGrade] = useState<1 | 2>(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SolveResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await solveProblem(problem.trim(), grade);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Smart Math Solver</h1>
      </header>

      <form className="panel" onSubmit={onSubmit}>
        <label htmlFor="problem">Bài toán / phép tính</label>
        <textarea
          id="problem"
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="Nhập đề bằng tiếng Việt..."
          spellCheck={false}
        />
        <div className="row">
          <div className="grade">
            <label htmlFor="grade">Cấp</label>
            <select
              id="grade"
              value={grade}
              onChange={(e) => setGrade(Number(e.target.value) as 1 | 2)}
            >
              <option value={1}>Cấp 1 (trực quan)</option>
              <option value={2}>Cấp 2 (đại số)</option>
            </select>
          </div>
          <button className="primary" type="submit" disabled={loading || !problem.trim()}>
            {loading ? "Đang suy diễn…" : "Giải"}
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </form>

      {result && (
        <section className="panel">
          <div className="result-method">Phương pháp: {result.method}</div>
          <div className="steps">
            {result.steps.map((s) => (
              <article key={s.step_number} className="step">
                <div className="step-head">
                  Bước {s.step_number}: {s.title}
                </div>
                {s.latex && s.latex.trim() ? <LatexBlock latex={s.latex.trim()} /> : null}
                <div className="step-body">{s.explanation}</div>
              </article>
            ))}
          </div>
          <div className="result-final">Kết quả: {result.result}</div>
        </section>
      )}

      
    </div>
  );
}
