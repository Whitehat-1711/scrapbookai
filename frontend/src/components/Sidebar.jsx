import { useMemo } from "react";
import { useWorkflow } from "../context/WorkflowContext";

const navItems = [
  { id: "journal", label: "Journal", icon: "📝" },
  { id: "blog-gen", label: "Blog Lab", icon: "✍️" },
  { id: "strategic-map", label: "SERP Lab", icon: "🔍" },
  { id: "resource-pile", label: "Ops Dashboard", icon: "📊" },
  { id: "humanizer", label: "Humanizer", icon: "🧬" },
  { id: "seo-audit", label: "SEO Audit", icon: "🔬" },
];

export default function Sidebar({ activePage = "journal", onNavigate }) {
  const { blogHistory } = useWorkflow();
  const recentHistory = useMemo(() => blogHistory.slice(0, 3), [blogHistory]);

  const handleNavigate = (page) => {
    if (typeof onNavigate === "function") {
      onNavigate(page);
    }
  };

  return (
    <>
      <style>{`
        .sidebar {
          width: 220px;
          min-width: 220px;
          background: #B8A8E3;
          height: 100vh;
          display: flex;
          flex-direction: column;
          padding: 24px 16px;
          position: relative;
          font-family: 'Nunito', sans-serif;
          border-right: 2px dashed rgba(31,42,68,0.15);
        }
        .sidebar-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 24px;
          padding: 0 4px;
        }
        .sidebar-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #1F2A44;
          border: 2px solid #FFC857;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          flex-shrink: 0;
          overflow: hidden;
        }
        .sidebar-logo-text h2 {
          font-family: 'Nunito', sans-serif;
          font-weight: 900;
          font-size: 15px;
          color: #1F2A44;
          margin: 0;
          line-height: 1.2;
        }
        .sidebar-logo-text p {
          font-family: 'Caveat', cursive;
          font-size: 12px;
          color: #1F2A44;
          margin: 0;
          opacity: 0.7;
          letter-spacing: 0.5px;
        }
        .sidebar-nav {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 14px;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.15s ease;
          font-weight: 600;
          font-size: 14px;
          color: #1F2A44;
          border: 2px solid transparent;
          position: relative;
        }
        .nav-item:hover {
          background: rgba(255,255,255,0.3);
          transform: translateX(2px);
        }
        .nav-item.active {
          background: #FFC857;
          border: 2px solid #1F2A44;
          box-shadow: 3px 3px 0px rgba(31,42,68,0.25);
          transform: translateX(1px) translateY(-1px);
        }
        .nav-icon {
          font-size: 16px;
          width: 20px;
          text-align: center;
        }
        .sidebar-bottom {
          margin-top: 20px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .new-entry-btn {
          width: 100%;
          padding: 12px;
          background: #FFC857;
          border: 2px solid #1F2A44;
          border-radius: 50px;
          font-family: 'Nunito', sans-serif;
          font-weight: 800;
          font-size: 14px;
          color: #1F2A44;
          cursor: pointer;
          box-shadow: 3px 3px 0px rgba(31,42,68,0.25);
          transition: all 0.15s ease;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
        }
        .new-entry-btn:hover {
          transform: translateY(-2px);
          box-shadow: 5px 5px 0px rgba(31,42,68,0.3);
        }
        .new-entry-btn:active {
          transform: translateY(0);
          box-shadow: 2px 2px 0px rgba(31,42,68,0.25);
        }
        .sidebar-history {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1.5px dashed rgba(31,42,68,0.2);
        }
        .history-label {
          font-size: 11px; font-weight: 800; letter-spacing: 0.7px;
          text-transform: uppercase; color: rgba(31,42,68,0.5); margin-bottom: 10px;
        }
        .history-card {
          padding: 10px 12px; border-radius: 12px; background: rgba(253,250,246,0.7);
          border: 1.5px solid rgba(31,42,68,0.12); margin-bottom: 8px;
        }
        .history-title {
          font-size: 13px; font-weight: 700; color: #1F2A44; margin-bottom: 3px;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .history-meta {
          font-size: 11px; color: rgba(31,42,68,0.6);
        }
        .history-empty {
          font-size: 12px; font-weight: 600; color: rgba(31,42,68,0.5);
        }
      `}</style>
      <div className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-avatar">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=aryan&backgroundColor=b6e3f4" style={{width:'100%',height:'100%'}} alt="avatar" onError={e => { e.target.style.display='none'; e.target.parentElement.innerHTML='🧑'; }} />
          </div>
          <div className="sidebar-logo-text">
            <h2>The Scrapbook</h2>
            <p>Curated Chaos</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <div
              key={item.id}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => handleNavigate(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className="new-entry-btn" onClick={() => handleNavigate("blog-gen")}>
            <span>+</span> New Entry
          </button>
          <div className="sidebar-history">
            <div className="history-label">Recent Drafts</div>
            {recentHistory.length ? (
              recentHistory.map((entry, idx) => (
                <div key={entry.id || idx} className="history-card" onClick={() => handleNavigate("blog-gen")}>
                  <div className="history-title">{entry.title || entry.keyword}</div>
                  <div className="history-meta">
                    {entry.keyword || "--"} · {entry.seoScore ? `${Math.round(entry.seoScore)} SEO` : "Draft"}
                  </div>
                </div>
              ))
            ) : (
              <div className="history-empty">No runs yet. Generate your first blog!</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
