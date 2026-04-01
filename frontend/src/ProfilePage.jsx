import Sidebar from "./components/Sidebar";
import { useWorkflow } from "./context/WorkflowContext";

const profileStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body, html { font-family: 'Nunito', sans-serif; background: #F5EBDD; color: #1F2A44; }
  .app-shell { display: flex; min-height: 100vh; background: #F5EBDD; }
  .main-content {
    flex: 1; overflow-y: auto; padding: 32px; background: #F5EBDD;
    background-image:
      linear-gradient(rgba(31,42,68,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(31,42,68,0.03) 1px, transparent 1px);
    background-size: 28px 28px;
  }
  .profile-grid { display: grid; grid-template-columns: 320px 1fr; gap: 24px; align-items: start; }
  .card { background: #FDFAF6; border: 1.5px solid rgba(31,42,68,0.1); border-radius: 18px; padding: 20px; box-shadow: 4px 4px 0 rgba(31,42,68,0.08); }
  .avatar-wrap { width: 120px; height: 120px; border-radius: 50%; overflow: hidden; border: 3px solid #1F2A44; box-shadow: 4px 4px 0 rgba(31,42,68,0.2); }
  .name { font-size: 22px; font-weight: 900; margin-top: 12px; }
  .role { font-size: 13px; font-weight: 700; color: rgba(31,42,68,0.6); }
  .pill { display: inline-block; padding: 6px 10px; border-radius: 50px; border: 1.5px dashed rgba(31,42,68,0.2); font-weight: 800; font-size: 11px; margin-right: 6px; margin-top: 8px; }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }
  .stat { padding: 14px; border-radius: 14px; background: rgba(255,255,255,0.9); border: 1.5px solid rgba(31,42,68,0.08); }
  .stat-label { font-size: 11px; font-weight: 800; letter-spacing: 0.6px; color: rgba(31,42,68,0.6); text-transform: uppercase; }
  .stat-value { font-size: 24px; font-weight: 900; margin-top: 6px; }
  .section-title { font-size: 16px; font-weight: 900; margin-bottom: 10px; }
  .history-list { display: flex; flex-direction: column; gap: 10px; }
  .history-item { border: 1.5px solid rgba(31,42,68,0.08); border-radius: 12px; padding: 12px; background: rgba(255,255,255,0.85); }
  .history-title { font-weight: 800; font-size: 14px; }
  .history-meta { font-size: 12px; color: rgba(31,42,68,0.6); }
  .actions { display: flex; gap: 10px; margin-top: 12px; }
  .btn { padding: 10px 14px; border-radius: 10px; border: 2px solid #1F2A44; font-weight: 800; cursor: pointer; background: #FFC857; box-shadow: 3px 3px 0 rgba(31,42,68,0.2); }
  .btn.secondary { background: #FDFAF6; border-style: dashed; }
`;

export default function ProfilePage({ activePage = "profile", onNavigate }) {
  const { blogHistory } = useWorkflow();
  const recent = blogHistory.slice(0, 5);

  return (
    <>
      <style>{profileStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          <div className="profile-grid">
            <div className="card">
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
              <div className="pill">Team: Growth</div>
              <div className="pill">Timezone: IST</div>
              <div className="pill">Access: Admin</div>
              <div className="actions">
                <button className="btn" onClick={() => onNavigate?.("blog-gen")}>New Blog</button>
                <button className="btn secondary" onClick={() => onNavigate?.("humanizer")}>Run Humanizer</button>
              </div>
            </div>

            <div className="card">
              <div className="section-title">Performance</div>
              <div className="stats">
                <div className="stat">
                  <div className="stat-label">Blogs Generated</div>
                  <div className="stat-value">{blogHistory.length}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Avg. SEO Score</div>
                  <div className="stat-value">{Math.round((recent.reduce((s, r) => s + (r.seoScore || 0), 0) / (recent.length || 1)) || 0)}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Recent Wordcount</div>
                  <div className="stat-value">{recent[0]?.wordCount || "--"}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: 20 }}>
            <div className="section-title">Recent Drafts</div>
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
