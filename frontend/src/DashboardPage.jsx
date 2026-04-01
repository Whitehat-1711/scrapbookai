import { useState } from "react";
import Sidebar from "./components/Sidebar";
import ProfileOverlay from "./components/ProfileOverlay";

const doodleStyles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body, html { 
    font-family: 'Nunito', sans-serif;
    background: #F5EBDD;
    color: #1F2A44;
  }

  .app-shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
    background: #F5EBDD;
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    background: #F5EBDD;
    background-image: 
      linear-gradient(rgba(31,42,68,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(31,42,68,0.04) 1px, transparent 1px);
    background-size: 28px 28px;
  }

  .topbar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 28px;
    background: rgba(245,235,221,0.92);
    backdrop-filter: blur(4px);
    border-bottom: 1.5px dashed rgba(31,42,68,0.12);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .topbar-search {
    flex: 1;
    max-width: 320px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: #FDFAF6;
    border: 1.5px solid rgba(31,42,68,0.15);
    border-radius: 50px;
    padding: 8px 16px;
  }
  .topbar-search input {
    border: none; background: transparent; outline: none;
    font-family: 'Nunito', sans-serif; font-size: 13px; color: #1F2A44; width: 100%;
  }
  .topbar-search input::placeholder { color: #9AA5B4; }

  .badge {
    padding: 5px 12px; border-radius: 50px; font-size: 11px; font-weight: 700;
    letter-spacing: 0.5px; text-transform: uppercase; border: 1.5px solid;
  }
  .badge-geo { background: #C8E6CB; color: #2D6A4F; border-color: #2D6A4F; }
  .badge-seo { background: #FFF3CD; color: #92681A; border-color: #92681A; }

  .topbar-right {
    margin-left: auto; display: flex; align-items: center; gap: 14px;
  }
  .topbar-greeting {
    font-weight: 700; font-size: 14px; color: #1F2A44;
  }
  .topbar-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    background: #1F2A44; border: 2px solid #FFC857;
    overflow: hidden; cursor: pointer;
  }
  .bell-wrap {
    position: relative; cursor: pointer; font-size: 18px;
  }
  .bell-dot {
    position: absolute; top: 0; right: 0;
    width: 8px; height: 8px; background: #F4A4A4;
    border-radius: 50%; border: 1.5px solid #F5EBDD;
  }

  .page-body {
    padding: 32px 28px;
  }

  /* Organic Power Section */
  .hero-row {
    display: flex;
    align-items: flex-start;
    gap: 24px;
    margin-bottom: 36px;
  }

  .organic-circle-wrap {
    position: relative;
    flex-shrink: 0;
  }

  .organic-circle {
    width: 220px;
    height: 220px;
    background: #FFC857;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 3px solid #1F2A44;
    box-shadow: 6px 6px 0px rgba(31,42,68,0.2);
    position: relative;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .organic-circle:hover {
    transform: translateY(-3px);
    box-shadow: 9px 9px 0px rgba(31,42,68,0.2);
  }

  .circle-label {
    font-family: 'Caveat', cursive;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(31,42,68,0.7);
    margin-bottom: 4px;
  }
  .circle-score {
    font-family: 'Nunito', sans-serif;
    font-weight: 900;
    font-size: 88px;
    line-height: 1;
    color: #1F2A44;
  }
  .circle-subtitle {
    font-family: 'Caveat', cursive;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(31,42,68,0.8);
  }

  .top5-sticker {
    position: absolute;
    bottom: -10px;
    right: -10px;
    background: #A3C9A8;
    border: 2px solid #1F2A44;
    border-radius: 8px;
    padding: 5px 12px;
    font-family: 'Caveat', cursive;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
    color: #1F2A44;
    box-shadow: 2px 2px 0px rgba(31,42,68,0.2);
    transform: rotate(-2deg);
    white-space: nowrap;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    flex: 1;
    align-self: center;
  }

  .stat-card {
    background: #FDFAF6;
    border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 16px;
    padding: 18px 16px;
    box-shadow: 3px 3px 0px rgba(31,42,68,0.08);
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .stat-card:hover {
    transform: translateY(-3px) translateX(-1px);
    box-shadow: 6px 6px 0px rgba(31,42,68,0.12);
  }
  .stat-card.purple { background: #D4C8F5; }
  .stat-card.green { background: #C8E6CB; }
  .stat-card.gray { background: #E8E4DC; }
  .stat-card.yellow { background: #FFE5A0; }

  .stat-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
  }
  .stat-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: rgba(31,42,68,0.6);
    margin-bottom: 4px;
  }
  .stat-value {
    font-family: 'Nunito', sans-serif;
    font-weight: 900;
    font-size: 28px;
    color: #1F2A44;
    line-height: 1;
    margin-bottom: 4px;
  }
  .stat-change {
    font-size: 12px;
    font-weight: 700;
    color: #2D6A4F;
  }
  .stat-tag {
    font-size: 12px;
    font-weight: 700;
    color: #2D6A4F;
    background: rgba(163,201,168,0.4);
    padding: 2px 8px;
    border-radius: 20px;
    display: inline-block;
  }

  /* Lower sections */
  .lower-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .section-card {
    background: #FDFAF6;
    border: 1.5px solid rgba(31,42,68,0.12);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 4px 4px 0px rgba(31,42,68,0.08);
    position: relative;
  }
  .section-card.lavender { background: #D4C8F5; }

  .section-title {
    font-family: 'Nunito', sans-serif;
    font-weight: 900;
    font-size: 22px;
    color: #1F2A44;
    margin-bottom: 4px;
  }
  .section-subtitle {
    font-family: 'Caveat', cursive;
    font-size: 14px;
    color: rgba(31,42,68,0.6);
    margin-bottom: 20px;
  }

  /* Keyword chart */
  .keyword-chart {
    height: 180px;
    display: flex;
    align-items: flex-end;
    gap: 32px;
    padding: 0 8px;
    position: relative;
  }
  .kw-bar-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    flex: 1;
  }
  .kw-dot {
    width: 8px; height: 8px;
    background: #1F2A44;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .kw-line {
    width: 1.5px;
    background: rgba(31,42,68,0.25);
    flex: 1;
  }
  .kw-labels {
    display: flex;
    gap: 32px;
    padding: 8px 8px 0;
    flex-wrap: wrap;
  }
  .kw-label {
    font-family: 'Caveat', cursive;
    font-size: 12px;
    color: rgba(31,42,68,0.6);
    flex: 1;
    text-align: center;
  }

  .pencil-icon {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 18px;
    opacity: 0.4;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  .pencil-icon:hover { opacity: 0.8; }

  /* Internal linking map */
  .link-map {
    height: 200px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .link-node {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-family: 'Caveat', cursive;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    border: 2px solid #1F2A44;
    cursor: pointer;
    transition: transform 0.2s;
  }
  .link-node:hover { transform: scale(1.1); }
  .link-node.home {
    width: 72px; height: 72px;
    background: #1F2A44; color: #FDFAF6;
    font-size: 13px;
    box-shadow: 4px 4px 0px rgba(31,42,68,0.3);
  }
  .link-node.small {
    width: 46px; height: 46px;
    background: #FDFAF6; color: #1F2A44;
    box-shadow: 2px 2px 0px rgba(31,42,68,0.15);
  }
  .link-node.empty {
    width: 38px; height: 38px;
    background: #FDFAF6; color: transparent;
    border-style: dashed;
  }

  .insight-badge {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    background: #A3C9A8;
    border: 1.5px solid #1F2A44;
    border-radius: 50px;
    padding: 6px 16px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 12px;
    color: #1F2A44;
    white-space: nowrap;
    box-shadow: 2px 2px 0px rgba(31,42,68,0.15);
  }
`;

function KeywordChart() {
  const bars = [
    { height: 30, label: '"notebook design system"' },
    { height: 55, label: '"editorial ui components"' },
    { height: 72, label: '"org..."' },
    { height: 65, label: '"..."' },
    { height: 90, label: '"..."' },
  ];

  return (
    <div>
      <div className="keyword-chart">
        {bars.map((b, i) => (
          <div key={i} className="kw-bar-wrap" style={{ height: '100%', justifyContent: 'flex-end' }}>
            <div className="kw-dot" />
            <div className="kw-line" style={{ height: `${b.height}%` }} />
          </div>
        ))}
      </div>
      <div className="kw-labels">
        {bars.map((b, i) => (
          <span key={i} className="kw-label">{b.label}</span>
        ))}
      </div>
    </div>
  );
}

function LinkMap() {
  return (
    <div className="link-map">
      <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none' }}>
        <line x1="50%" y1="50%" x2="22%" y2="25%" stroke="rgba(31,42,68,0.2)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="50%" y1="50%" x2="78%" y2="30%" stroke="rgba(31,42,68,0.2)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="50%" y1="50%" x2="15%" y2="60%" stroke="rgba(31,42,68,0.2)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="50%" y1="50%" x2="82%" y2="65%" stroke="rgba(31,42,68,0.2)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="50%" y1="50%" x2="55%" y2="80%" stroke="rgba(31,42,68,0.2)" strokeWidth="1.5" strokeDasharray="4,3" />
      </svg>
      <div className="link-node home" style={{ top: '38%', left: '50%', transform: 'translate(-50%,-50%)' }}>HOME</div>
      <div className="link-node small" style={{ top: '12%', left: '22%', transform: 'translate(-50%,-50%)' }}>BLOG</div>
      <div className="link-node small" style={{ top: '18%', left: '78%', transform: 'translate(-50%,-50%)' }}>●</div>
      <div className="link-node small" style={{ top: '58%', left: '15%', transform: 'translate(-50%,-50%)' }}>ABOUT</div>
      <div className="link-node small" style={{ top: '62%', left: '83%', transform: 'translate(-50%,-50%)' }}>DOCS</div>
      <div className="link-node small" style={{ top: '78%', left: '63%', transform: 'translate(-50%,-50%)' }}>PRICING</div>
      <div className="insight-badge">Insight: 3 Orphan pages found</div>
    </div>
  );
}

export default function DashboardPage({ activePage = "resource-pile", onNavigate }) {
  const [showProfile, setShowProfile] = useState(false);
  return (
    <>
      <style>{doodleStyles}</style>
      <div className="app-shell">
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
        <div className="main-content">
          {/* Topbar */}
          <div className="topbar">
            <div className="topbar-search">
              <span>🔍</span>
              <input placeholder="Search insights..." />
            </div>
            <span className="badge badge-geo">GEO READY</span>
            <span className="badge badge-seo">SEO ENGINE ON</span>
            <div className="topbar-right">
              <span className="topbar-greeting">Good morning, Aryan ✏️</span>
              <div className="bell-wrap">🔔<div className="bell-dot" /></div>
              <div className="topbar-avatar" onClick={() => setShowProfile((v) => !v)}>
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=aryan&backgroundColor=b6e3f4" style={{width:'100%',height:'100%'}} alt="av" />
              </div>
              {showProfile && <ProfileOverlay onClose={() => setShowProfile(false)} onNavigate={onNavigate} />}
            </div>
          </div>

          <div className="page-body">
            {/* Hero Row */}
            <div className="hero-row">
              <div className="organic-circle-wrap">
                <div className="organic-circle">
                  <span className="circle-label">ORGANIC POWER</span>
                  <span className="circle-score">92</span>
                  <span className="circle-subtitle">SEO SCORE</span>
                </div>
                <div className="top5-sticker">TOP 5% IN CATEGORY</div>
              </div>

              <div className="stats-grid">
                <div className="stat-card purple">
                  <span className="stat-icon">👁</span>
                  <div className="stat-label">Impressions</div>
                  <div className="stat-value">42.8k</div>
                  <div className="stat-change">+12.4%</div>
                </div>
                <div className="stat-card green">
                  <span className="stat-icon">🎯</span>
                  <div className="stat-label">Avg. CTR</div>
                  <div className="stat-value">4.2%</div>
                  <div className="stat-change">+0.8%</div>
                </div>
                <div className="stat-card gray">
                  <span className="stat-icon">⚡</span>
                  <div className="stat-label">Page Speed</div>
                  <div className="stat-value">0.9s</div>
                  <div className="stat-tag">FAST</div>
                </div>
                <div className="stat-card yellow">
                  <span className="stat-icon">🔗</span>
                  <div className="stat-label">Backlinks</div>
                  <div className="stat-value">1,204</div>
                  <div className="stat-change">+15 new</div>
                </div>
              </div>
            </div>

            {/* Lower Row */}
            <div className="lower-row">
              <div className="section-card">
                <span className="pencil-icon">✏️</span>
                <div className="section-title">Keyword Ranking Trends</div>
                <div className="section-subtitle">Hand-drawn trajectory of top 5 keywords</div>
                <KeywordChart />
              </div>
              <div className="section-card lavender">
                <div className="section-title">Internal Linking Map</div>
                <div className="section-subtitle">Visualization of link density & equity</div>
                <LinkMap />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
