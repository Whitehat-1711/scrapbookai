import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ProfileOverlay from "./components/ProfileOverlay";
import { useWorkflow } from "./context/WorkflowContext";

const serpStyles = `
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

  .topbar {
    display: flex; align-items: center; gap: 14px; padding: 12px 24px;
    background: rgba(245,235,221,0.92); backdrop-filter: blur(4px);
    border-bottom: 1.5px dashed rgba(31,42,68,0.12); position: sticky; top: 0; z-index: 100;
  }
  .topbar-search {
    flex: 1; max-width: 300px; display: flex; align-items: center; gap: 8px;
    background: #FDFAF6; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 50px; padding: 7px 14px;
  }
  .topbar-search input { border: none; background: transparent; outline: none; font-family: 'Nunito', sans-serif; font-size: 13px; color: #1F2A44; width: 100%; }
  .topbar-search input::placeholder { color: #9AA5B4; }
  .badge { padding: 5px 12px; border-radius: 50px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; border: 1.5px solid; }
  .badge-geo { background: #C8E6CB; color: #2D6A4F; border-color: #2D6A4F; }
  .badge-seo { background: #D4C8F5; color: #4A3B8C; border-color: #4A3B8C; }
  .topbar-right { margin-left: auto; display: flex; align-items: center; gap: 12px; position: relative; }
  .topbar-greeting { 
    background: #C8E6CB; border: 1.5px solid #2D6A4F;
    border-radius: 50px; padding: 6px 14px;
    font-weight: 700; font-size: 13px; color: #1F2A44;
  }
  .topbar-bell { font-size: 18px; cursor: pointer; }
  .topbar-avatar { width: 36px; height: 36px; border-radius: 50%; border: 2px solid #1F2A44; overflow: hidden; cursor: pointer; }

  .page-body { padding: 32px 28px 80px; }

  /* Page header */
  .page-header { margin-bottom: 8px; position: relative; }
  .page-title {
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 38px; color: #1F2A44;
    line-height: 1.1; margin-bottom: 10px;
  }
  .page-desc { font-size: 15px; color: rgba(31,42,68,0.7); line-height: 1.5; }
  .page-desc .highlight {
    font-style: italic; font-weight: 800; color: #1F2A44;
    background: #FFE5A0; padding: 1px 4px; border-radius: 4px;
  }
  .doodle-arrow {
    position: absolute; top: 8px; right: 60px; font-size: 32px; opacity: 0.15;
    transform: rotate(-20deg); user-select: none;
  }

  /* Main grid */
  .main-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 32px; align-items: start;
  }

  /* Left: Competitor landscape */
  .comp-section {}
  .comp-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
  .comp-title { font-weight: 900; font-size: 22px; color: #1F2A44; }
  .sources-badge {
    background: #E8E4DC; border: 1.5px solid rgba(31,42,68,0.15);
    border-radius: 50px; padding: 5px 14px; font-size: 12px; font-weight: 700; color: rgba(31,42,68,0.6);
    display: flex; align-items: center; gap: 6px;
  }

  .center-diagram {
    display: flex; justify-content: center; align-items: center;
    margin: 8px 0 20px; position: relative; height: 70px;
  }
  .opportunity-circle {
    width: 90px; height: 90px; border-radius: 50%;
    border: 2px dashed rgba(31,42,68,0.25);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: 'Caveat', cursive; font-size: 11px; font-weight: 700;
    color: rgba(31,42,68,0.6); text-align: center; position: absolute; left: 50%; top: -10px;
    transform: translateX(-50%); background: rgba(245,235,221,0.8);
  }
  .opp-arrow { font-size: 22px; position: absolute; right: 20%; top: 50%; transform: translateY(-50%) rotate(-30deg); opacity: 0.4; }

  .comp-list { display: flex; flex-direction: column; gap: 14px; }
  .comp-card {
    background: #FDFAF6; border: 1.5px solid rgba(31,42,68,0.1);
    border-radius: 16px; padding: 16px 18px; cursor: pointer;
    box-shadow: 3px 3px 0px rgba(31,42,68,0.06); transition: all 0.2s;
    position: relative; overflow: hidden;
  }
  .comp-card:hover { transform: translateY(-2px) translateX(-1px); box-shadow: 5px 5px 0px rgba(31,42,68,0.1); }
  .comp-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 16px 0 0 16px;
  }
  .comp-card.c1::before { background: #FFC857; }
  .comp-card.c2::before { background: #A3C9A8; }
  .comp-card.c3::before { background: #B8A8E3; }

  .comp-num {
    font-size: 10px; font-weight: 800; letter-spacing: 0.5px;
    background: #E8E4DC; border-radius: 6px; padding: 2px 6px;
    color: rgba(31,42,68,0.6); display: inline-block; margin-bottom: 6px;
  }
  .comp-name { font-weight: 900; font-size: 16px; color: #1F2A44; margin-bottom: 8px; }
  .comp-desc { font-size: 13px; color: rgba(31,42,68,0.7); line-height: 1.5; margin-bottom: 10px; }
  .comp-desc .highlight-text {
    background: #FFE5A0; border-radius: 3px; padding: 0 3px; font-weight: 700;
    color: #1F2A44;
  }
  .comp-desc .highlight-purple {
    background: #E8E0FF; border-radius: 3px; padding: 0 3px; font-weight: 700;
    color: #4A3B8C;
  }
  .comp-desc .highlight-green {
    background: #C8E6CB; border-radius: 3px; padding: 0 3px; font-weight: 700;
    color: #1F5732;
  }
  .comp-tags { display: flex; flex-wrap: wrap; gap: 6px; }
  .comp-tag {
    padding: 3px 10px; border-radius: 50px; font-size: 11px; font-weight: 700;
    background: #E8E4DC; color: rgba(31,42,68,0.65); border: 1.5px solid rgba(31,42,68,0.1);
  }

  /* Right: Gap Opportunities */
  .gap-section {}
  .gap-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
  .gap-title { font-weight: 900; font-size: 22px; color: #1F2A44; }
  .reanalyze-btn {
    display: flex; align-items: center; gap: 6px; padding: 6px 14px;
    background: transparent; border: 1.5px solid rgba(31,42,68,0.2); border-radius: 50px;
    font-family: 'Nunito', sans-serif; font-size: 12px; font-weight: 700; color: rgba(31,42,68,0.6);
    cursor: pointer; transition: all 0.15s;
  }
  .reanalyze-btn:hover { background: rgba(255,255,255,0.5); color: #1F2A44; }

  .gap-grid { display: flex; flex-direction: column; gap: 14px; }

  .gap-card {
    border-radius: 16px; padding: 18px;
    border: 1.5px solid rgba(31,42,68,0.1);
    box-shadow: 3px 3px 0px rgba(31,42,68,0.07); cursor: pointer; transition: all 0.2s;
    position: relative;
  }
  .gap-card:hover { transform: translateY(-2px); box-shadow: 5px 5px 0px rgba(31,42,68,0.1); }

  .gap-card.missing-kw { background: #C8F0D0; border-color: rgba(45,106,79,0.2); }
  .gap-card.weak-sections { background: #D4C8F5; border-color: rgba(107,87,196,0.2); }
  .gap-card.goldmine { background: #FFC857; border-color: rgba(31,42,68,0.15); }
  .gap-card.prediction { background: #FDFAF6; border-color: rgba(31,42,68,0.12); }

  .gap-meta {
    display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 10px;
    font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; color: rgba(31,42,68,0.5);
  }
  .priority-dot { width: 8px; height: 8px; background: #2D6A4F; border-radius: 50%; }

  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

  .gap-card-title { font-weight: 900; font-size: 18px; color: #1F2A44; margin-bottom: 6px; }
  .gap-card-body { font-size: 13px; color: rgba(31,42,68,0.75); line-height: 1.5; }
  .gap-card-body a { color: #4A3B8C; font-weight: 700; text-decoration: underline; cursor: pointer; }

  .kw-list { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
  .kw-item { font-size: 12px; font-weight: 700; color: #1F5732; font-style: italic; }

  .added-badge {
    display: inline-flex; align-items: center; gap: 4px; margin-top: 8px;
    background: rgba(31,42,68,0.1); border-radius: 50px; padding: 3px 10px;
    font-size: 10px; font-weight: 700; color: rgba(31,42,68,0.6);
  }
  .added-dot { width: 6px; height: 6px; background: #2D6A4F; border-radius: 50%; }

  .puzzle-icon { font-size: 20px; margin-bottom: 8px; display: block; }

  .prediction-quote {
    font-family: 'Caveat', cursive;
    font-size: 15px; color: rgba(31,42,68,0.8); line-height: 1.6;
    font-style: italic; border-left: 3px solid #FFC857; padding-left: 12px;
  }
  .prediction-icon { font-size: 18px; display: flex; align-items: flex-start; justify-content: flex-start; gap: 10px; }

  /* Bottom CTA */
  .bottom-cta {
    display: flex; flex-direction: column; align-items: center; gap: 12px;
    margin-top: 48px; padding-top: 24px; border-top: 1.5px dashed rgba(31,42,68,0.1);
  }
  .inject-btn {
    background: #FFC857; border: 2px solid #1F2A44;
    border-radius: 50px; padding: 14px 36px;
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 16px; color: #1F2A44;
    cursor: pointer; box-shadow: 5px 5px 0px rgba(31,42,68,0.2);
    transition: all 0.2s; display: flex; align-items: center; gap: 10px;
  }
  .inject-btn:hover { transform: translateY(-3px); box-shadow: 8px 8px 0px rgba(31,42,68,0.25); }
  .inject-btn:active { transform: translateY(0); box-shadow: 3px 3px 0px rgba(31,42,68,0.2); }

  .powered-by {
    font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
    color: rgba(31,42,68,0.35);
  }

  .doodle-img {
    position: fixed; bottom: 60px; right: 20px; font-size: 48px; opacity: 0.12;
    transform: rotate(10deg); pointer-events: none; user-select: none;
  }
`;

export default function SerpPage({ activePage = "strategic-map", onNavigate }) {
  const [showProfile, setShowProfile] = useState(false);
  const { serpData, loading, errors, actions, blogResult } = useWorkflow();
  const [searchKeyword, setSearchKeyword] = useState(blogResult?.keyword || "");
  const [competitorUrls, setCompetitorUrls] = useState([]);
  const [localError, setLocalError] = useState(null);

  const effectiveKeyword = serpData?.keyword || searchKeyword;

  const loadSerpAnalysis = async (kw = effectiveKeyword) => {
    setLocalError(null);
    try {
      return await actions.runSerpAnalysis({
        keyword: kw,
        target_location: "India",
        competitor_urls: competitorUrls,
      });
    } catch (err) {
      let errorMsg = "Failed to load SERP analysis";
      if (err instanceof Error) {
        errorMsg = err.message;
      } else if (err?.payload?.detail) {
        errorMsg = err.payload.detail;
      } else if (typeof err === "string") {
        errorMsg = err;
      } else if (err && typeof err === "object") {
        try {
          errorMsg = JSON.stringify(err);
        } catch {
          errorMsg = "SERP analysis failed: Unknown error";
        }
      }
      console.error("SERP analysis failed:", errorMsg, "Full error:", err);
      setLocalError(errorMsg);
      return null;
    }
  };

  useEffect(() => {
    if (!serpData) {
      loadSerpAnalysis(searchKeyword);
    }
  }, []);

  const isAnalyzing = !!loading.serpAnalysis;

  const handleRunSerpAnalysis = async () => {
    await loadSerpAnalysis(searchKeyword);
  };

  const handleInjectAndGenerate = async () => {
    try {
      let analysis = serpData;
      if (!analysis) {
        analysis = await loadSerpAnalysis(searchKeyword);
      }

      if (!analysis) {
        setLocalError("SERP analysis is required to generate the blog.");
        return;
      }

      const payload = {
        keyword: (analysis.keyword || searchKeyword || "").trim(),
        secondary_keywords: [],
        target_location: analysis.target_location || "India",
        word_count: analysis.recommended_word_count || 2500,
        tone: "professional",
        competitor_urls: competitorUrls,
        internal_links: [],
        enable_humanization: true,
        serp_analysis: analysis,
      };

      await actions.generateBlog(payload);
      onNavigate?.("blog-gen");
    } catch (err) {
      console.error("Inject and generate blog failed", err);
      setLocalError(err.message || "Blog generation failed");
    }
  };

  return (
    <>
      <style>{serpStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          {/* Topbar */}
          <div className="topbar">
            <div className="topbar-search">
              <span>🔍</span>
              <input
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRunSerpAnalysis()}
                placeholder="Search insights..."
              />
            </div>
            <div className="topbar-search" style={{ maxWidth: "400px" }}>
              <span>🔗</span>
              <input
                value={competitorUrls.join(", ")}
                onChange={(e) =>
                  setCompetitorUrls(
                    e.target.value
                      .split(",")
                      .map((url) => url.trim())
                      .filter((url) => url),
                  )
                }
                placeholder="Add competitor blog URLs (optional, comma-separated)"
              />
            </div>
            <button
              className="reanalyze-btn"
              onClick={handleRunSerpAnalysis}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? "Analyzing..." : "🔄 Re-analyze"}
            </button>
            <span className="badge badge-geo">GEO READY</span>
            <span className="badge badge-seo">SEO ENGINE ON</span>
            <div className="topbar-right">
              <div className="topbar-greeting">Good morning, Aryan 👊</div>
              <div className="topbar-bell">🔔</div>
              <div
                className="topbar-avatar"
                onClick={() => setShowProfile((v) => !v)}
              >
                <img
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=aryan&backgroundColor=b6e3f4"
                  style={{ width: "100%", height: "100%" }}
                  alt="av"
                />
              </div>
              {showProfile && (
                <ProfileOverlay
                  onClose={() => setShowProfile(false)}
                  onNavigate={onNavigate}
                />
              )}
            </div>
          </div>

          <div className="page-body">
            {/* Header */}
            <div className="page-header">
              <h1 className="page-title">SERP Gap Analysis</h1>
              <p className="page-desc">
                We've dissected the top 5 competitors for{" "}
                <span className="highlight">"{effectiveKeyword}"</span>. Here's
                where they're winning, and where you can strike.
                {serpData && (
                  <>
                    {" "}
                    Analyzed {serpData.results?.length || 0} competitors, found{" "}
                    {serpData.missing_keywords?.length || 0} keyword gaps,{" "}
                    {competitorUrls.length} external blogs used.
                  </>
                )}
              </p>
              <div className="doodle-arrow">→</div>
            </div>

            {localError && (
              <div
                style={{
                  margin: "0 24px 12px",
                  padding: "12px 16px",
                  borderRadius: "10px",
                  background: "#ffe6e6",
                  color: "#a00000",
                  border: "1px solid #ffb3b3",
                }}
              >
                ⚠️ {localError}
              </div>
            )}

            <div className="main-grid">
              {/* Left col */}
              <div className="comp-section">
                <div className="comp-header">
                  <div className="comp-title">Competitor Landscape</div>
                  <div className="sources-badge">
                    {serpData?.results?.length || 0} SERP sources analyzed
                  </div>
                </div>

                <div className="center-diagram">
                  <div className="opportunity-circle">
                    YOUR CONTENT
                    <br />
                    OPPORTUNITY
                  </div>
                  <div className="opp-arrow">↗</div>
                </div>

                <div className="comp-list">
                  {serpData?.results?.length ? (
                    serpData.results.map((item, index) => (
                      <div
                        className={`comp-card c${(index % 3) + 1}`}
                        key={item.url || index}
                      >
                        <div className="comp-num">
                          {String(index + 1).padStart(2, "0")}
                        </div>
                        <div className="comp-name">
                          {item.title || "Untitled competitor"}
                        </div>
                        <div className="comp-desc">
                          {item.snippet ||
                            item.summary ||
                            "No snippet available."}
                        </div>
                        <div className="comp-tags">
                          <span className="comp-tag">
                            {item.content_type ||
                              item.serp_personality ||
                              "Unknown format"}
                          </span>
                          <span className="comp-tag">
                            {item.word_count_estimate
                              ? `${item.word_count_estimate} words`
                              : "Word count unk"}
                          </span>
                          {item.has_featured_snippet && (
                            <span className="comp-tag">Featured snippet</span>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="comp-card c1">
                      <div className="comp-num">--</div>
                      <div className="comp-name">No competitor data yet</div>
                      <div className="comp-desc">
                        Run SERP analysis to load the top competitors.
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Right col */}
              <div className="gap-section">
                <div className="gap-header">
                  <div className="gap-title">Gap Opportunities</div>
                  <button
                    className="reanalyze-btn"
                    onClick={handleRunSerpAnalysis}
                  >
                    {isAnalyzing ? "Analyzing..." : "🔄 Re-analyze"}
                  </button>
                </div>

                <div className="gap-grid">
                  {/* Two col top */}
                  <div className="two-col">
                    <div className="gap-card missing-kw">
                      <div className="gap-meta">
                        <div className="priority-dot" />
                        PRIORITY: HIGH
                      </div>
                      <div className="gap-card-title">Missing Keywords</div>
                      <div className="kw-list">
                        {serpData?.missing_keywords?.length > 0 ? (
                          serpData.missing_keywords.slice(0, 8).map((kw, i) => (
                            <span key={i} className="kw-item">
                              {kw}
                            </span>
                          ))
                        ) : (
                          <span className="kw-item">
                            Run analysis to load missing keyword opportunities.
                          </span>
                        )}
                      </div>
                      <div className="added-badge">
                        <div className="added-dot" /> Recommended for working
                        into headings and bullets
                      </div>
                    </div>

                    <div className="gap-card weak-sections">
                      <div className="gap-meta">▤ STYLE GAP</div>
                      <div className="gap-card-title">
                        {serpData?.content_gap_summary?.title ||
                          "Pending insight generation"}
                      </div>

                      <div className="gap-card-body">
                        {serpData?.content_gap_summary?.description ||
                          "Run SERP analysis to extract the primary content gap summary."}
                      </div>
                      <div className="gap-card-body">
                        {serpData?.weak_sections?.length > 0 ? (
                          serpData.weak_sections.slice(0, 5).map((w, i) => (
                            <div key={i}>
                              Competitors are weak on <strong>{w}</strong> — you
                              should include this with depth.
                            </div>
                          ))
                        ) : (
                          <div>No weak sections detected yet.</div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Goldmine REMOVED - now using content_gap_summary in weak-sections card */}

                  {/* Prediction */}
                  <div className="gap-card prediction">
                    <div className="prediction-icon">
                      <span>💡</span>
                      <div className="prediction-quote">
                        {serpData?.serp_personality
                          ? `Top competitors are mostly ${serpData.serp_personality}. To outperform them, add deep coverage on: ${serpData.weak_sections?.slice(0, 3).join(", ") || "N/A"}.`
                          : "Run analysis and get strategic TODOs for your blog."}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div
              className="gap-card"
              style={{
                marginBottom: 20,
                borderColor: "rgba(31,42,68,0.18)",
                background: "rgba(255,255,255,0.92)",
              }}
            >
              <div className="gap-meta">🎯 Actionable SEO Plan</div>
              <div className="gap-card-body">
                <strong>What to add:</strong>
                <ul>
                  {(serpData?.missing_keywords?.slice(0, 4) || []).map(
                    (kw, i) => (
                      <li key={`addkw-${i}`}>
                        Include keyword: <strong>{kw}</strong> in your H2/H3 and
                        intro.
                      </li>
                    ),
                  )}
                  {(serpData?.weak_sections?.slice(0, 3) || []).map((s, i) => (
                    <li key={`addsec-${i}`}>
                      Cover the weak section: <strong>{s}</strong> with example
                      use cases.
                    </li>
                  ))}
                  {!serpData?.missing_keywords?.length &&
                    !serpData?.weak_sections?.length && (
                      <li>
                        Keep the existing structure, but run SERP again for the
                        latest findings.
                      </li>
                    )}
                </ul>
                <strong>Why this matters:</strong>
                <p>
                  {serpData?.content_gap_summary?.description ||
                    "Your blog should capitalize on uncovered angles competitors missed to win SERP visibility."}
                </p>
              </div>
            </div>

            {/* Bottom CTA */}
            <div className="bottom-cta">
              <button
                className="inject-btn"
                onClick={handleInjectAndGenerate}
                disabled={isAnalyzing || loading.blogGeneration}
              >
                {loading.blogGeneration
                  ? "Generating..."
                  : "🚀 Generate Blog from SERP"}
              </button>
              <div className="powered-by">
                Powered by The Analyst Engine v4.2
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="doodle-img">✏️</div>
    </>
  );
}
