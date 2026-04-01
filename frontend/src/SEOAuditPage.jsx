import { useEffect, useMemo, useState } from "react";
import Sidebar from "./components/Sidebar";
import { useWorkflow } from "./context/WorkflowContext";

const auditStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body, html { font-family: 'Nunito', sans-serif; background: #F5EBDD; color: #1F2A44; }

  .app-shell { display: flex; min-height: 100vh; background: #F5EBDD; }
  .main-content {
    flex: 1; overflow-y: auto; background: #F5EBDD;
    background-image:
      linear-gradient(rgba(31,42,68,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(31,42,68,0.03) 1px, transparent 1px);
    background-size: 28px 28px;
  }

  .audit-hero {
    padding: 30px 32px; border-bottom: 1.5px dashed rgba(31,42,68,0.15);
    background: linear-gradient(125deg, rgba(200,230,203,0.25), rgba(184,168,227,0.2));
  }
  .audit-title { font-size: 34px; font-weight: 900; color: #1F2A44; line-height: 1.1; }
  .audit-sub { margin-top: 10px; font-size: 15px; color: rgba(31,42,68,0.7); max-width: 760px; }

  .audit-grid {
    display: grid; grid-template-columns: 340px 1fr; gap: 28px; padding: 32px; align-items: start;
  }

  .audit-form, .audit-panel {
    background: #FDFAF6; border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 18px; padding: 24px; box-shadow: 4px 4px 0 rgba(31,42,68,0.08);
  }
  .audit-form h3 { font-size: 20px; font-weight: 900; margin-bottom: 16px; }

  .form-group { margin-bottom: 16px; }
  .form-label {
    font-size: 11px; font-weight: 800; letter-spacing: 0.7px; color: rgba(31,42,68,0.55);
    text-transform: uppercase; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
  }
  .form-input, .form-textarea {
    width: 100%; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 12px;
    padding: 10px 12px; font-family: 'Nunito', sans-serif; font-size: 13px; color: #1F2A44;
    background: #FFFDF9; outline: none;
  }
  .form-input:focus, .form-textarea:focus { border-color: #A3C9A8; box-shadow: 0 0 0 2px rgba(163,201,168,0.25); }
  .form-textarea { min-height: 220px; resize: vertical; line-height: 1.6; }

  .form-helper { font-size: 11px; font-weight: 700; color: #4A3B8C; cursor: pointer; }

  .audit-actions { display: flex; flex-direction: column; gap: 10px; margin-top: 18px; }
  .run-btn {
    padding: 13px; border-radius: 12px; border: 2px solid #1F2A44; background: #A3C9A8;
    font-weight: 900; font-size: 14px; color: #1F2A44; cursor: pointer;
    box-shadow: 4px 4px 0 rgba(31,42,68,0.2);
  }
  .run-btn:disabled { opacity: 0.6; cursor: not-allowed; box-shadow: 3px 3px 0 rgba(31,42,68,0.15); }
  .ghost-btn {
    padding: 11px; border-radius: 10px; border: 1.5px dashed rgba(31,42,68,0.2);
    background: rgba(255,255,255,0.8); font-weight: 800; font-size: 12px; cursor: pointer;
  }

  .error-note {
    margin-top: 10px; padding: 9px 12px; border-radius: 10px; background: #F4A4A4;
    color: #7A1A1A; font-size: 12px; font-weight: 700; border: 1.5px solid rgba(122,26,26,0.25);
  }

  .audit-panel h3 { font-size: 22px; font-weight: 900; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; }

  .score-badge {
    display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px;
    border-radius: 14px; border: 2px solid #1F2A44; font-weight: 900; font-size: 20px;
    margin-bottom: 18px; box-shadow: 4px 4px 0 rgba(31,42,68,0.18);
  }
  .score-meta { font-size: 11px; letter-spacing: 0.6px; text-transform: uppercase; color: rgba(31,42,68,0.7); }

  .metrics-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px;
  }
  .metric-card {
    border-radius: 14px; border: 1.5px solid rgba(31,42,68,0.1); padding: 14px;
    background: rgba(255,255,255,0.9);
  }
  .metric-label { font-size: 11px; font-weight: 800; letter-spacing: 0.5px; color: rgba(31,42,68,0.55); text-transform: uppercase; }
  .metric-value { font-size: 22px; font-weight: 900; color: #1F2A44; margin-top: 6px; }
  .metric-sub { font-size: 12px; color: rgba(31,42,68,0.6); }

  .density-list { margin: 20px 0; border: 1.5px dashed rgba(31,42,68,0.18); border-radius: 14px; padding: 16px; }
  .density-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(31,42,68,0.08); font-weight: 700; font-size: 13px; }
  .density-row:last-child { border-bottom: none; }
  .density-status { font-size: 11px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; padding: 4px 10px; border-radius: 50px; }
  .status-optimal { background: #C8E6CB; color: #1F5732; }
  .status-under { background: #FFE5A0; color: #7A5400; }
  .status-over { background: #F4A4A4; color: #7A1A1A; }

  .issues-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .issue-card {
    padding: 14px; border-radius: 12px; background: rgba(31,42,68,0.03);
    border: 1.5px solid rgba(31,42,68,0.08); font-size: 13px; color: rgba(31,42,68,0.75);
  }
  .issue-card strong { display: block; font-size: 11px; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 6px; color: rgba(31,42,68,0.6); }

  .lsi-wrap { margin: 18px 0; }
  .lsi-title { font-size: 11px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase; color: rgba(31,42,68,0.6); margin-bottom: 8px; }
  .chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip { padding: 6px 10px; border-radius: 50px; border: 1.5px solid rgba(31,42,68,0.15); font-size: 12px; font-weight: 700; background: rgba(255,255,255,0.8); }

  .recommendations { margin-top: 20px; border-top: 1.5px dashed rgba(31,42,68,0.15); padding-top: 16px; }
  .recommendations h4 { font-size: 14px; font-weight: 900; margin-bottom: 8px; }
  .recommendations ul { padding-left: 20px; }
  .recommendations li { margin-bottom: 6px; font-size: 13px; color: rgba(31,42,68,0.78); }

  .empty-panel {
    padding: 36px; text-align: center; border: 2px dashed rgba(31,42,68,0.2);
    border-radius: 16px; color: rgba(31,42,68,0.55); font-weight: 700; line-height: 1.6;
  }
`;

const scoreTone = (score) => {
  if (typeof score !== "number") return { color: "#1F2A44", bg: "rgba(31,42,68,0.1)" };
  if (score >= 80) return { color: "#1F5732", bg: "#C8E6CB" };
  if (score >= 60) return { color: "#7A5400", bg: "#FFE5A0" };
  return { color: "#7A1A1A", bg: "#F4A4A4" };
};

const formatNumber = (value) => (typeof value === "number" ? value.toFixed(1) : "--");

export default function SEOAuditPage({ activePage = "seo-audit", onNavigate }) {
  const { blogResult, blogHistory, seoAudit, loading, errors, actions } = useWorkflow();
  const [form, setForm] = useState({
    keyword: blogHistory?.[0]?.keyword || "",
    content: blogResult?.content || "",
  });
  const [secondaryRaw, setSecondaryRaw] = useState("");

  useEffect(() => {
    if (blogResult?.content) {
      setForm((prev) => ({ ...prev, content: blogResult.content }));
    }
  }, [blogResult]);

  useEffect(() => {
    if (blogHistory?.length && blogHistory[0].keyword) {
      setForm((prev) => ({ ...prev, keyword: prev.keyword || blogHistory[0].keyword }));
    }
  }, [blogHistory]);

  const secondaryKeywords = useMemo(
    () =>
      secondaryRaw
        .split(",")
        .map((kw) => kw.trim())
        .filter(Boolean),
    [secondaryRaw]
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.keyword.trim() || !form.content.trim()) return;
    try {
      await actions.runSEOAudit({
        keyword: form.keyword.trim(),
        content: form.content.trim(),
        secondary_keywords: secondaryKeywords,
      });
    } catch (error) {
      // handled upstream
    }
  };

  const score = seoAudit?.overall_score;
  const badgeTone = scoreTone(score);

  return (
    <>
      <style>{auditStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          <div className="audit-hero">
            <div className="audit-title">SEO Audit Studio</div>
            <p className="audit-sub">
              Benchmark any draft against Blogy’s deterministic SEO rules. Inspect density, readability, heading depth,
              LSI coverage, and get a prioritized fix list with projected traffic numbers.
            </p>
          </div>

          <div className="audit-grid">
            <form className="audit-form" onSubmit={handleSubmit}>
              <h3>🔍 Analyze Draft</h3>
              <div className="form-group">
                <div className="form-label">Primary Keyword</div>
                <input
                  className="form-input"
                  value={form.keyword}
                  onChange={(event) => setForm((prev) => ({ ...prev, keyword: event.target.value }))}
                  placeholder="e.g. modular timber homes"
                />
              </div>

              <div className="form-group">
                <div className="form-label">Secondary Keywords</div>
                <input
                  className="form-input"
                  value={secondaryRaw}
                  onChange={(event) => setSecondaryRaw(event.target.value)}
                  placeholder="comma separated (optional)"
                />
              </div>

              <div className="form-group">
                <div className="form-label">
                  Content
                  {blogResult?.content && (
                    <span className="form-helper" onClick={() => setForm((prev) => ({ ...prev, content: blogResult.content }))}>
                      Use latest blog output
                    </span>
                  )}
                </div>
                <textarea
                  className="form-textarea"
                  value={form.content}
                  onChange={(event) => setForm((prev) => ({ ...prev, content: event.target.value }))}
                  placeholder="Paste the full draft to score"
                />
              </div>

              {errors.seoAudit && <div className="error-note">{errors.seoAudit}</div>}

              <div className="audit-actions">
                <button className="run-btn" type="submit" disabled={loading.seoAudit}>
                  {loading.seoAudit ? "⏳ Auditing..." : "📊 Run SEO Audit"}
                </button>
                <button className="ghost-btn" type="button" onClick={() => onNavigate?.("blog-gen")}>Back to Blog Lab</button>
              </div>
            </form>

            <div className="audit-panel">
              <h3>📈 Scoreboard</h3>
              {seoAudit ? (
                <>
                  <div
                    className="score-badge"
                    style={{ color: badgeTone.color, background: badgeTone.bg }}
                  >
                    <div>{typeof score === "number" ? score.toFixed(0) : "--"}</div>
                    <div>
                      <div className="score-meta">Overall SEO Score</div>
                      <div style={{ fontSize: 12 }}>{seoAudit.projected_traffic_potential}</div>
                    </div>
                  </div>

                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="metric-label">Readability</div>
                      <div className="metric-value">{formatNumber(seoAudit.readability_score)}</div>
                      <div className="metric-sub">{seoAudit.readability_grade}</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Word Count</div>
                      <div className="metric-value">{seoAudit.word_count}</div>
                      <div className="metric-sub">Headings: {seoAudit.heading_count}</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Internal Links</div>
                      <div className="metric-value">{seoAudit.internal_link_count}</div>
                      <div className="metric-sub">Keyword in title: {seoAudit.keyword_in_title ? "Yes" : "No"}</div>
                    </div>
                  </div>

                  <div className="density-list">
                    {seoAudit.keyword_density.map((item) => (
                      <div key={item.keyword} className="density-row">
                        <span>{item.keyword}</span>
                        <span>{item.density_percent.toFixed(2)}%</span>
                        <span className={`density-status status-${item.status}`}>
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="issues-grid">
                    <div className="issue-card">
                      <strong>Issues Detected</strong>
                      {seoAudit.issues.length ? (
                        <ul>
                          {seoAudit.issues.map((issue) => (
                            <li key={issue}>{issue}</li>
                          ))}
                        </ul>
                      ) : (
                        <div>Looks solid. No blocking issues.</div>
                      )}
                    </div>
                    <div className="issue-card">
                      <strong>Quick Wins</strong>
                      {seoAudit.recommendations.length ? (
                        <ul>
                          {seoAudit.recommendations.map((rec) => (
                            <li key={rec}>{rec}</li>
                          ))}
                        </ul>
                      ) : (
                        <div>Keep doubling down on structure + intent.</div>
                      )}
                    </div>
                  </div>

                  <div className="lsi-wrap">
                    <div className="lsi-title">LSI keywords found</div>
                    {seoAudit.lsi_keywords_found.length ? (
                      <div className="chip-row">
                        {seoAudit.lsi_keywords_found.map((kw) => (
                          <span className="chip" key={kw}>#{kw}</span>
                        ))}
                      </div>
                    ) : (
                      <div className="chip">No semantic twins detected yet.</div>
                    )}
                  </div>

                  <div className="recommendations">
                    <h4>Next actions</h4>
                    <ul>
                      {seoAudit.recommendations.slice(0, 4).map((rec) => (
                        <li key={rec}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </>
              ) : (
                <div className="empty-panel">
                  Paste a draft and run the audit to see composite scores, density checks, LSI coverage, and prioritized fixes.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
