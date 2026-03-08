import { useState, useRef, useCallback } from "react";

const API_BASE = "http://localhost:8000";

const AGENTS = [
  { id: 1, name: "Analyzer",      icon: "🔍", desc: "Understands legacy code structure and logic",         color: "#00d4aa" },
  { id: 2, name: "IR Generator",  icon: "🔀", desc: "Converts logic into language-agnostic pseudocode",    color: "#4f8ef7" },
  { id: 3, name: "Translator",    icon: "⚡", desc: "Converts pseudocode into modern Python or Java",      color: "#c084fc" },
  { id: 4, name: "Debugger",      icon: "🐛", desc: "Validates and fixes errors in the generated code",    color: "#f59e0b" },
  { id: 5, name: "Documenter",    icon: "📚", desc: "Generates full technical documentation",              color: "#f472b6" },
];

const TABS = [
  { id: "analysis",           label: "🔍 Analysis",        agent: 1, color: "#00d4aa" },
  { id: "pseudocode",         label: "🔀 Pseudocode IR",   agent: 2, color: "#4f8ef7" },
  { id: "translated_code",    label: "⚡ Translated",      agent: 3, color: "#c084fc" },
  { id: "debug",              label: "🐛 Debug Report",    agent: 4, color: "#f59e0b" },
  { id: "corrected_code",     label: "✅ Final Code",      agent: 4, color: "#f59e0b" },
  { id: "full_documentation", label: "📚 Docs",            agent: 5, color: "#f472b6" },
];

const SAMPLE_COBOL = `       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL-CALC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-EMPLOYEE-NAME        PIC X(30) VALUE SPACES.
       01  WS-HOURS-WORKED         PIC 9(3)V9(2) VALUE ZEROS.
       01  WS-HOURLY-RATE          PIC 9(5)V9(2) VALUE ZEROS.
       01  WS-GROSS-PAY            PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-OVERTIME-HOURS       PIC 9(3)V9(2) VALUE ZEROS.
       01  WS-TAX-RATE             PIC 9(1)V9(4) VALUE 0.2000.
       01  WS-TAX-DEDUCTION        PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-NET-PAY              PIC 9(7)V9(2) VALUE ZEROS.
       01  WS-OVERTIME-THRESHOLD   PIC 9(3) VALUE 40.
       01  WS-OVERTIME-MULTIPLIER  PIC 9(1)V9(1) VALUE 1.5.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY "Enter Employee Name: "
           ACCEPT WS-EMPLOYEE-NAME
           DISPLAY "Enter Hours Worked: "
           ACCEPT WS-HOURS-WORKED
           DISPLAY "Enter Hourly Rate: "
           ACCEPT WS-HOURLY-RATE
           IF WS-HOURS-WORKED > WS-OVERTIME-THRESHOLD
               COMPUTE WS-OVERTIME-HOURS = WS-HOURS-WORKED - WS-OVERTIME-THRESHOLD
               COMPUTE WS-GROSS-PAY = (WS-OVERTIME-THRESHOLD * WS-HOURLY-RATE) + (WS-OVERTIME-HOURS * WS-HOURLY-RATE * WS-OVERTIME-MULTIPLIER)
           ELSE
               COMPUTE WS-GROSS-PAY = WS-HOURS-WORKED * WS-HOURLY-RATE
           END-IF
           COMPUTE WS-TAX-DEDUCTION = WS-GROSS-PAY * WS-TAX-RATE
           COMPUTE WS-NET-PAY = WS-GROSS-PAY - WS-TAX-DEDUCTION
           DISPLAY "Net Pay: $" WS-NET-PAY
           STOP RUN.`;

const C = {
  bg: "#080a0f",
  surface: "#0e1117",
  card: "#12161f",
  border: "#1a1f2e",
  borderHover: "#252b3d",
  textPrimary: "#e2e8f0",
  textSecondary: "#6b7280",
  textMuted: "#374151",
};

function AgentCard({ agent, status }) {
  const isActive = status === "running";
  const isDone = status === "done";
  return (
    <div style={{
      padding: "14px 16px",
      borderRadius: 12,
      background: isDone ? `${agent.color}0d` : isActive ? `${agent.color}08` : C.surface,
      border: `1px solid ${isDone ? agent.color + "35" : isActive ? agent.color + "25" : C.border}`,
      display: "flex", alignItems: "center", gap: 12,
      transition: "all 0.5s ease",
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        background: isDone ? agent.color : isActive ? `${agent.color}20` : C.card,
        border: `1.5px solid ${isDone || isActive ? agent.color : C.border}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: isDone ? 14 : 16,
        boxShadow: isActive ? `0 0 16px ${agent.color}50` : isDone ? `0 0 8px ${agent.color}30` : "none",
        transition: "all 0.5s ease",
        animation: isActive ? "agentPulse 1.5s ease infinite" : "none",
      }}>
        {isDone ? "✓" : agent.icon}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 13, fontWeight: 700,
          color: isDone ? agent.color : isActive ? C.textPrimary : C.textSecondary,
          fontFamily: "'Space Grotesk', sans-serif",
          transition: "color 0.4s",
        }}>
          Agent {agent.id}: {agent.name}
        </div>
        <div style={{ fontSize: 11, color: C.textMuted, marginTop: 2, lineHeight: 1.4 }}>
          {agent.desc}
        </div>
      </div>
      <div style={{
        fontSize: 11, fontWeight: 600,
        color: isDone ? agent.color : isActive ? agent.color : C.textMuted,
        fontFamily: "monospace",
        flexShrink: 0,
        opacity: isDone || isActive ? 1 : 0.4,
      }}>
        {isDone ? "DONE" : isActive ? "RUNNING" : "IDLE"}
      </div>
    </div>
  );
}

function DropZone({ onFileSelect, selectedFile, disabled }) {
  const [drag, setDrag] = useState(false);
  const ref = useRef();
  const onDrop = useCallback((e) => {
    e.preventDefault(); setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) onFileSelect(f);
  }, [onFileSelect]);

  return (
    <div
      onClick={() => !disabled && ref.current?.click()}
      onDragOver={e => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={onDrop}
      style={{
        border: `2px dashed ${drag ? "#00d4aa" : selectedFile ? "#00d4aa60" : C.border}`,
        borderRadius: 12, padding: "28px 20px", textAlign: "center",
        cursor: disabled ? "not-allowed" : "pointer",
        background: drag ? "#00d4aa0a" : selectedFile ? "#00d4aa06" : "transparent",
        transition: "all 0.3s",
      }}
    >
      <input ref={ref} type="file" accept=".cbl,.cob,.cpy,.f,.for,.f90,.f95"
        style={{ display: "none" }} disabled={disabled}
        onChange={e => e.target.files[0] && onFileSelect(e.target.files[0])} />
      {selectedFile ? (
        <>
          <div style={{ fontSize: 28, marginBottom: 6 }}>📄</div>
          <div style={{ color: "#00d4aa", fontWeight: 700, fontSize: 14, fontFamily: "monospace" }}>{selectedFile.name}</div>
          <div style={{ color: C.textSecondary, fontSize: 11, marginTop: 4 }}>{(selectedFile.size / 1024).toFixed(1)} KB · click to change</div>
        </>
      ) : (
        <>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🗂️</div>
          <div style={{ color: C.textPrimary, fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Drop legacy code file</div>
          <div style={{ color: C.textSecondary, fontSize: 11 }}>.cbl · .cob · .f · .for · .f90</div>
        </>
      )}
    </div>
  );
}

function CodeBlock({ content }) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(content); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div style={{ position: "relative" }}>
      <button onClick={copy} style={{
        position: "absolute", top: 10, right: 10, zIndex: 2,
        background: copied ? "#00d4aa" : C.surface, border: `1px solid ${copied ? "#00d4aa" : C.border}`,
        borderRadius: 6, padding: "3px 10px", color: copied ? "#080a0f" : C.textSecondary,
        fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all 0.2s", fontFamily: "monospace",
      }}>{copied ? "✓ Copied" : "Copy"}</button>
      <pre style={{
        background: "#0a0d14", border: `1px solid ${C.border}`, borderRadius: 10,
        padding: 20, margin: 0, overflowX: "auto", overflowY: "auto", maxHeight: 500,
        fontSize: 12.5, lineHeight: 1.7, color: C.textPrimary,
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        whiteSpace: "pre-wrap", wordBreak: "break-word",
      }}>{content}</pre>
    </div>
  );
}

function ProseBlock({ content }) {
  return (
    <div style={{
      background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10,
      padding: "24px 28px", maxHeight: 520, overflowY: "auto",
    }}>
      <pre style={{
        fontFamily: "'Space Grotesk', sans-serif", whiteSpace: "pre-wrap",
        wordBreak: "break-word", color: C.textPrimary, fontSize: 13.5, lineHeight: 1.9, margin: 0,
      }}>{content}</pre>
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [targetLang, setTargetLang] = useState("python");
  const [useDemo, setUseDemo] = useState(false);
  const [loading, setLoading] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState({});
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("analysis");

  const setAgent = (id, status) => setAgentStatuses(prev => ({ ...prev, [id]: status }));

  const handleRun = async () => {
    setError(null); setResults(null);
    setAgentStatuses({});

    if (!file && !useDemo) { setError("Please upload a file or enable demo mode."); return; }

    setLoading(true);

    try {
      let uploadFile = file;
      if (useDemo) {
        const blob = new Blob([SAMPLE_COBOL], { type: "text/plain" });
        uploadFile = new File([blob], "payroll_demo.cbl", { type: "text/plain" });
      }

      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("target_language", targetLang);

      // Simulate sequential agent activation while waiting for real response
      setAgent(1, "running");
      const responsePromise = fetch(`${API_BASE}/api/analyze`, { method: "POST", body: formData });

      // Stagger the visual agent indicators
      const delays = [0, 6000, 12000, 18000, 24000];
      delays.forEach((delay, i) => {
        setTimeout(() => {
          if (i > 0) setAgent(i, "done");
          if (i < 5) setAgent(i + 1, "running");
        }, delay);
      });

      const response = await responsePromise;

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();

      // Mark all done
      setAgentStatuses({ 1: "done", 2: "done", 3: "done", 4: "done", 5: "done" });
      setResults(data);
      setActiveTab("analysis");

    } catch (err) {
      if (err.message.includes("fetch") || err.message.includes("Failed to fetch")) {
        setError("Cannot connect to the backend.\n\nMake sure the FastAPI server is running:\n  cd NewGenCode\n  venv\\Scripts\\activate\n  python server.py");
      } else {
        setError(err.message);
      }
      setAgentStatuses({});
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => { setResults(null); setError(null); setFile(null); setAgentStatuses({}); };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { background: ${C.bg}; color: ${C.textPrimary}; font-family: 'Space Grotesk', sans-serif; min-height: 100vh; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: ${C.surface}; }
        ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 3px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes agentPulse { 0%,100% { box-shadow: 0 0 16px var(--c, #00d4aa)50; } 50% { box-shadow: 0 0 28px var(--c, #00d4aa)80; } }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
      `}</style>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header style={{
        height: 60, padding: "0 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: `1px solid ${C.border}`,
        background: `${C.surface}e0`, backdropFilter: "blur(16px)",
        position: "sticky", top: 0, zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, #00d4aa, #4f8ef7)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16,
            boxShadow: "0 0 14px #00d4aa40",
          }}>⚙</div>
          <div>
            <span style={{ fontSize: 17, fontWeight: 700, letterSpacing: "-0.3px" }}>
              NewGen<span style={{ color: "#00d4aa" }}>Code</span>
            </span>
            <span style={{ fontSize: 10, color: C.textMuted, marginLeft: 10, fontFamily: "monospace", letterSpacing: "1.5px" }}>
              5-AGENT PIPELINE
            </span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {AGENTS.map(a => (
            <div key={a.id} style={{
              padding: "3px 8px", borderRadius: 5,
              background: `${a.color}10`, border: `1px solid ${a.color}25`,
              fontSize: 10, color: a.color, fontWeight: 600, fontFamily: "monospace",
            }}>
              {a.icon} {a.name}
            </div>
          ))}
        </div>
      </header>

      <main style={{ maxWidth: 1280, margin: "0 auto", padding: "36px 28px" }}>

        {!results ? (
          <div style={{ animation: "slideUp 0.5s ease" }}>

            {/* Hero */}
            <div style={{ textAlign: "center", marginBottom: 48 }}>
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                padding: "5px 14px", borderRadius: 20, marginBottom: 20,
                background: "#00d4aa10", border: "1px solid #00d4aa30",
                fontSize: 11, color: "#00d4aa", fontWeight: 600, fontFamily: "monospace", letterSpacing: "1.5px",
              }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#00d4aa", display: "inline-block" }} />
                COBOL / FORTRAN → PYTHON / JAVA
              </div>
              <h1 style={{ fontSize: 48, fontWeight: 700, lineHeight: 1.1, letterSpacing: "-2px", marginBottom: 14 }}>
                Modernize Legacy Code<br />
                <span style={{ color: "#00d4aa" }}>with 5 AI Agents</span>
              </h1>
              <p style={{ fontSize: 16, color: C.textSecondary, maxWidth: 480, margin: "0 auto", lineHeight: 1.7 }}>
                Drop your COBOL or FORTRAN source. Five specialized AI agents analyze, convert, translate, debug, and document your code automatically.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28 }}>

              {/* Left panel */}
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 16, padding: 28 }}>
                <div style={{ fontSize: 12, color: C.textSecondary, fontWeight: 600, letterSpacing: "1px", marginBottom: 18, fontFamily: "monospace" }}>
                  INPUT CONFIGURATION
                </div>

                {/* Demo toggle */}
                <div
                  onClick={() => setUseDemo(!useDemo)}
                  style={{
                    display: "flex", alignItems: "center", gap: 10, padding: "12px 14px",
                    background: useDemo ? "#f59e0b0d" : "transparent",
                    border: `1px solid ${useDemo ? "#f59e0b40" : C.border}`,
                    borderRadius: 10, cursor: "pointer", marginBottom: 14, transition: "all 0.3s",
                  }}
                >
                  <div style={{
                    width: 18, height: 18, borderRadius: 4, flexShrink: 0,
                    background: useDemo ? "#f59e0b" : "transparent",
                    border: `2px solid ${useDemo ? "#f59e0b" : C.textSecondary}`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 10, color: "#000", transition: "all 0.2s",
                  }}>{useDemo ? "✓" : ""}</div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: useDemo ? "#f59e0b" : C.textPrimary }}>
                      Demo: COBOL Payroll Calculator
                    </div>
                    <div style={{ fontSize: 11, color: C.textMuted }}>Test without uploading a file</div>
                  </div>
                </div>

                <DropZone onFileSelect={setFile} selectedFile={file} disabled={loading || useDemo} />

                {/* Target language */}
                <div style={{ marginTop: 20 }}>
                  <div style={{ fontSize: 11, color: C.textSecondary, fontWeight: 600, letterSpacing: "1px", marginBottom: 10, fontFamily: "monospace" }}>
                    TARGET LANGUAGE
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {[{ id: "python", icon: "🐍", label: "Python 3" }, { id: "java", icon: "☕", label: "Java 17" }].map(l => (
                      <button key={l.id} onClick={() => setTargetLang(l.id)} style={{
                        flex: 1, padding: "11px 14px",
                        background: targetLang === l.id ? "#00d4aa15" : "transparent",
                        border: `2px solid ${targetLang === l.id ? "#00d4aa" : C.border}`,
                        borderRadius: 9, cursor: "pointer",
                        color: targetLang === l.id ? "#00d4aa" : C.textSecondary,
                        fontWeight: 700, fontSize: 13, fontFamily: "'Space Grotesk', sans-serif",
                        transition: "all 0.2s", display: "flex", alignItems: "center", justifyContent: "center", gap: 7,
                      }}>{l.icon} {l.label}</button>
                    ))}
                  </div>
                </div>

                {/* Run button */}
                <button
                  onClick={handleRun}
                  disabled={loading || (!file && !useDemo)}
                  style={{
                    width: "100%", marginTop: 20, padding: "15px 20px",
                    background: loading || (!file && !useDemo)
                      ? C.border
                      : "linear-gradient(135deg, #00d4aa, #00a882)",
                    border: "none", borderRadius: 11,
                    color: loading || (!file && !useDemo) ? C.textMuted : "#080a0f",
                    fontSize: 14, fontWeight: 700, cursor: loading || (!file && !useDemo) ? "not-allowed" : "pointer",
                    fontFamily: "'Space Grotesk', sans-serif",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                    transition: "all 0.3s",
                    boxShadow: !loading && (file || useDemo) ? "0 0 24px #00d4aa35" : "none",
                  }}
                >
                  {loading ? (
                    <>
                      <div style={{
                        width: 16, height: 16, border: "2px solid transparent",
                        borderTopColor: "#080a0f", borderRadius: "50%",
                        animation: "spin 0.7s linear infinite",
                      }} />
                      Agents Running...
                    </>
                  ) : <>⚡ Run 5-Agent Pipeline</>}
                </button>

                {error && (
                  <div style={{
                    marginTop: 16, padding: 16,
                    background: "#ff5a5a0a", border: "1px solid #ff5a5a30", borderRadius: 10,
                    animation: "fadeIn 0.3s ease",
                  }}>
                    <div style={{ color: "#ff5a5a", fontWeight: 700, fontSize: 13, marginBottom: 6 }}>⚠ Error</div>
                    <pre style={{ color: C.textSecondary, fontSize: 12, fontFamily: "monospace", whiteSpace: "pre-wrap" }}>{error}</pre>
                  </div>
                )}
              </div>

              {/* Right panel — Agent pipeline */}
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 16, padding: 28 }}>
                <div style={{ fontSize: 12, color: C.textSecondary, fontWeight: 600, letterSpacing: "1px", marginBottom: 18, fontFamily: "monospace" }}>
                  AGENT PIPELINE STATUS
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {AGENTS.map((agent, i) => (
                    <div key={agent.id}>
                      <AgentCard agent={agent} status={agentStatuses[agent.id] || "idle"} />
                      {i < AGENTS.length - 1 && (
                        <div style={{
                          marginLeft: 18, width: 2, height: 14,
                          background: agentStatuses[agent.id] === "done"
                            ? `linear-gradient(to bottom, ${agent.color}, ${AGENTS[i+1].color})`
                            : C.border,
                          transition: "background 0.5s",
                        }} />
                      )}
                    </div>
                  ))}
                </div>

                {!loading && Object.keys(agentStatuses).length === 0 && (
                  <div style={{
                    marginTop: 20, padding: 14,
                    background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10,
                  }}>
                    <div style={{ fontSize: 12, color: C.textMuted, lineHeight: 1.7 }}>
                      Each agent runs in sequence, passing its output to the next.<br />
                      Total pipeline time: ~30–60 seconds depending on code size.
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

        ) : (

          /* ── Results ─────────────────────────────────────────────────── */
          <div style={{ animation: "slideUp 0.5s ease" }}>

            {/* Results header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
              <div>
                <div style={{ fontSize: 10, color: "#00d4aa", fontFamily: "monospace", letterSpacing: "2px", marginBottom: 6 }}>
                  ✓ ALL 5 AGENTS COMPLETE
                </div>
                <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: "-0.5px" }}>
                  <span style={{ color: "#00d4aa" }}>{results.filename}</span>
                  <span style={{ fontSize: 15, color: C.textSecondary, fontWeight: 400, marginLeft: 12 }}>
                    {results.source_language?.toUpperCase()} → {results.target_language?.toUpperCase()}
                  </span>
                </h2>
              </div>
              <button onClick={handleReset} style={{
                padding: "9px 18px", borderRadius: 9,
                background: "transparent", border: `1px solid ${C.border}`,
                color: C.textSecondary, cursor: "pointer", fontSize: 13, fontWeight: 600,
                transition: "all 0.2s", fontFamily: "'Space Grotesk', sans-serif",
              }}
                onMouseEnter={e => { e.target.style.borderColor = "#00d4aa"; e.target.style.color = "#00d4aa"; }}
                onMouseLeave={e => { e.target.style.borderColor = C.border; e.target.style.color = C.textSecondary; }}
              >← New File</button>
            </div>

            {/* Agent done pills */}
            <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
              {AGENTS.map(a => (
                <div key={a.id} style={{
                  padding: "4px 12px", borderRadius: 20,
                  background: `${a.color}10`, border: `1px solid ${a.color}30`,
                  display: "flex", alignItems: "center", gap: 6,
                  fontSize: 11, color: a.color, fontWeight: 700, fontFamily: "monospace",
                }}>
                  <span>✓</span> {a.icon} Agent {a.id}: {a.name}
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div style={{
              display: "flex", gap: 3, marginBottom: 18,
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: 4, overflowX: "auto",
            }}>
              {TABS.map(tab => (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
                  flex: 1, minWidth: 110, padding: "9px 12px",
                  background: activeTab === tab.id ? `${tab.color}18` : "transparent",
                  border: `1px solid ${activeTab === tab.id ? tab.color + "40" : "transparent"}`,
                  borderRadius: 9, cursor: "pointer",
                  color: activeTab === tab.id ? tab.color : C.textSecondary,
                  fontSize: 12, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif",
                  transition: "all 0.2s", whiteSpace: "nowrap",
                }}>{tab.label}</button>
              ))}
            </div>

            {/* Tab content */}
            <div style={{ animation: "fadeIn 0.3s ease" }}>
              {activeTab === "analysis"           && <ProseBlock content={results.analysis} />}
              {activeTab === "pseudocode"         && <CodeBlock content={results.pseudocode} />}
              {activeTab === "translated_code"    && <CodeBlock content={results.translated_code} />}
              {activeTab === "debug"              && <ProseBlock content={results.review_report} />}
              {activeTab === "corrected_code"     && <CodeBlock content={results.corrected_code} />}
              {activeTab === "full_documentation" && <ProseBlock content={results.full_documentation} />}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
