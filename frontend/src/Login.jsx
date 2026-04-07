import React, { useState } from "react";
import { api } from "./api/client";

const BookIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{
    background: '#E0C3FC',
    border: '3px solid #1F2A44',
    padding: '4px',
    borderRadius: '4px',
    boxShadow: '3px 3px 0px #1F2A44'
  }}>
    <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="#1F2A44" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2Z" stroke="#1F2A44" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const Coin = ({ size = 120, rotate = 0, style, delay = 0, duration = 4 }) => (
  <div style={{
    position: 'absolute',
    width: `${size}px`,
    height: `${size}px`,
    ...style
  }}>
    <div style={{ width: '100%', height: '100%', animation: `coin-float ${duration}s ease-in-out ${delay}s infinite` }}>
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ filter: 'drop-shadow(8px 8px 0px #1F2A44)', transform: `rotate(${rotate}deg)` }}>
        {/* Outer Coin */}
        <circle cx="50" cy="50" r="46" fill="#E0C3FC" stroke="#1F2A44" strokeWidth="4" />
        {/* Inner Ring */}
        <circle cx="50" cy="50" r="34" stroke="#1F2A44" strokeWidth="3" opacity="0.6" />
        {/* Top Highlight Curve */}
        <path d="M 20 50 A 30 30 0 0 1 50 20" stroke="rgba(255,255,255,0.8)" strokeWidth="6" strokeLinecap="round" />
        {/* Small Star / Imprint */}
        <path d="M50 35 L54 45 L65 45 L56 52 L60 62 L50 56 L40 62 L44 52 L35 45 L46 45 Z" fill="#1F2A44" />
      </svg>
    </div>
  </div>
);

export default function LoginPage({ onNavigate }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let res;
      if (mode === "signup") {
        const cleanUsername = username.trim();
        const cleanEmail = email.trim();
        if (cleanUsername.length < 2) {
          throw new Error("Username must be at least 2 characters.");
        }
        if (cleanEmail.length < 5 || !cleanEmail.includes("@")) {
          throw new Error("Please enter a valid email address.");
        }
        if (password.length < 8) {
          throw new Error("Password must be at least 8 characters.");
        }
        res = await api.auth.signup({
          username: cleanUsername,
          email: cleanEmail,
          password,
        });
      } else {
        const cleanEmail = email.trim();
        if (cleanEmail.length < 5 || !cleanEmail.includes("@")) {
          throw new Error("Please enter a valid email address.");
        }
        if (password.length < 8) {
          throw new Error("Password must be at least 8 characters.");
        }
        res = await api.auth.login({
          email: cleanEmail,
          password,
        });
      }
      if (res?.user) {
        window.localStorage.setItem("blogy:user", JSON.stringify(res.user));
      }
      onNavigate("journal");
    } catch (err) {
      setError(err?.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      background: '#F5EBDD',
      overflow: 'hidden',
      position: 'relative',
      fontFamily: "'Nunito', sans-serif",
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      
      {/* Background Dot Grid */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'linear-gradient(rgba(31,42,68,0.06) 2px, transparent 2px), linear-gradient(90deg, rgba(31,42,68,0.06) 2px, transparent 2px)',
        backgroundSize: '40px 40px',
        zIndex: 0
      }} />

      <style>{`
        @keyframes coin-float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-12px) rotate(4deg); }
        }
      `}</style>

      {/* --- SCATTERED COINS MATCHING IMAGE --- */}
      {/* Top Left (Huge, fully on-screen) */}
      <Coin size={350} rotate={-15} delay={0} duration={5} style={{ top: '100px', left: '40px' }} />
      {/* Middle Left (Shifted lower down & fully visible) */}
      <Coin size={180} rotate={15} delay={1.5} duration={4.5} style={{ top: '70%', left: '40px', transform: 'translateY(-50%)' }} />
      {/* Bottom Left (Shifted right) */}
      <Coin size={180} rotate={20} delay={0.5} duration={4} style={{ bottom: '-60px', left: '18%' }} />
      {/* Top Right */}
      <Coin size={150} rotate={-25} delay={2} duration={5.5} style={{ top: '10%', right: '15%' }} />
      {/* Middle Right (Large, fully on-screen) */}
      <Coin size={300} rotate={-10} delay={1} duration={6} style={{ top: '40%', right: '40px', transform: 'translateY(-50%)' }} />
      {/* Bottom Right */}
      <Coin size={240} rotate={-5} delay={2.5} duration={5} style={{ bottom: '-80px', right: '5%' }} />

      {/* --- LOGIN CONTAINER --- */}
      <div style={{
        position: 'relative',
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        
        <BookIcon />
        
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '900',
          color: '#1F2A44',
          marginTop: '16px',
          marginBottom: '4px'
        }}>
          Welcome Back
        </h1>
        <p style={{
          fontSize: '1rem',
          color: '#4A5568',
          fontWeight: '600',
          marginBottom: '24px'
        }}>
          {mode === "signup" ? "Sign up for your account" : "Login to your account"}
        </p>

        {/* Login Card */}
        <form onSubmit={handleSubmit} style={{
          background: '#FFFFFF',
          border: '4px solid #1F2A44',
          boxShadow: '8px 8px 0px #1F2A44',
          borderRadius: '2px', // Brutalist sharp corners
          padding: '40px',
          width: '420px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          
          {mode === "signup" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <label style={{ fontSize: "0.85rem", fontWeight: "800", color: "#1F2A44", textTransform: "uppercase" }}>
                Username
              </label>
              <input
                required
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  padding: "12px 16px",
                  fontSize: "1rem",
                  fontFamily: "'Nunito', sans-serif",
                  border: "2px solid #1F2A44",
                  borderRadius: "0px",
                  outline: "none",
                  background: "#fff",
                  color: "#1F2A44",
                }}
              />
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: '800', color: '#1F2A44', textTransform: 'uppercase' }}>
              Email
            </label>
            <input 
              required
              type="email" 
              placeholder="Enter email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                padding: '12px 16px',
                fontSize: '1rem',
                fontFamily: "'Nunito', sans-serif",
                border: '2px solid #1F2A44',
                borderRadius: '0px',
                outline: 'none',
                background: '#fff',
                color: '#1F2A44'
              }}
              onFocus={(e) => { e.target.style.boxShadow = '3px 3px 0px rgba(31,42,68,0.2)'; e.target.style.transform = 'translate(-2px, -2px)'; e.target.style.transition = 'all 0.1s'; }}
              onBlur={(e) => { e.target.style.boxShadow = 'none'; e.target.style.transform = 'none'; }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: '800', color: '#1F2A44', textTransform: 'uppercase' }}>
              Password
            </label>
            <input 
              required
              type="password" 
              placeholder="Enter password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                padding: '12px 16px',
                fontSize: '1rem',
                fontFamily: "'Nunito', sans-serif",
                border: '2px solid #1F2A44',
                borderRadius: '0px',
                outline: 'none',
                background: '#fff',
                color: '#1F2A44'
              }}
              onFocus={(e) => { e.target.style.boxShadow = '3px 3px 0px rgba(31,42,68,0.2)'; e.target.style.transform = 'translate(-2px, -2px)'; e.target.style.transition = 'all 0.1s'; }}
              onBlur={(e) => { e.target.style.boxShadow = 'none'; e.target.style.transform = 'none'; }}
            />
          </div>

          <button 
            type="submit"
            disabled={loading}
            style={{
              background: '#1F2A44',
              border: '3px solid #1F2A44',
              boxShadow: '4px 4px 0px rgba(31,42,68,0.4)',
              color: '#FFC857',
              fontSize: '1.2rem',
              fontWeight: '800',
              padding: '12px',
              marginTop: '10px',
              cursor: 'pointer',
              transition: 'transform 0.1s, box-shadow 0.1s'
            }}
            onMouseDown={(e) => { e.target.style.transform = 'translate(4px, 4px)'; e.target.style.boxShadow = '0px 0px 0px transparent'; }}
            onMouseUp={(e) => { e.target.style.transform = 'translate(0px, 0px)'; e.target.style.boxShadow = '4px 4px 0px rgba(31,42,68,0.4)'; }}
          >
            {loading ? "Please wait..." : mode === "signup" ? "Create Account" : "Login"}
          </button>

          {error && (
            <div style={{ color: "#B3261E", fontSize: "0.9rem", fontWeight: 700, textAlign: "center" }}>
              {error}
            </div>
          )}

          <p style={{
            textAlign: 'center',
            fontSize: '0.9rem',
            color: '#4A5568',
            marginTop: '8px'
          }}>
            {mode === "login" ? "Don't have an account? " : "Already have an account? "}
            <span 
              onClick={() => setMode((m) => (m === "login" ? "signup" : "login"))} 
              style={{ color: '#92681A', fontWeight: '800', cursor: 'pointer', textDecoration: 'underline' }}
            >
              {mode === "login" ? "Sign Up" : "Login"}
            </span>
          </p>

        </form>
      </div>
      
      {/* Back to Home Button at Top Left */}
      <div 
        onClick={() => onNavigate('landing')}
        style={{
          position: 'absolute',
          top: '32px',
          left: '32px',
          fontFamily: "'Caveat', cursive",
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: '#1F2A44',
          cursor: 'pointer',
          zIndex: 20
        }}
      >
        ← Back to Scrapbook
      </div>

    </div>
  );
}