import { useState, useEffect, useRef } from "react";

const PIPELINE_STEPS = [
  { label: "Analyzing competitors...", icon: "🔍", duration: 800 },
  { label: "Extracting keyword gaps...", icon: "🧩", duration: 700 },
  { label: "Structuring blog outline...", icon: "🗂️", duration: 900 },
  { label: "Generating content...", icon: "✍️", duration: 1300 },
  { label: "Optimizing SEO...", icon: "📈", duration: 800 },
  { label: "Finalizing output...", icon: "✨", duration: 700 },
];

const TIPS = [
  "This may take a few seconds...",
  "Our AI is crafting high-quality content...",
  "Building SEO-optimized structure...",
  "Almost there — polishing your blog...",
];

const loaderStyles = `
  /* ===== Blog Generation Loader ===== */
  .bgl-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 360px;
    padding: 40px 24px;
    gap: 28px;
  }

  .bgl-header {
    text-align: center;
    margin-bottom: 4px;
  }
  .bgl-header-icon {
    font-size: 36px;
    margin-bottom: 8px;
    animation: bgl-bounce 2s ease-in-out infinite;
  }
  .bgl-header-title {
    font-family: 'Nunito', sans-serif;
    font-weight: 900;
    font-size: 20px;
    color: #1F2A44;
    margin-bottom: 4px;
  }
  .bgl-header-sub {
    font-size: 13px;
    color: rgba(31,42,68,0.55);
    font-weight: 600;
  }

  /* Progress bar */
  .bgl-progress-track {
    width: 100%;
    max-width: 380px;
    height: 8px;
    background: rgba(31,42,68,0.08);
    border-radius: 100px;
    overflow: hidden;
    border: 1px solid rgba(31,42,68,0.08);
  }
  .bgl-progress-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #FFC857, #F4A4A4, #B8A8E3);
    background-size: 200% 100%;
    animation: bgl-gradient-shift 3s ease infinite;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Steps list */
  .bgl-steps {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    max-width: 340px;
  }

  .bgl-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    border-radius: 12px;
    font-family: 'Nunito', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: rgba(31,42,68,0.3);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1.5px solid transparent;
    opacity: 0;
    transform: translateY(8px);
  }
  .bgl-step.visible {
    opacity: 1;
    transform: translateY(0);
  }
  .bgl-step.completed {
    color: rgba(31,42,68,0.55);
    background: rgba(200, 230, 203, 0.25);
    border-color: rgba(45, 106, 79, 0.12);
  }
  .bgl-step.active {
    color: #1F2A44;
    background: rgba(255, 200, 87, 0.18);
    border-color: rgba(255, 200, 87, 0.5);
    box-shadow: 0 2px 8px rgba(255, 200, 87, 0.15);
  }
  .bgl-step.pending {
    color: rgba(31,42,68,0.25);
  }

  /* Step indicator icons */
  .bgl-step-indicator {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
    transition: all 0.3s ease;
  }
  .bgl-step.completed .bgl-step-indicator {
    background: #C8E6CB;
    color: #2D6A4F;
    border: 1.5px solid #2D6A4F;
  }
  .bgl-step.active .bgl-step-indicator {
    background: #FFC857;
    border: 1.5px solid #1F2A44;
    animation: bgl-pulse 1.5s ease-in-out infinite;
  }
  .bgl-step.pending .bgl-step-indicator {
    background: rgba(31,42,68,0.06);
    border: 1.5px solid rgba(31,42,68,0.1);
  }

  /* Tip message */
  .bgl-tip {
    font-size: 12px;
    font-weight: 600;
    color: rgba(31,42,68,0.45);
    font-style: italic;
    text-align: center;
    min-height: 18px;
    transition: opacity 0.5s ease;
  }

  /* Animations */
  @keyframes bgl-pulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255,200,87,0.4); }
    50% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(255,200,87,0); }
  }
  @keyframes bgl-bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }
  @keyframes bgl-gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

export default function BlogGenerationLoader() {
  const [currentStep, setCurrentStep] = useState(0);
  const [visibleSteps, setVisibleSteps] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);
  const timerRef = useRef(null);
  const tipTimerRef = useRef(null);

  // Step-by-step progression
  useEffect(() => {
    // Reveal steps one-by-one first, then advance active step
    const revealInterval = setInterval(() => {
      setVisibleSteps((prev) => {
        if (prev < PIPELINE_STEPS.length) return prev + 1;
        clearInterval(revealInterval);
        return prev;
      });
    }, 260);

    return () => clearInterval(revealInterval);
  }, []);

  useEffect(() => {
    // Start advancing through steps after all are visible
    const startDelay = setTimeout(
      () => {
        const advanceStep = () => {
          setCurrentStep((prev) => {
            const next = prev + 1;
            if (next >= PIPELINE_STEPS.length) {
              // Stay on last step — backend is still working
              return PIPELINE_STEPS.length - 1;
            }
            // Schedule next step
            timerRef.current = setTimeout(
              advanceStep,
              PIPELINE_STEPS[next].duration,
            );
            return next;
          });
        };

        timerRef.current = setTimeout(advanceStep, PIPELINE_STEPS[0].duration);
      },
      PIPELINE_STEPS.length * 260 + 320,
    );

    return () => {
      clearTimeout(startDelay);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  // Rotate tips
  useEffect(() => {
    tipTimerRef.current = setInterval(() => {
      setTipIndex((prev) => (prev + 1) % TIPS.length);
    }, 4000);
    return () => clearInterval(tipTimerRef.current);
  }, []);

  const progressPercent = Math.min(
    ((currentStep + 1) / PIPELINE_STEPS.length) * 100,
    95, // Never hit 100% while loading — feels more honest
  );

  return (
    <>
      <style>{loaderStyles}</style>
      <div className="bgl-container">
        <div className="bgl-header">
          <div className="bgl-header-icon">⚡</div>
          <div className="bgl-header-title">Generating Your Blog</div>
          <div className="bgl-header-sub">
            Running the full AI pipeline for maximum quality
          </div>
        </div>

        {/* Progress bar */}
        <div className="bgl-progress-track">
          <div
            className="bgl-progress-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Steps */}
        <div className="bgl-steps">
          {PIPELINE_STEPS.map((step, i) => {
            let stepClass = "bgl-step";
            if (i < visibleSteps) stepClass += " visible";
            if (i < currentStep) stepClass += " completed";
            else if (i === currentStep) stepClass += " active";
            else stepClass += " pending";

            return (
              <div key={i} className={stepClass}>
                <div className="bgl-step-indicator">
                  {i < currentStep ? "✓" : step.icon}
                </div>
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>

        {/* Dynamic tip */}
        <div className="bgl-tip">{TIPS[tipIndex]}</div>
      </div>
    </>
  );
}
