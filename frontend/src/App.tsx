import { useState } from "react";
import "./App.css";
import { diagnoseCode, type DiagnoseResponse } from "./api";

export default function App() {
  const [problemTitle, setProblemTitle] = useState("Tìm phần tử lớn nhất trong mảng");
  const [problemStatement, setProblemStatement] = useState(
    "Nhập mảng n số nguyên và in ra giá trị lớn nhất.",
  );
  const [sourceCode, setSourceCode] = useState(
    "#include <iostream>\nusing namespace std;\nint main(){\n  int n; cin >> n;\n  int a[1000];\n  for(int i=0;i<=n;i++) cin >> a[i];\n  int mx = a[0];\n  for(int i=1;i<=n;i++) if(a[i]>mx) mx=a[i];\n  cout << mx;\n}",
  );
  const [language, setLanguage] = useState<"c" | "cpp">("cpp");
  const [compareWithLlm, setCompareWithLlm] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnoseResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await diagnoseCode({
        problem_title: problemTitle.trim(),
        problem_statement: problemStatement.trim(),
        source_code: sourceCode,
        language,
        compare_with_llm: compareWithLlm,
      });
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
        <h1>Hệ thống hỗ trợ giải bài tập lập trình</h1>
        <p>Chẩn đoán lỗi logic/thuật toán theo luật và giải thích từng bước theo ngữ cảnh.</p>
      </header>

      <form className="panel" onSubmit={onSubmit}>
        <label htmlFor="problem-title">Tên bài</label>
        <textarea
          id="problem-title"
          value={problemTitle}
          onChange={(e) => setProblemTitle(e.target.value)}
          placeholder="Ví dụ: Tìm max trong mảng"
          spellCheck={false}
        />

        <label htmlFor="problem-statement">Mô tả đề bài</label>
        <textarea
          id="problem-statement"
          value={problemStatement}
          onChange={(e) => setProblemStatement(e.target.value)}
          placeholder="Mô tả input, output, ràng buộc..."
          spellCheck={false}
        />
        <label htmlFor="source-code">Mã nguồn sinh viên (C/C++)</label>
        <textarea
          id="source-code"
          value={sourceCode}
          onChange={(e) => setSourceCode(e.target.value)}
          placeholder="Dán mã nguồn C/C++ tại đây..."
          spellCheck={false}
        />

        <div className="row">
          <div className="grade">
            <label htmlFor="language">Ngôn ngữ</label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as "c" | "cpp")}
            >
              <option value="cpp">C++</option>
              <option value="c">C</option>
            </select>
          </div>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={compareWithLlm}
              onChange={(e) => setCompareWithLlm(e.target.checked)}
            />
            So sánh với baseline chỉ dùng LLM
          </label>
          <button
            className="primary"
            type="submit"
            disabled={loading || !problemTitle.trim() || !problemStatement.trim() || !sourceCode.trim()}
          >
            {loading ? "Đang chẩn đoán..." : "Phân tích mã nguồn"}
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </form>

      {result && (
        <section className="panel">
          <div className="result-header">
            <div className="result-method">📚 Mô hình tri thức: <span className="highlight">{result.knowledge_model}</span></div>
            <div className="flow">🔄 Chuỗi suy luận: <span className="highlight">{result.code_pattern_flow.join(" → ")}</span></div>
            <div className="result-method">🧠 Suy luận chính: <span className="highlight">{result.rule_based.method}</span></div>
            <div className="topics">
              📍 Chủ đề phát hiện: <span className="highlight">
                {result.rule_based.detected_topics.length
                  ? result.rule_based.detected_topics.join(", ")
                  : "Chưa xác định"}
              </span>
            </div>
          </div>

          <hr className="divider" />

          <div className="steps">
            {result.rule_based.diagnostics.map((diag) => {
              const severityEmoji = {
                critical: "🔴",
                high: "🟠",
                medium: "🟡",
                low: "🔵",
              }[diag.severity] || "⚪";

              return (
                <article key={diag.rule_id} className={`step severity-${diag.severity}`}>
                  <div className="step-head">
                    {severityEmoji} <strong>[{diag.severity.toUpperCase()}]</strong> {diag.error_type} <code className="rule-id">{diag.rule_id}</code>
                  </div>
                  <div className="step-body step-why">
                    <strong>❓ Nguyên nhân:</strong>
                    <p>{diag.why_it_happens}</p>
                  </div>
                  <div className="step-body step-evidence">
                    <strong>🔍 Bằng chứng:</strong>
                    <p><code>{diag.evidence}</code></p>
                  </div>
                  <div className="step-body step-fix">
                    <strong>🔧 Tóm tắt sửa:</strong>
                    <p>{diag.fix_summary}</p>
                  </div>
                  <div className="substeps">
                    <strong>📋 Các bước sửa:</strong>
                    {diag.step_explanations.map((s) => (
                      <div key={`${diag.rule_id}-${s.step_number}`} className="substep">
                        <div className="step-title">
                          <span className="step-badge">Bước {s.step_number}</span> {s.title}
                        </div>
                        <p className="step-exp">{s.explanation}</p>
                        {s.suggested_code ? <pre className="code-block">{s.suggested_code}</pre> : null}
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>

          <hr className="divider" />

          <div className="result-final">
            <strong>📖 Gợi ý học tiếp:</strong>
            <ul>
              {result.rule_based.next_learning_steps.map((s) => (
                <li key={s}>💡 {s}</li>
              ))}
            </ul>
          </div>

          {result.llm_baseline && (
            <div className="llm-box">
              <h3>🤖 Phân tích bổ sung (LLM Baseline)</h3>
              <div className="llm-content">
                <div className="llm-section">
                  <strong>📝 Phân tích:</strong>
                  <p>{result.llm_baseline.analysis}</p>
                </div>
                <div className="llm-section">
                  <strong>💪 Độ tự tin:</strong>
                  <p>{result.llm_baseline.confidence}</p>
                </div>
                <div className="llm-section">
                  <strong>🛠️ Gợi ý sửa:</strong>
                  <ul>
                    {result.llm_baseline.suggested_fixes.map((fix, idx) => (
                      <li key={idx}>✓ {fix}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {result.comparison && (
            <div className="llm-box">
              <h3>⚖️ So sánh hiệu quả (Rule-Based vs LLM)</h3>
              <div className="llm-content">
                <div className="comparison-item">
                  <strong>📊 Coverage:</strong>
                  <p>{result.comparison.coverage_note}</p>
                </div>
                <div className="comparison-item">
                  <strong>🔬 Interpretability:</strong>
                  <p>{result.comparison.interpretability_note}</p>
                </div>
                <div className="comparison-item">
                  <strong>✨ Actionability:</strong>
                  <p>{result.comparison.actionability_note}</p>
                </div>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
