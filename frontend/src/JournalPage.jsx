import { useState, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Sidebar from "./components/Sidebar";
import ProfileOverlay from "./components/ProfileOverlay";
import { useWorkflow } from "./context/WorkflowContext";
import { api } from "./api/client";

// ── Styles ─────────────────────────────────────────────────────────────────
const journalStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body, html { font-family: 'Nunito', sans-serif; background: #F5EBDD; color: #1F2A44; }
  
  .app-shell { display: flex; height: 100vh; overflow: hidden; background: #F5EBDD; }
  
  .main-content {
    flex: 1; overflow-y: auto; background: #F5EBDD;
    background-image: 
      linear-gradient(rgba(31,42,68,0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(31,42,68,0.035) 1px, transparent 1px);
    background-size: 28px 28px;
  }

  .topbar {
    display: flex; align-items: center; gap: 16px; padding: 12px 24px;
    background: rgba(245,235,221,0.92); backdrop-filter: blur(4px);
    border-bottom: 1.5px dashed rgba(31,42,68,0.12); position: sticky; top: 0; z-index: 100;
  }
  .badge { padding: 5px 12px; border-radius: 50px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; border: 1.5px solid; }
  .badge-geo { background: #C8E6CB; color: #2D6A4F; border-color: #2D6A4F; }
  .badge-seo { background: #FFF3CD; color: #92681A; border-color: #92681A; }
  .topbar-right { margin-left: auto; display: flex; align-items: center; gap: 12px; }
  .topbar-greeting { font-weight: 700; font-size: 14px; color: #1F2A44; }
  .topbar-avatar { width: 36px; height: 36px; border-radius: 50%; border: 2px solid #1F2A44; overflow: hidden; cursor: pointer; }
  .bell-wrap { position: relative; cursor: pointer; font-size: 18px; }
  .bell-dot { position: absolute; top: 0; right: 0; width: 8px; height: 8px; background: #F4A4A4; border-radius: 50%; border: 1.5px solid #F5EBDD; }

  .page-body { padding: 28px 24px; display: flex; gap: 24px; align-items: flex-start; }
  .left-col { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 20px; }
  .right-col { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; }

  /* Hero banner */
  .hero-banner {
    background: #D4C8F5; border: 2px solid rgba(31,42,68,0.12); border-radius: 20px;
    padding: 28px 32px; display: flex; align-items: center; justify-content: space-between;
    box-shadow: 5px 5px 0px rgba(31,42,68,0.08); position: relative; overflow: hidden;
  }
  .hero-text h1 { font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 30px; color: #1F2A44; line-height: 1.2; margin-bottom: 12px; }
  .hero-text p { font-size: 14px; color: rgba(31,42,68,0.7); line-height: 1.5; margin-bottom: 20px; }
  .hero-img { width: 180px; height: 130px; object-fit: cover; border-radius: 12px; border: 2px solid rgba(31,42,68,0.15); flex-shrink: 0; box-shadow: 4px 4px 0px rgba(31,42,68,0.15); }
  .cta-btn {
    display: inline-flex; align-items: center; gap: 8px; background: #FFC857;
    border: 2px solid #1F2A44; border-radius: 12px; padding: 12px 20px;
    font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 15px;
    color: #1F2A44; cursor: pointer; box-shadow: 4px 4px 0px rgba(31,42,68,0.25);
    transition: all 0.15s; text-decoration: none;
  }
  .cta-btn:hover { transform: translateY(-2px) translateX(-1px); box-shadow: 6px 6px 0px rgba(31,42,68,0.3); }

  /* Blog list */
  .section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
  .section-title { font-weight: 900; font-size: 22px; color: #1F2A44; display: flex; align-items: center; gap: 8px; }
  .view-all { font-size: 13px; font-weight: 700; color: #6B5FD4; cursor: pointer; text-decoration: none; }
  .view-all:hover { text-decoration: underline; }

  .blog-list { display: flex; flex-direction: column; }
  .blog-item {
    display: flex; align-items: center; gap: 14px; padding: 14px 12px;
    border-bottom: 1.5px dashed rgba(31,42,68,0.1); cursor: pointer;
    transition: all 0.15s; border-radius: 10px; margin: 0 -12px;
  }
  .blog-item:hover { background: rgba(255,255,255,0.7); box-shadow: 2px 2px 0px rgba(31,42,68,0.08); transform: translateX(2px); }
  .blog-item:last-child { border-bottom: none; }
  .blog-icon-wrap { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; border: 1.5px solid rgba(31,42,68,0.1); }
  .blog-info { flex: 1; min-width: 0; }
  .blog-title { font-weight: 700; font-size: 14px; color: #1F2A44; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .blog-meta { font-size: 12px; color: rgba(31,42,68,0.5); }
  .blog-meta span { font-weight: 700; }
  .seo-badge { padding: 4px 10px; border-radius: 50px; font-size: 11px; font-weight: 800; background: #C8E6CB; color: #1F5732; border: 1.5px solid #2D6A4F; white-space: nowrap; }
  .seo-badge.orange { background: #FFE5A0; color: #7A5400; border-color: #E6B040; }
  .del-btn { font-size: 16px; opacity: 0.3; cursor: pointer; transition: opacity 0.15s; padding: 4px; border-radius: 6px; }
  .del-btn:hover { opacity: 0.8; background: rgba(200,60,60,0.08); }

  /* Stats card */
  .seo-health-card { background: #FDFAF6; border: 2px dashed rgba(31,42,68,0.2); border-radius: 18px; padding: 20px; box-shadow: 3px 3px 0px rgba(31,42,68,0.07); }
  .seo-health-title { font-weight: 900; font-size: 18px; color: #1F2A44; margin-bottom: 16px; }
  .health-row { margin-bottom: 14px; }
  .health-label-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
  .health-label { font-size: 12px; font-weight: 700; color: #1F2A44; }
  .health-value { font-size: 12px; font-weight: 700; color: rgba(31,42,68,0.6); }
  .health-bar-bg { height: 8px; background: rgba(31,42,68,0.08); border-radius: 50px; overflow: hidden; }
  .health-bar { height: 100%; border-radius: 50px; transition: width 0.6s cubic-bezier(.4,0,.2,1); }
  .bar-green { background: #A3C9A8; }
  .bar-purple { background: #B8A8E3; }
  .bar-yellow { background: #FFC857; }
  .audit-btn { width: 100%; padding: 12px; background: #1F2A44; border: none; border-radius: 12px; font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 14px; color: #FDFAF6; cursor: pointer; margin-top: 8px; box-shadow: 3px 3px 0px rgba(31,42,68,0.3); transition: all 0.15s; }
  .audit-btn:hover { transform: translateY(-2px); box-shadow: 5px 5px 0px rgba(31,42,68,0.3); }
  .bottom-cards { display: flex; gap: 12px; }
  .hint-card { flex: 1; height: 70px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; border: 1.5px solid rgba(31,42,68,0.1); cursor: pointer; transition: transform 0.2s; box-shadow: 2px 2px 0px rgba(31,42,68,0.07); }
  .hint-card:hover { transform: scale(1.05) rotate(-2deg); }
  .hint-card.green-bg { background: #C8E6CB; }
  .hint-card.purple-bg { background: #D4C8F5; }
  .fab { position: fixed; bottom: 28px; right: 28px; width: 52px; height: 52px; border-radius: 50%; background: #FFC857; border: 2px solid #1F2A44; display: flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; box-shadow: 4px 4px 0px rgba(31,42,68,0.25); transition: all 0.2s; z-index: 200; }
  .fab:hover { transform: scale(1.1) rotate(5deg); box-shadow: 6px 6px 0px rgba(31,42,68,0.3); }

  /* ── Blog Reader Modal ───────────────────────────────────────────────── */
  .modal-backdrop {
    position: fixed; inset: 0; z-index: 1000;
    background: rgba(31,42,68,0.55); backdrop-filter: blur(6px);
    display: flex; align-items: center; justify-content: center;
    animation: fadeIn 0.2s ease;
  }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes slideUp { from { opacity: 0; transform: translateY(24px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

  .modal-window {
    background: #FDFAF6;
    width: min(860px, calc(100vw - 48px));
    height: calc(100vh - 80px);
    border-radius: 24px;
    border: 2px solid rgba(31,42,68,0.15);
    box-shadow: 0 32px 80px rgba(31,42,68,0.25), 8px 8px 0px rgba(31,42,68,0.12);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slideUp 0.25s cubic-bezier(.34,1.56,.64,1);
  }

  .modal-header {
    padding: 20px 28px 16px;
    border-bottom: 1.5px dashed rgba(31,42,68,0.12);
    background: rgba(245,235,221,0.6);
    flex-shrink: 0;
  }
  .modal-header-top {
    display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px;
  }
  .modal-title {
    font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 22px;
    color: #1F2A44; line-height: 1.25; flex: 1;
  }
  .modal-close {
    width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid rgba(31,42,68,0.2);
    background: #FDFAF6; display: flex; align-items: center; justify-content: center;
    font-size: 18px; cursor: pointer; transition: all 0.15s; flex-shrink: 0; color: #1F2A44;
  }
  .modal-close:hover { background: #1F2A44; color: #FDFAF6; border-color: #1F2A44; }

  .modal-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .modal-chip {
    padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: 700;
    border: 1.5px solid rgba(31,42,68,0.15); background: rgba(31,42,68,0.05); color: rgba(31,42,68,0.65);
    letter-spacing: 0.3px;
  }
  .modal-chip.seo-good { background: #C8E6CB; color: #1F5732; border-color: #2D6A4F; }
  .modal-chip.seo-ok   { background: #FFE5A0; color: #7A5400; border-color: #E6B040; }
  .modal-chip.seo-bad  { background: #F4A4A4; color: #7a1a1a; border-color: #d14444; }

  .modal-actions {
    display: flex; gap: 8px; align-items: center; margin-left: auto;
  }
  .modal-action-btn {
    padding: 7px 14px; border-radius: 10px; font-size: 12px; font-weight: 700;
    border: 1.5px solid rgba(31,42,68,0.2); background: #FDFAF6;
    cursor: pointer; transition: all 0.15s; color: #1F2A44; display: flex; align-items: center; gap: 5px;
  }
  .modal-action-btn:hover { background: #1F2A44; color: #FDFAF6; border-color: #1F2A44; }
  .modal-action-btn.copied { background: #C8E6CB; border-color: #2D6A4F; color: #1F5732; }

  .modal-meta-desc {
    font-size: 13px; color: rgba(31,42,68,0.55); font-style: italic;
    padding: 8px 12px; background: rgba(31,42,68,0.03); border-radius: 8px;
    border-left: 3px solid #FFC857; margin-top: 4px;
  }

  .modal-body {
    flex: 1; overflow-y: auto; padding: 28px 36px;
  }
  .modal-body::-webkit-scrollbar { width: 6px; }
  .modal-body::-webkit-scrollbar-track { background: transparent; }
  .modal-body::-webkit-scrollbar-thumb { background: rgba(31,42,68,0.15); border-radius: 3px; }

  /* ── Markdown content ──────────────────────────────────────────────────── */
  .md-content { font-size: 15px; line-height: 1.85; color: rgba(31,42,68,0.82); }
  .md-content h1 { font-size: 28px; font-weight: 900; margin: 28px 0 14px; color: #1F2A44; }
  .md-content h2 { font-size: 21px; font-weight: 900; margin: 24px 0 12px; color: #1F2A44; padding-bottom: 8px; border-bottom: 2px solid rgba(31,42,68,0.08); }
  .md-content h3 { font-size: 17px; font-weight: 800; margin: 20px 0 10px; color: #1F2A44; }
  .md-content h4 { font-size: 15px; font-weight: 800; margin: 16px 0 8px; color: #1F2A44; }
  .md-content p { margin-bottom: 16px; }
  .md-content strong { font-weight: 800; color: #1F2A44; }
  .md-content em { font-style: italic; }
  .md-content a { color: #6B5FD4; text-decoration: none; font-weight: 700; }
  .md-content a:hover { text-decoration: underline; }
  .md-content ul { margin: 10px 0 16px 22px; list-style: disc; }
  .md-content ol { margin: 10px 0 16px 22px; list-style: decimal; }
  .md-content li { margin-bottom: 7px; }
  .md-content li > ul, .md-content li > ol { margin-top: 6px; margin-bottom: 4px; }
  .md-content blockquote { margin: 18px 0; padding: 12px 18px; border-left: 4px solid #FFC857; background: rgba(255,200,87,0.08); border-radius: 0 10px 10px 0; font-style: italic; color: rgba(31,42,68,0.7); }
  .md-content code { background: rgba(31,42,68,0.07); padding: 2px 7px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 13px; color: #1F2A44; }
  .md-content pre { background: #1F2A44; padding: 16px 20px; border-radius: 12px; overflow-x: auto; margin: 18px 0; }
  .md-content pre code { background: none; color: #e8eaf6; padding: 0; font-size: 13.5px; }
  .md-content hr { border: none; border-top: 2px dashed rgba(31,42,68,0.12); margin: 28px 0; }

  /* ── Tables ─────────────────────────────────────────────────────────────── */
  /* Wrap table in scrollable container so long tables don't break the layout */
  .md-content table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 20px 0;
    font-size: 13.5px;
    border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 12px;
    overflow: hidden;
    display: block;          /* makes overflow-x work on table  */
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  /* thead row */
  .md-content thead tr { background: rgba(31,42,68,0.07); }
  .md-content thead tr:first-child th:first-child { border-top-left-radius : 11px; }
  .md-content thead tr:first-child th:last-child  { border-top-right-radius: 11px; }

  /* th */
  .md-content th {
    padding: 12px 16px;
    text-align: left;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: rgba(31,42,68,0.65);
    border-bottom: 2px solid rgba(31,42,68,0.1);
    white-space: nowrap;
    background: rgba(31,42,68,0.06);
  }

  /* td */
  .md-content td {
    padding: 11px 16px;
    border-bottom: 1px solid rgba(31,42,68,0.07);
    color: rgba(31,42,68,0.8);
    vertical-align: top;
    min-width: 100px;
  }

  /* zebra stripes */
  .md-content tbody tr:nth-child(even) { background: rgba(31,42,68,0.025); }

  /* hover row highlight */
  .md-content tbody tr:hover { background: rgba(255,200,87,0.1); transition: background 0.15s; }

  /* no border on last row */
  .md-content tbody tr:last-child td { border-bottom: none; }

  /* rounded bottom corners */
  .md-content tbody tr:last-child td:first-child { border-bottom-left-radius : 10px; }
  .md-content tbody tr:last-child td:last-child  { border-bottom-right-radius: 10px; }

  /* centre-aligned columns (GFM :---: syntax) */
  .md-content th[align="center"], .md-content td[align="center"] { text-align: center; }
  .md-content th[align="right"],  .md-content td[align="right"]  { text-align: right; }
  .md-content th[align="left"],   .md-content td[align="left"]   { text-align: left; }

  .modal-loading {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 200px; gap: 16px; color: rgba(31,42,68,0.45);
  }
  .spinner {
    width: 40px; height: 40px; border: 3px solid rgba(31,42,68,0.1);
    border-top-color: #FFC857; border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
`;

// ── Helpers ────────────────────────────────────────────────────────────────
const ICONS  = ["✨","🎭","📖","🌿","🚀","💡","🎯","🔮","🌊","🦋"];
const ICON_BG= ["#FFE5A0","#D4C8F5","#C8E6CB","#F4A4A4","#FDFAF6"];

function fmtDate(iso) {
  if (!iso) return "";
  const d = new Date(iso), now = new Date();
  const diffH = Math.round((now - d) / 3600000);
  if (diffH < 1)  return "Just now";
  if (diffH < 24) return `${diffH}h ago`;
  const diffD = Math.floor(diffH / 24);
  if (diffD === 1) return "Yesterday";
  if (diffD < 7)  return `${diffD} days ago`;
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

// ── Blog Reader Modal ──────────────────────────────────────────────────────
function BlogModal({ blog, onClose }) {
  const [detail, setDetail] = useState(null);
  const [fetching, setFetching] = useState(true);
  const [copied, setCopied] = useState(false);

  // Fetch full content (list endpoint excludes it)
  useEffect(() => {
    let cancelled = false;
    setFetching(true);
    api.blog.get(blog.id)
      .then((d) => { if (!cancelled) { setDetail(d); setFetching(false); } })
      .catch(() => { if (!cancelled) setFetching(false); });
    return () => { cancelled = true; };
  }, [blog.id]);

  // Close on Escape key
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const handleCopy = () => {
    if (!detail?.content) return;
    navigator.clipboard.writeText(detail.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const seo = detail?.seo_score ?? blog.seo_score ?? 0;
  const seoClass = seo >= 70 ? "seo-good" : seo >= 45 ? "seo-ok" : "seo-bad";

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-window">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-top">
            <div style={{ flex: 1 }}>
              <div className="modal-title">{blog.title || blog.keyword}</div>
              {(detail?.meta_description || blog.meta_description) && (
                <div className="modal-meta-desc">
                  {detail?.meta_description || blog.meta_description}
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button
                className={`modal-action-btn ${copied ? "copied" : ""}`}
                onClick={handleCopy}
                disabled={fetching}
              >
                {copied ? "✅ Copied!" : "📋 Copy"}
              </button>
              <button className="modal-close" onClick={onClose} title="Close (Esc)">✕</button>
            </div>
          </div>

          {/* Chips row */}
          <div className="modal-chips">
            <span className={`modal-chip ${seoClass}`}>⚡ {seo} SEO Score</span>
            <span className="modal-chip">📝 {detail?.word_count ?? blog.word_count ?? 0} words</span>
            <span className="modal-chip">🔑 {blog.keyword}</span>
            <span className="modal-chip">{blog.status}</span>
            {blog.created_at && (
              <span className="modal-chip">🕐 {fmtDate(blog.created_at)}</span>
            )}
            {(detail?.generation_time ?? blog.generation_time) && (
              <span className="modal-chip">⏱ {(detail?.generation_time ?? blog.generation_time).toFixed(1)}s gen</span>
            )}
            {(detail?.slug || blog.slug) && (
              <span className="modal-chip">🔗 /{detail?.slug || blog.slug}</span>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="modal-body">
          {fetching ? (
            <div className="modal-loading">
              <div className="spinner" />
              <div style={{ fontSize: 14, fontWeight: 700 }}>Loading blog content…</div>
            </div>
          ) : detail?.content ? (
            <div className="md-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {detail.content}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="modal-loading">
              <div style={{ fontSize: 32 }}>📭</div>
              <div style={{ fontSize: 14, fontWeight: 700 }}>Content not available</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────
export default function JournalPage({ activePage = "journal", onNavigate }) {
  const [showProfile, setShowProfile] = useState(false);
  const [selectedBlog, setSelectedBlog] = useState(null);
  const { mongoBlogs, loading, actions } = useWorkflow();

  useEffect(() => {
    actions.fetchBlogHistory({ limit: 20 });
  }, []);

  const handleDelete = async (blogId, e) => {
    e.stopPropagation();
    if (!window.confirm("Permanently delete this blog?")) return;
    try { await actions.deleteBlog(blogId); }
    catch (err) { alert(err.message); }
  };

  const handleClose = useCallback(() => setSelectedBlog(null), []);

  const totalBlogs  = mongoBlogs.length;
  const avgSEO      = totalBlogs ? Math.round(mongoBlogs.reduce((s, b) => s + (b.seo_score || 0), 0) / totalBlogs) : 0;
  const totalWords  = mongoBlogs.reduce((s, b) => s + (b.word_count || 0), 0);

  return (
    <>
      <style>{journalStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          {/* Topbar */}
          <div className="topbar">
            <span className="badge badge-geo">GEO READY</span>
            <span className="badge badge-seo">SEO ENGINE ON</span>
            <div className="topbar-right">
              <span className="topbar-greeting">Good morning, Aryan 🖊</span>
              <div className="bell-wrap">🔔<div className="bell-dot" /></div>
              <div className="topbar-avatar" onClick={() => setShowProfile((v) => !v)}>
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=aryan&backgroundColor=b6e3f4" style={{width:'100%',height:'100%'}} alt="av" />
              </div>
            </div>
          </div>

          <div className="page-body">
            <div className="left-col">
              {/* Hero Banner */}
              <div className="hero-banner">
                <div className="hero-text">
                  <h1>Your blog engine is<br/>ready to fire 🚀</h1>
                  <p>We've analyzed your latest keywords and identified<br/>trending topics you'll love.</p>
                  <button className="cta-btn" onClick={() => onNavigate?.("blog-gen")}>
                    + Generate Blog
                  </button>
                </div>
                <img
                  src="https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400&h=260&fit=crop&auto=format"
                  alt="typewriter" className="hero-img"
                  onError={e => { e.target.style.display = 'none'; }}
                />
              </div>

              {/* Recent Blogs (live from MongoDB) */}
              <div>
                <div className="section-header">
                  <div className="section-title">Recent Blogs ✏️</div>
                  <a
                    className="view-all"
                    onClick={() => actions.fetchBlogHistory({ limit: 20 })}
                    style={{ cursor: "pointer" }}
                  >
                    {loading.blogHistory ? "Loading…" : "Refresh ↻"}
                  </a>
                </div>

                <div className="blog-list">
                  {loading.blogHistory && mongoBlogs.length === 0 && (
                    <div style={{ padding: "28px 0", textAlign: "center", color: "rgba(31,42,68,0.4)", fontSize: 14 }}>
                      <div className="spinner" style={{ margin: "0 auto 10px" }} />
                      Loading blogs…
                    </div>
                  )}
                  {!loading.blogHistory && mongoBlogs.length === 0 && (
                    <div style={{ padding: "28px 0", textAlign: "center", color: "rgba(31,42,68,0.4)", fontSize: 14 }}>
                      No blogs yet — generate your first one! 🚀
                    </div>
                  )}

                  {mongoBlogs.slice(0, 10).map((b, i) => (
                    <div
                      key={b.id || i}
                      className="blog-item"
                      onClick={() => setSelectedBlog(b)}
                    >
                      <div className="blog-icon-wrap" style={{ background: ICON_BG[i % ICON_BG.length] }}>
                        {ICONS[i % ICONS.length]}
                      </div>
                      <div className="blog-info">
                        <div className="blog-title">{b.title || b.keyword}</div>
                        <div className="blog-meta">
                          {fmtDate(b.created_at)} • <span>{b.status}</span> • {b.word_count || 0} words
                        </div>
                      </div>
                      <span className={`seo-badge ${(b.seo_score || 0) < 70 ? "orange" : ""}`}>
                        {b.seo_score || "—"} SEO
                      </span>
                      <span
                        className="del-btn"
                        title="Delete blog"
                        onClick={(e) => handleDelete(b.id, e)}
                      >🗑</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Col */}
            <div className="right-col">
              <div className="seo-health-card">
                <div className="seo-health-title">Blog Stats 📊</div>
                {[
                  { label: "Total Blogs",       value: totalBlogs, bar: "bar-green",  pct: Math.min(totalBlogs * 10, 100) },
                  { label: "Avg SEO Score",      value: avgSEO || "—", bar: "bar-purple", pct: avgSEO },
                  { label: "Total Words Written", value: totalWords >= 1000 ? `${(totalWords/1000).toFixed(1)}k` : (totalWords || "—"), bar: "bar-yellow", pct: Math.min(totalWords / 500, 100) },
                ].map((r, i) => (
                  <div key={i} className="health-row">
                    <div className="health-label-row">
                      <span className="health-label">{r.label}</span>
                      <span className="health-value">{r.value}</span>
                    </div>
                    <div className="health-bar-bg">
                      <div className={`health-bar ${r.bar}`} style={{ width: `${r.pct || 0}%` }} />
                    </div>
                  </div>
                ))}
                <button className="audit-btn" onClick={() => onNavigate?.("seo-audit")}>
                  Run SEO Audit →
                </button>
              </div>

              <div className="bottom-cards">
                <div className="hint-card green-bg" onClick={() => onNavigate?.("blog-gen")}>📈</div>
                <div className="hint-card purple-bg" onClick={() => onNavigate?.("strategic-map")}>📖</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showProfile && <ProfileOverlay onClose={() => setShowProfile(false)} onNavigate={onNavigate} />}

      {/* Blog Reader Modal */}
      {selectedBlog && <BlogModal blog={selectedBlog} onClose={handleClose} />}

      <div className="fab" onClick={() => onNavigate?.("blog-gen")}>⚡</div>
    </>
  );
}
