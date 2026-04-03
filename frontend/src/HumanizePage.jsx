import { useEffect, useMemo, useState } from "react";
import Sidebar from "./components/Sidebar";
import { useWorkflow } from "./context/WorkflowContext";

const humanizeStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body, html { font-family: 'Nunito', sans-serif; background: #F5EBDD; color: #1F2A44; }

  .app-shell { display: flex; min-height: 100vh; background: #F5EBDD; }
  .main-content {
    flex: 1; overflow-y: auto; background: #F5EBDD;
    background-image:
      radial-gradient(circle at 1px 1px, rgba(31,42,68,0.05) 1px, transparent 0),
      radial-gradient(circle at 1px 1px, rgba(31,42,68,0.05) 1px, transparent 0);
    background-size: 26px 26px;
  }

  .humanize-hero {
    padding: 28px 32px; border-bottom: 1.5px dashed rgba(31,42,68,0.12);
    background: linear-gradient(120deg, rgba(184,168,227,0.18), rgba(255,200,87,0.15));
  }
  .hero-label {
    font-size: 11px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase;
    color: rgba(31,42,68,0.6); margin-bottom: 8px;
  }
  .hero-title { font-size: 32px; font-weight: 900; color: #1F2A44; line-height: 1.15; }
  .hero-sub {
    margin-top: 10px; font-size: 15px; color: rgba(31,42,68,0.75);
    max-width: 720px; line-height: 1.6;
  }
  .hero-sub strong { background: #FFE5A0; padding: 0 4px; border-radius: 4px; }

  .humanize-grid {
    display: grid; grid-template-columns: 360px 1fr; gap: 28px;
    padding: 32px; align-items: start;
  }

  .input-panel, .result-panel {
    background: #FDFAF6; border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 18px; padding: 24px;
    box-shadow: 4px 4px 0 rgba(31,42,68,0.08);
  }
  .panel-heading { font-size: 20px; font-weight: 900; margin-bottom: 16px; color: #1F2A44; display: flex; gap: 8px; align-items: center; }

  .input-panel textarea {
    width: 100%; min-height: 220px; border: 1.5px solid rgba(31,42,68,0.15);
    border-radius: 14px; padding: 14px; resize: vertical;
    font-family: 'Nunito', sans-serif; font-size: 13px; line-height: 1.5;
    color: #1F2A44; background: #FFFDF9; outline: none;
  }
  .input-panel textarea:focus { border-color: #B8A8E3; box-shadow: 0 0 0 2px rgba(184,168,227,0.2); }

  .panel-field { margin-bottom: 16px; }
  .panel-label {
    font-size: 11px; font-weight: 800; letter-spacing: 0.7px; text-transform: uppercase;
    color: rgba(31,42,68,0.55); margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
  }
  .helper-link { font-size: 11px; font-weight: 700; color: #4A3B8C; cursor: pointer; }

  .toggle-row {
    display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 700; color: #1F2A44;
  }
  .toggle-row input[type="checkbox"] { width: 18px; height: 18px; accent-color: #FFC857; }

  .panel-actions { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }
  .primary-btn {
    padding: 14px; border-radius: 12px; border: 2px solid #1F2A44;
    background: #FFC857; font-weight: 900; font-size: 14px; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 6px;
    box-shadow: 4px 4px 0 rgba(31,42,68,0.25); transition: transform 0.15s ease;
  }
  .primary-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: 3px 3px 0 rgba(31,42,68,0.2); }
  .secondary-btn {
    padding: 10px 14px; border-radius: 10px; border: 1.5px dashed rgba(31,42,68,0.2);
    background: rgba(255,255,255,0.6); font-weight: 800; font-size: 12px; cursor: pointer;
  }

  .error-banner {
    margin-top: 8px; padding: 10px 12px; border-radius: 10px; background: #F4A4A4;
    color: #7A1A1A; font-size: 12px; font-weight: 700; border: 1.5px solid rgba(122,26,26,0.25);
  }

  .score-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;
  }
  .score-card {
    border-radius: 14px; border: 1.5px solid rgba(31,42,68,0.1);
    padding: 14px; background: rgba(255,255,255,0.9);
  }
  .score-label { font-size: 11px; font-weight: 800; letter-spacing: 0.6px; color: rgba(31,42,68,0.55); text-transform: uppercase; }
  .score-value { font-size: 26px; font-weight: 900; color: #1F2A44; margin: 6px 0; }
  .score-sub { font-size: 12px; color: rgba(31,42,68,0.6); font-weight: 600; }

  .verdict-badge {
    display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
    border-radius: 50px; font-size: 12px; font-weight: 800; border: 2px solid;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .verdict-human { background: #C8E6CB; color: #1F5732; border-color: #2D6A4F; }
  .verdict-borderline { background: #FFE5A0; color: #7A5400; border-color: #D5A423; }
  .verdict-ai { background: #F4A4A4; color: #7A1A1A; border-color: #C05050; }

  .ai-bars { display: flex; gap: 16px; margin: 22px 0; }
  .ai-bar {
    flex: 1; background: rgba(31,42,68,0.05); border-radius: 12px; padding: 14px;
    border: 1.5px solid rgba(31,42,68,0.1);
  }
  .bar-label { font-size: 12px; font-weight: 800; color: rgba(31,42,68,0.6); margin-bottom: 8px; text-transform: uppercase; }
  .bar-track { height: 10px; border-radius: 50px; background: rgba(31,42,68,0.08); overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 50px; transition: width 0.4s ease; }

  .flags-wrap { margin: 18px 0; }
  .flags-title { font-size: 12px; font-weight: 800; letter-spacing: 0.5px; color: rgba(31,42,68,0.55); text-transform: uppercase; margin-bottom: 8px; }
  .flag-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .flag-chip {
    padding: 6px 10px; border-radius: 50px; font-size: 11px; font-weight: 700;
    background: rgba(31,42,68,0.05); border: 1.5px dashed rgba(31,42,68,0.2);
  }

  .rewritten-card {
    margin-top: 14px; border-radius: 16px; padding: 16px;
    background: rgba(184,168,227,0.15); border: 1.5px solid rgba(74,59,140,0.2);
  }
  .rewritten-card textarea {
    width: 100%; min-height: 200px; border: 1.5px solid rgba(74,59,140,0.2);
    background: #FFF; border-radius: 12px; padding: 12px; font-size: 13px;
    font-family: 'Nunito', sans-serif; line-height: 1.6; color: #1F2A44; resize: vertical;
  }
  .rewritten-actions { margin-top: 10px; display: flex; gap: 10px; }

  .empty-state {
    padding: 32px; border: 2px dashed rgba(31,42,68,0.2); border-radius: 18px;
    text-align: center; color: rgba(31,42,68,0.55); font-weight: 700; line-height: 1.6;
    font-size: 14px; background: rgba(255,255,255,0.7);
  }
`;

const verdictClass = (verdict) => {
  if (verdict === "likely_human") return "verdict-badge verdict-human";
  if (verdict === "borderline") return "verdict-badge verdict-borderline";
  if (!verdict) return "verdict-badge";
  return "verdict-badge verdict-ai";
};

const verdictLabel = (verdict) => (verdict ? verdict.replace(/_/g, " ") : "--");

const formatPercent = (value) => (typeof value === "number" ? `${value.toFixed(1)}%` : "--");
const formatNumber = (value) => (typeof value === "number" ? value.toFixed(1) : "--");

export default function HumanizePage({ activePage = "humanizer", onNavigate }) {
  const { blogResult, humanizeResult, loading, errors, actions } = useWorkflow();
  const [content, setContent] = useState(blogResult?.content || "");
  const [forceRewrite, setForceRewrite] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (blogResult?.content) {
      setContent(blogResult.content);
    }
  }, [blogResult]);

  const before = humanizeResult?.before_detection;
  const after = humanizeResult?.after_detection;

  const improvement = useMemo(() => humanizeResult?.naturalness_improvement ?? null, [humanizeResult]);

  const handlePrefill = () => {
    if (blogResult?.content) {
      setContent(blogResult.content);
    }
  };

  const copyToClipboard = async (value) => {
    if (!value || typeof navigator === "undefined" || !navigator.clipboard) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch (error) {
      console.warn("Clipboard copy failed", error);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!content.trim()) return;
    try {
      await actions.runHumanize({ content: content.trim(), force: forceRewrite });
    } catch (error) {
      // errors are surfaced from context
    }
  };

  return (
    <>
      <style>{humanizeStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          <div className="humanize-hero">
            <div className="hero-label">AI Detection Guard</div>
            <div className="hero-title">Humanize any draft before it hits the CMS.</div>
            <p className="hero-sub">
              Drop your content below and let the Humanizer run AI detection, rewrite weak sections, and return a
              <strong> reviewer-ready draft</strong> with before/after evidence and score deltas.
            </p>
          </div>

          <div className="humanize-grid">
            <form className="input-panel" onSubmit={handleSubmit}>
              <div className="panel-heading">✍️ Input Draft</div>

              <div className="panel-field">
                <div className="panel-label">
                  Content to humanize
                  {blogResult?.content && (
                    <span className="helper-link" onClick={handlePrefill}>
                      Use latest blog output
                    </span>
                  )}
                </div>
                <textarea
                  value={content}
                  onChange={(event) => setContent(event.target.value)}
                  placeholder="Paste any AI-sounding paragraph or full blog draft..."
                />
              </div>

              <div className="panel-field toggle-row">
                <input
                  type="checkbox"
                  checked={forceRewrite}
                  onChange={(event) => setForceRewrite(event.target.checked)}
                />
                Force rewrite even if the score is low
              </div>

              {errors.humanize && <div className="error-banner">{errors.humanize}</div>}

              <div className="panel-actions">
                <button className="primary-btn" type="submit" disabled={loading.humanize}>
                  {loading.humanize ? "⏳ Humanizing..." : "🧬 Run Humanizer"}
                </button>
                <button className="secondary-btn" type="button" onClick={() => setContent("")}>Clear input</button>
              </div>
            </form>

            <div className="result-panel">
              <div className="panel-heading">🧪 Detection Proof</div>

              {humanizeResult ? (
                <>
                  <div className="score-grid">
                    <div className="score-card">
                      <div className="score-label">Original probability</div>
                      <div className="score-value">{formatPercent(humanizeResult.before_detection?.ai_probability_percent)}</div>
                      <div className="score-sub">AI likelihood before rewrite</div>
                    </div>
                    <div className="score-card">
                      <div className="score-label">Final probability</div>
                      <div className="score-value">{formatPercent(humanizeResult.after_detection?.ai_probability_percent)}</div>
                      <div className="score-sub">After Humanizer pass</div>
                    </div>
                    <div className="score-card">
                      <div className="score-label">Improvement</div>
                      <div className="score-value">
                        {humanizeResult && improvement !== null ? `${improvement.toFixed(1)} pts` : "--"}
                      </div>
                      <div className="score-sub">Naturalness gain</div>
                    </div>
                  </div>

                  <div className="ai-bars">
                    <div className="ai-bar">
                      <div className="bar-label">Before verdict</div>
                      <div className={verdictClass(before?.verdict)}>{verdictLabel(before?.verdict)}</div>
                      <div className="bar-track" style={{ marginTop: 10 }}>
                        <div
                          className="bar-fill"
                          style={{ width: `${Math.min(before?.ai_probability_percent || 0, 100)}%`, background: "#F4A4A4" }}
                        />
                      </div>
                      <div className="score-sub" style={{ marginTop: 6 }}>
                        Naturalness {formatNumber(before?.naturalness_score)}
                      </div>
                    </div>

                    <div className="ai-bar">
                      <div className="bar-label">After verdict</div>
                      <div className={verdictClass(after?.verdict)}>{verdictLabel(after?.verdict)}</div>
                      <div className="bar-track" style={{ marginTop: 10 }}>
                        <div
                          className="bar-fill"
                          style={{ width: `${Math.min(after?.ai_probability_percent || 0, 100)}%`, background: "#A3C9A8" }}
                        />
                      </div>
                      <div className="score-sub" style={{ marginTop: 6 }}>
                        Naturalness {formatNumber(after?.naturalness_score)}
                      </div>
                    </div>
                  </div>

                  <div className="flags-wrap">
                    <div className="flags-title">Detection flags reduced</div>
                    {before?.flags?.length ? (
                      <div className="flag-chips">
                        {before.flags.map((flag) => (
                          <span key={flag} className="flag-chip">
                            ❗ {flag}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <div className="flag-chip">No specific flags triggered</div>
                    )}
                  </div>

                  <div className="rewritten-card">
                    <div className="panel-label" style={{ marginBottom: 6 }}>Humanized draft</div>
                    <textarea value={humanizeResult.humanized_content || ""} readOnly />
                    <div className="rewritten-actions">
                      <button className="secondary-btn" type="button" onClick={() => copyToClipboard(humanizeResult.humanized_content)}>
                        {copied ? "Copied" : "Copy to clipboard"}
                      </button>
                      <button className="secondary-btn" type="button" onClick={() => onNavigate?.("blog-gen")}>Send to Blog Lab</button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  Run the Humanizer to see AI detection deltas, verdicts, and a polished rewrite. Paste any draft on the left and press “Run Humanizer”.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
