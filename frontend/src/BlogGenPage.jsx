import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Sidebar from "./components/Sidebar";
import { useWorkflow } from "./context/WorkflowContext";

const genStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body, html { font-family: 'Nunito', sans-serif; background: #F5EBDD; color: #1F2A44; }

  .app-shell { display: flex; height: 100vh; overflow: hidden; background: #F5EBDD; }
  .main-content {
    flex: 1; overflow-y: auto; background: #F5EBDD;
    background-image:
      linear-gradient(rgba(31,42,68,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(31,42,68,0.03) 1px, transparent 1px);
    background-size: 28px 28px;
  }

  /* Step Progress */
  .step-progress {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    padding: 16px 24px; border-bottom: 1.5px dashed rgba(31,42,68,0.1);
    background: rgba(245,235,221,0.5);
  }
  .step {
    display: flex; align-items: center; gap: 8px; padding: 8px 18px;
    border-radius: 12px; font-size: 13px; font-weight: 700; color: rgba(31,42,68,0.45);
    border: 1.5px solid transparent; position: relative;
  }
  .step.done { color: rgba(31,42,68,0.5); background: rgba(31,42,68,0.05); }
  .step.active {
    background: #FFC857; color: #1F2A44;
    border: 2px solid #1F2A44;
    box-shadow: 3px 3px 0px rgba(31,42,68,0.2);
    transform: translateY(-2px);
  }
  .step.active::before {
    content: 'ZONE';
    position: absolute; top: -10px; right: 4px;
    background: #F4A4A4; color: #1F2A44;
    font-size: 8px; font-weight: 800; letter-spacing: 0.5px;
    padding: 2px 5px; border-radius: 4px; border: 1px solid rgba(31,42,68,0.2);
  }
  .step-num { font-size: 10px; opacity: 0.7; }
  .step-arrow { color: rgba(31,42,68,0.25); font-size: 18px; }

  /* Page body */
  .page-body { display: flex; gap: 0; height: calc(100vh - 64px); overflow: hidden; }

  /* Left: Keyword Config */
  .kw-panel {
    width: 260px; flex-shrink: 0; padding: 20px 16px; border-right: 1.5px dashed rgba(31,42,68,0.12);
    overflow-y: auto; background: rgba(245,235,221,0.3);
  }
  .panel-section { margin-bottom: 16px; }
  .panel-label {
    font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
    color: rgba(31,42,68,0.45); margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
  }
  .kw-panel-title { font-weight: 900; font-size: 17px; color: #1F2A44; margin-bottom: 20px; display: flex; align-items: center; gap: 6px; }

  .gen-input {
    width: 100%; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 10px;
    padding: 9px 12px; font-family: 'Nunito', sans-serif; font-size: 13px;
    color: #1F2A44; background: #FDFAF6; outline: none;
  }
  .gen-input:focus { border-color: #FFC857; }
  .gen-input::placeholder { color: #9AA5B4; }

  .gen-select {
    width: 100%; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 10px;
    padding: 9px 12px; font-family: 'Nunito', sans-serif; font-size: 13px;
    color: #1F2A44; background: #FDFAF6; outline: none; cursor: pointer;
  }

  .gen-checkbox-row {
    display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #1F2A44;
  }
  .gen-checkbox-row input[type="checkbox"] { accent-color: #FFC857; width: 16px; height: 16px; }

  .generate-btn {
    width: 100%; padding: 13px; background: #FFC857; border: 2px solid #1F2A44;
    border-radius: 12px; font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 14px;
    color: #1F2A44; cursor: pointer; box-shadow: 3px 3px 0px rgba(31,42,68,0.2);
    transition: all 0.15s; display: flex; align-items: center; justify-content: center; gap: 6px;
    margin-top: 10px;
  }
  .generate-btn:hover { transform: translateY(-2px); box-shadow: 5px 5px 0px rgba(31,42,68,0.25); }
  .generate-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: 3px 3px 0px rgba(31,42,68,0.2); }

  .gen-error { color: #b3261e; font-size: 12px; font-weight: 700; margin-top: 6px; }

  /* Center: Blog preview */
  .blog-preview-panel {
    flex: 1; padding: 24px 20px; overflow-y: auto; position: relative;
  }

  .blog-preview-card {
    background: #FDFAF6;
    border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 18px;
    padding: 28px 28px 28px;
    box-shadow: 4px 4px 0px rgba(31,42,68,0.08);
    position: relative;
    min-height: 360px;
  }

  .blog-score-badge {
    position: absolute; top: 16px; right: 16px;
    background: #FFC857; border: 2px solid #1F2A44;
    border-radius: 10px; padding: 6px 12px;
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 13px; color: #1F2A44;
    display: flex; align-items: center; gap: 6px;
    box-shadow: 2px 2px 0px rgba(31,42,68,0.2);
  }
  .score-label { font-size: 9px; font-weight: 700; letter-spacing: 0.5px; opacity: 0.7; }

  .snippet-ready {
    display: inline-block; background: #C8E6CB; border: 1.5px solid #2D6A4F;
    border-radius: 50px; padding: 3px 10px; font-size: 10px; font-weight: 800;
    color: #1F5732; letter-spacing: 0.5px; margin-bottom: 12px;
  }

  .blog-title-display {
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 26px;
    color: #1F2A44; line-height: 1.25; margin-bottom: 8px;
  }
  .blog-meta-desc {
    font-size: 13px; color: rgba(31,42,68,0.6); font-style: italic; margin-bottom: 16px;
    padding: 8px 12px; background: rgba(31,42,68,0.03); border-radius: 8px;
  }
  .blog-body {
    font-size: 14px; color: rgba(31,42,68,0.75); line-height: 1.8;
  }
  .blog-body h1 { font-size: 28px; font-weight: 900; margin: 20px 0 12px; color: #1F2A44; }
  .blog-body h2 { font-size: 22px; font-weight: 900; margin: 18px 0 10px; color: #1F2A44; border-bottom: 2px solid rgba(31,42,68,0.1); padding-bottom: 8px; }
  .blog-body h3 { font-size: 18px; font-weight: 800; margin: 14px 0 8px; color: #1F2A44; }
  .blog-body h4 { font-size: 15px; font-weight: 800; margin: 12px 0 6px; color: #1F2A44; }
  .blog-body p { margin-bottom: 14px; }
  .blog-body strong { font-weight: 800; color: #1F2A44; }
  .blog-body em { font-style: italic; }
  .blog-body ul, .blog-body ol { margin: 12px 0 12px 24px; }
  .blog-body li { margin-bottom: 8px; }
  .blog-body table { width: 100%; border-collapse: collapse; margin: 16px 0; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 8px; }
  .blog-body th { background: rgba(31,42,68,0.08); padding: 12px; text-align: left; font-weight: 800; border-bottom: 2px solid rgba(31,42,68,0.15); }
  .blog-body td { padding: 12px; border-bottom: 1px solid rgba(31,42,68,0.1); }
  .blog-body tr:last-child td { border-bottom: none; }
  .blog-body blockquote { margin: 14px 0; padding: 12px 16px; border-left: 4px solid #FFC857; background: rgba(255,200,87,0.08); }
  .blog-body code { background: rgba(31,42,68,0.05); padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; }
  .blog-body pre { background: rgba(31,42,68,0.08); padding: 12px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }
  .blog-body pre code { background: none; padding: 0; }
  .blog-body a { color: #6B5FD4; text-decoration: none; font-weight: 700; }
  .blog-body a:hover { text-decoration: underline; }

  .blog-placeholder {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 300px; color: rgba(31,42,68,0.4); text-align: center; gap: 12px;
  }
  .blog-placeholder-icon { font-size: 48px; opacity: 0.5; }
  .blog-placeholder-text { font-size: 16px; font-weight: 700; }
  .blog-placeholder-sub { font-size: 13px; max-width: 320px; line-height: 1.5; }

  .blog-gen-time {
    margin-top: 16px; padding-top: 12px; border-top: 1.5px dashed rgba(31,42,68,0.1);
    font-size: 12px; color: rgba(31,42,68,0.5); display: flex; gap: 16px;
  }
  .blog-gen-time span { font-weight: 700; }

  /* Hashnode Publishing */
  .hashnode-section {
    margin-top: 20px; padding-top: 20px; border-top: 2px solid rgba(255,200,87,0.3);
  }
  .hashnode-title {
    font-size: 13px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
    color: rgba(31,42,68,0.6); margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
  }
  .hashnode-checkbox-row {
    display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600;
    color: #1F2A44; margin-bottom: 12px;
  }
  .hashnode-checkbox-row input[type="checkbox"] { accent-color: #FFC857; width: 16px; height: 16px; cursor: pointer; }
  .hashnode-tags-input {
    width: 100%; border: 1.5px solid rgba(31,42,68,0.15); border-radius: 10px;
    padding: 9px 12px; font-family: 'Nunito', sans-serif; font-size: 12px;
    color: #1F2A44; background: #FDFAF6; outline: none; margin-bottom: 12px;
  }
  .hashnode-tags-input:focus { border-color: #FFC857; }
  .hashnode-tags-input::placeholder { color: #9AA5B4; }
  .hashnode-tag-hint {
    font-size: 11px; color: rgba(31,42,68,0.45); margin-bottom: 12px; font-style: italic;
  }
  .publish-btn {
    width: 100%; padding: 11px; background: rgba(255,200,87,0.9); border: 2px solid #1F2A44;
    border-radius: 10px; font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 13px;
    color: #1F2A44; cursor: pointer; box-shadow: 2px 2px 0px rgba(31,42,68,0.15);
    transition: all 0.15s; display: flex; align-items: center; justify-content: center; gap: 6px;
  }
  .publish-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 3px 3px 0px rgba(31,42,68,0.2); }
  .publish-btn:disabled { opacity: 0.6; cursor: not-allowed; }
  .hashnode-success {
    margin-top: 12px; padding: 12px; background: #C8E6CB; border: 1.5px solid #2D6A4F;
    border-radius: 8px; color: #1F5732; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; gap: 8px;
  }
  .hashnode-error {
    margin-top: 12px; padding: 12px; background: #F8DEDC; border: 1.5px solid #B3261E;
    border-radius: 8px; color: #B3261E; font-size: 12px; font-weight: 700;
  }
  .hashnode-link {
    color: #6B5FD4; text-decoration: none; font-weight: 700; word-break: break-all;
  }
  .hashnode-link:hover { text-decoration: underline; }

  /* Right: SEO validation - REMOVED */

  /* AI Detection - REMOVED */
`;

export default function BlogGenPage({ activePage = "blog-gen", onNavigate }) {
  const {
    blogResult,
    loading,
    errors,
    actions,
    serpData,
    serpAnalysis,
    keywordClusters,
  } = useWorkflow();

  const [form, setForm] = useState({
    keyword: "",
    secondary_keywords: "",
    competitor_urls: "",
    target_location: "India",
    word_count: 2500,
    tone: "professional",
    enable_humanization: true,
  });

  // Hashnode state
  const [hashnode, setHashnode] = useState({
    tags: "",
    publishing: false,
    result: null,
    error: null,
  });

  useEffect(() => {
    const data = serpAnalysis || serpData;
    if (data?.keyword) {
      setForm((prev) => ({
        ...prev,
        keyword: data.keyword,
      }));
    }
  }, [serpAnalysis, serpData]);

  const activeStep = loading.blogGeneration ? 2 : blogResult?.content ? 3 : 1;
  const steps = [
    { num: "01", label: "Keyword Input" },
    { num: "02", label: "Generating" },
    { num: "03", label: "Blog Output" },
  ];

  const handleGenerate = async (e) => {
    e.preventDefault();

    if (!form.keyword.trim()) return;

    await actions.generateBlog({
      keyword: form.keyword.trim(),

      secondary_keywords: form.secondary_keywords
        ? form.secondary_keywords
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [],

      target_location: form.target_location,
      word_count: Number(form.word_count) || 2500,
      tone: form.tone,
      enable_humanization: form.enable_humanization,
      competitor_urls: form.competitor_urls
        ? form.competitor_urls
            .split(",")
            .map((url) => url.trim())
            .filter(Boolean)
        : [],

      // 🔥 This uses the current SERP analysis context if available
      serp_analysis: serpAnalysis || serpData || null,
    });
    // Reset Hashnode state on new generation
    setHashnode({ tags: "", publishing: false, result: null, error: null });
  };

  const handlePublishHashnode = async () => {
    if (!blogResult?.blog_id) {
      setHashnode((p) => ({
        ...p,
        error:
          "No blog ID found. Your blog may not have been saved to MongoDB, so publishing is blocked. Check backend logs and Mongo connection settings.",
      }));
      return;
    }

    setHashnode((p) => ({ ...p, publishing: true, error: null }));

    try {
      const tagsArray = hashnode.tags
        ? hashnode.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
            .slice(0, 5)
        : [];

      const response = await fetch(
        `http://localhost:8000/blog/${blogResult.blog_id}/publish-hashnode`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tags: tagsArray }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setHashnode((p) => ({
          ...p,
          error: data.detail || "Failed to publish",
        }));
      } else {
        setHashnode((p) => ({
          ...p,
          result: data,
          error: null,
        }));
      }
    } catch (err) {
      setHashnode((p) => ({ ...p, error: err.message }));
    } finally {
      setHashnode((p) => ({ ...p, publishing: false }));
    }
  };

  const seo = blogResult?.seo_score;
  const ai = blogResult?.ai_detection;
  const snippet = blogResult?.snippet_optimization;

  const getVerdictClass = (verdict) => {
    if (!verdict) return "";
    if (verdict === "likely_human") return "verdict-human";
    if (verdict === "borderline") return "verdict-borderline";
    return "verdict-ai";
  };

  const getBarColor = (value) => {
    if (value >= 70) return "#A3C9A8";
    if (value >= 40) return "#FFC857";
    return "#F4A4A4";
  };

  return (
    <>
      <style>{genStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          {/* Step Progress */}
          <div className="step-progress">
            {steps.map((s, i) => (
              <span key={s.num} style={{ display: "contents" }}>
                <div
                  className={`step ${i + 1 === activeStep ? "active" : i + 1 < activeStep ? "done" : ""}`}
                >
                  <span className="step-num">{s.num}</span> {s.label}
                </div>
                {i < steps.length - 1 && <span className="step-arrow">→</span>}
              </span>
            ))}
          </div>

          <div className="page-body">
            {/* Left Panel — Form */}
            <div className="kw-panel">
              <div className="kw-panel-title">
                🏷 Blog Config {serpData ? "✨ (SERP Enhanced)" : ""}
              </div>

              <form onSubmit={handleGenerate}>
                <div className="panel-section">
                  <div className="panel-label">Primary Keyword *</div>
                  <input
                    className="gen-input"
                    value={form.keyword}
                    onChange={(e) =>
                      setForm((p) => ({ ...p, keyword: e.target.value }))
                    }
                    placeholder="e.g. sustainable architecture"
                    required
                  />
                </div>

                <div className="panel-section">
                  <div className="panel-label">Secondary Keywords</div>
                  <input
                    className="gen-input"
                    value={form.secondary_keywords}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        secondary_keywords: e.target.value,
                      }))
                    }
                    placeholder="comma separated"
                  />
                </div>

                <div className="panel-section">
                  <div className="panel-label">
                    Add Competitor Blog URLs (optional)
                  </div>
                  <input
                    className="gen-input"
                    value={form.competitor_urls}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        competitor_urls: e.target.value,
                      }))
                    }
                    placeholder="comma separated URLs"
                  />
                </div>

                <div className="panel-section">
                  <div className="panel-label">Target Location</div>
                  <input
                    className="gen-input"
                    value={form.target_location}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        target_location: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="panel-section">
                  <div className="panel-label">Word Count</div>
                  <input
                    type="number"
                    className="gen-input"
                    min={800}
                    max={5000}
                    value={form.word_count}
                    onChange={(e) =>
                      setForm((p) => ({ ...p, word_count: e.target.value }))
                    }
                  />
                </div>

                <div className="panel-section">
                  <div className="panel-label">Tone of Voice</div>
                  <select
                    className="gen-select"
                    value={form.tone}
                    onChange={(e) =>
                      setForm((p) => ({ ...p, tone: e.target.value }))
                    }
                  >
                    <option value="professional">Professional</option>
                    <option value="conversational">Conversational</option>
                    <option value="authoritative">Authoritative</option>
                  </select>
                </div>

                <div className="panel-section">
                  <label className="gen-checkbox-row">
                    <input
                      type="checkbox"
                      checked={form.enable_humanization}
                      onChange={(e) =>
                        setForm((p) => ({
                          ...p,
                          enable_humanization: e.target.checked,
                        }))
                      }
                    />
                    Enable Humanization
                  </label>
                </div>

                {errors.blogGeneration && (
                  <div className="gen-error">{errors.blogGeneration}</div>
                )}

                <button
                  className="generate-btn"
                  type="submit"
                  disabled={loading.blogGeneration}
                >
                  {loading.blogGeneration
                    ? "⏳ Generating..."
                    : blogResult?.content
                      ? "🔄 Regenerate Blog"
                      : "🚀 Generate Blog"}
                </button>
              </form>
            </div>

            {/* Center Panel — Blog Preview */}
            <div className="blog-preview-panel">
              {blogResult?.content ? (
                <div className="blog-preview-card">
                  {seo && (
                    <div className="blog-score-badge">
                      <div>
                        <div className="score-label">SEO SCORE</div>
                        <div>{Math.round(seo.overall_score)}</div>
                      </div>
                    </div>
                  )}

                  {snippet && snippet.readiness_probability >= 60 && (
                    <div className="snippet-ready">
                      SNIPPET READY ({Math.round(snippet.readiness_probability)}
                      %)
                    </div>
                  )}

                  <h1 className="blog-title-display">{blogResult.title}</h1>

                  {blogResult.meta_description && (
                    <div className="blog-meta-desc">
                      {blogResult.meta_description}
                    </div>
                  )}

                  <div className="blog-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {blogResult.content.replace(/^#\s+.+\n/, "")}
                    </ReactMarkdown>
                  </div>

                  <div className="blog-gen-time">
                    <div>
                      ⏱ <span>{blogResult.generation_time_seconds}s</span>
                    </div>
                    <div>
                      📝 <span>{blogResult.word_count} words</span>
                    </div>
                    <div>
                      🤖 <span>{blogResult.model_used}</span>
                    </div>
                    <div>
                      🔗{" "}
                      <span>
                        {blogResult.external_links_used || 0} external blogs used
                      </span>
                    </div>
                  </div>

                  {/* Hashnode Publishing Section */}
                  <div className="hashnode-section">
                    <div className="hashnode-title">📤 Publish to Hashnode</div>

                    {!hashnode.result ? (
                      <>
                        <input
                          type="text"
                          className="hashnode-tags-input"
                          value={hashnode.tags}
                          onChange={(e) =>
                            setHashnode((p) => ({ ...p, tags: e.target.value }))
                          }
                          placeholder="Tags (comma-separated, max 5). e.g. ai, tech, blog"
                          disabled={hashnode.publishing}
                        />
                        <div className="hashnode-tag-hint">
                          💡 Add relevant tags to increase visibility on
                          Hashnode
                        </div>

                        <button
                          className="publish-btn"
                          onClick={handlePublishHashnode}
                          disabled={hashnode.publishing}
                        >
                          {hashnode.publishing
                            ? "📤 Publishing..."
                            : "🚀 Publish to Hashnode"}
                        </button>

                        {hashnode.error && (
                          <div className="hashnode-error">
                            ❌ {hashnode.error}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="hashnode-success">
                        <div>
                          ✅ Published to Hashnode!{" "}
                          {hashnode.result.status === "already_published" &&
                            "(Already published)"}
                        </div>
                        <a
                          href={hashnode.result.hashnode_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hashnode-link"
                        >
                          📖 Read on Hashnode →
                        </a>
                      </div>
                    )}
                  </div>

                  {(serpAnalysis || serpData) && (
                    <div
                      style={{
                        marginTop: 16,
                        padding: "14px",
                        borderRadius: 12,
                        background: "#EFEFEF",
                        border: "1px solid rgba(31,42,68,0.15)",
                      }}
                    >
                      <div style={{ fontWeight: 800, marginBottom: 8 }}>
                        🕵️‍♀️ SERP Gap Insights
                      </div>
                      <div>
                        <strong>Dominant Format:</strong>{" "}
                        {(serpAnalysis || serpData).serp_personality}
                      </div>
                      <div>
                        <strong>Winning Angle:</strong>{" "}
                        {(serpAnalysis || serpData).winning_angle}
                      </div>
                      <div>
                        <strong>Recommend Size:</strong>{" "}
                        {(serpAnalysis || serpData).recommended_word_count}{" "}
                        words
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <strong>Top Gaps:</strong>{" "}
                        {(serpAnalysis || serpData).content_gaps
                          ?.slice(0, 4)
                          .join(", ") || "None detected"}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="blog-preview-card">
                  <div className="blog-placeholder">
                    <div className="blog-placeholder-icon">✍️</div>
                    <div className="blog-placeholder-text">
                      {loading.blogGeneration
                        ? "Generating your blog..."
                        : "No blog generated yet"}
                    </div>
                    <div className="blog-placeholder-sub">
                      {loading.blogGeneration
                        ? "Running keyword clustering, SERP analysis, content generation, SEO optimization, and humanization pipeline..."
                        : "Fill in the keyword config on the left and hit Generate Blog to start the AI pipeline."}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Panel — SEO Validation */}
          </div>
        </div>
      </div>
    </>
  );
}
