import { useEffect, useMemo } from "react";
import { useWorkflow } from "../context/WorkflowContext";

const overlayStyles = `
  .profile-overlay-backdrop {
    position: fixed; inset: 0; background: rgba(31,42,68,0.25);
    display: flex; align-items: flex-start; justify-content: center; z-index: 999;
    padding: 20px;
    overflow-y: auto;
  }
  .profile-overlay-card {
    position: relative;
    margin-top: 10px;
    width: min(960px, calc(100% - 40px));
    max-height: calc(100vh - 120px);
    background: #FDFAF6;
    border: 2px solid rgba(31,42,68,0.15);
    border-radius: 18px;
    box-shadow: 10px 10px 0 rgba(31,42,68,0.2);
    overflow: hidden;
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 0;
  }
  .profile-left { padding: 24px; border-right: 1.5px dashed rgba(31,42,68,0.12); display: grid; gap: 12px; align-content: start; overflow-y: auto; max-height: calc(100vh - 120px); }
  .profile-right { padding: 24px; overflow-y: auto; max-height: calc(100vh - 120px); }
  .avatar-wrap { width: 120px; height: 120px; border-radius: 50%; overflow: hidden; border: 3px solid #1F2A44; box-shadow: 4px 4px 0 rgba(31,42,68,0.2); }
  .name { font-size: 22px; font-weight: 900; margin-top: 12px; }
  .role { font-size: 13px; font-weight: 700; color: rgba(31,42,68,0.6); }
  .pill { display: inline-block; padding: 6px 10px; border-radius: 50px; border: 1.5px dashed rgba(31,42,68,0.2); font-weight: 800; font-size: 11px; margin-right: 6px; margin-top: 8px; }
  .actions { display: flex; gap: 10px; margin-top: 12px; }
  .btn { padding: 10px 14px; border-radius: 10px; border: 2px solid #1F2A44; font-weight: 800; cursor: pointer; background: #FFC857; box-shadow: 3px 3px 0 rgba(31,42,68,0.2); }
  .btn.secondary { background: #FDFAF6; border-style: dashed; }
  .section-title { font-size: 16px; font-weight: 900; margin-bottom: 10px; }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 8px; }
  .stat { padding: 12px; border-radius: 14px; background: rgba(255,255,255,0.9); border: 1.5px solid rgba(31,42,68,0.08); }
  .stat-label { font-size: 11px; font-weight: 800; letter-spacing: 0.6px; color: rgba(31,42,68,0.6); text-transform: uppercase; }
  .stat-value { font-size: 24px; font-weight: 900; margin-top: 6px; }
  .history-list { display: flex; flex-direction: column; gap: 10px; }
  .history-item { border: 1.5px solid rgba(31,42,68,0.08); border-radius: 12px; padding: 12px; background: rgba(255,255,255,0.85); }
  .history-title { font-weight: 800; font-size: 14px; }
  .history-meta { font-size: 12px; color: rgba(31,42,68,0.6); }
  .close-btn { position: absolute; top: 16px; right: 16px; background: #1F2A44; color: #FDFAF6; border: none; border-radius: 50%; width: 32px; height: 32px; cursor: pointer; font-weight: 900; box-shadow: 2px 2px 0 rgba(31,42,68,0.2); }

  @media (max-width: 900px) {
    .profile-overlay-card {
      grid-template-columns: 1fr;
      max-height: none;
    }
    .profile-left { border-right: none; border-bottom: 1.5px dashed rgba(31,42,68,0.12); }
  }
`;

export default function ProfileOverlay({ onClose, onNavigate }) {
  const { blogHistory, mongoBlogs, actions } = useWorkflow();

  useEffect(() => {
    if (!mongoBlogs.length) {
      actions
        .fetchBlogHistory({ limit: 25 })
        .catch(() => {});
    }
  }, [actions, mongoBlogs.length]);

  const unifiedHistory = useMemo(() => {
    if (Array.isArray(blogHistory) && blogHistory.length) return blogHistory;
    if (!Array.isArray(mongoBlogs) || !mongoBlogs.length) return [];
    return mongoBlogs.map((b) => ({
      id: b.id,
      title: b.title || "Untitled Blog",
      keyword: b.keyword || "",
      seoScore: Number(b.seo_score || 0),
      wordCount: Number(b.word_count || 0),
      createdAt: b.created_at || new Date().toISOString(),
    }));
  }, [blogHistory, mongoBlogs]);

  const recent = unifiedHistory.slice(0, 5);
  const avgSeo = useMemo(
    () => {
      const scored = recent.filter((r) => Number.isFinite(Number(r.seoScore)));
      if (!scored.length) return 0;
      return Math.round(scored.reduce((s, r) => s + Number(r.seoScore || 0), 0) / scored.length);
    },
    [recent]
  );

  return (
    <>
      <style>{overlayStyles}</style>
      <div className="profile-overlay-backdrop" onClick={onClose}>
        <div className="profile-overlay-card" onClick={(e) => e.stopPropagation()}>
          <button className="close-btn" onClick={onClose}>×</button>
          <div className="profile-left">
            <div className="avatar-wrap">
              <img
                src="https://api.dicebear.com/7.x/avataaars/svg?seed=aryan&backgroundColor=b6e3f4"
                alt="avatar"
                style={{ width: "100%", height: "100%" }}
                onError={(e) => {
                  e.target.style.display = "none";
                  e.target.parentElement.innerHTML = "🧑";
                }}
              />
            </div>
            <div className="name">Aryan Shah</div>
            <div className="role">Content Lead · APAC</div>
            <div>
              <div className="pill">Team: Growth</div>
              <div className="pill">Timezone: IST</div>
              <div className="pill">Access: Admin</div>
            </div>
            <div className="actions">
              <button className="btn" onClick={() => onNavigate?.("blog-gen")}>New Blog</button>
              <button className="btn secondary" onClick={() => onNavigate?.("humanizer")}>Run Humanizer</button>
            </div>
          </div>

          <div className="profile-right">
            <div className="section-title">Performance</div>
            <div className="stats">
              <div className="stat">
                <div className="stat-label">Blogs Generated</div>
                <div className="stat-value">{unifiedHistory.length}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Avg. SEO Score</div>
                <div className="stat-value">{avgSeo}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Recent Wordcount</div>
                <div className="stat-value">{recent[0]?.wordCount || "--"}</div>
              </div>
            </div>

            <div className="section-title" style={{ marginTop: 18 }}>Recent Drafts</div>
            {recent.length ? (
              <div className="history-list">
                {recent.map((entry) => (
                  <div key={entry.id} className="history-item">
                    <div className="history-title">{entry.title || entry.keyword}</div>
                    <div className="history-meta">
                      {entry.keyword} · {entry.seoScore ? `${Math.round(entry.seoScore)} SEO` : "Draft"} · {new Date(entry.createdAt).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="history-meta">No drafts yet. Generate a blog to see history.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
