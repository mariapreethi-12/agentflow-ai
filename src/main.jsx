import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  Check,
  ChevronRight,
  ClipboardCheck,
  Copy,
  Code2,
  Database,
  FileJson,
  FileText,
  GitBranch,
  LayoutDashboard,
  Play,
  RefreshCcw,
  Save,
  Send,
  ShieldCheck,
  Sparkles,
  TestTube2,
  UserCheck,
} from "lucide-react";
import {
  artifactSchemas,
  createInitialProject,
  demoQuestions,
  flattenArtifact,
  generateArtifacts,
} from "./agentSchemas";
import { agentFlowApi } from "./api";
import "./styles.css";

const storageKey = "agentflow.currentProject.v1";

const stages = [
  {
    id: "intake",
    artifactKey: "clarifying_questions",
    label: "Idea Intake",
    agent: "PM Agent",
    icon: FileText,
    decision: "Answer questions",
  },
  {
    id: "prd",
    artifactKey: "prd",
    label: "PRD",
    agent: "Product Manager",
    icon: ClipboardCheck,
    decision: "Approve scope",
  },
  {
    id: "architecture",
    artifactKey: "architecture",
    label: "Architecture",
    agent: "Architect Agent",
    icon: Database,
    decision: "Approve design",
  },
  {
    id: "backend",
    artifactKey: "backend_plan",
    label: "Backend Code",
    agent: "Backend Agent",
    icon: Code2,
    decision: "Review files",
  },
  {
    id: "qa",
    artifactKey: "qa_plan",
    label: "QA Plan",
    agent: "QA Agent",
    icon: TestTube2,
    decision: "Approve tests",
  },
  {
    id: "review",
    artifactKey: "review_report",
    label: "Review",
    agent: "Reviewer Agent",
    icon: ShieldCheck,
    decision: "Request changes",
  },
];

function loadProject() {
  try {
    const saved = localStorage.getItem(storageKey);
    return saved ? JSON.parse(saved) : createInitialProject();
  } catch {
    return createInitialProject();
  }
}

function App() {
  const [project, setProject] = useState(loadProject);
  const [showSchema, setShowSchema] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [selectedFilePath, setSelectedFilePath] = useState("");
  const [syncState, setSyncState] = useState({
    mode: "local",
    label: "Local mode",
  });

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(project));
  }, [project]);

  useEffect(() => {
    let cancelled = false;

    async function connectBackend() {
      setSyncState({ mode: "connecting", label: "Connecting API" });
      try {
        await agentFlowApi.health();
        const backendProject = project.backendProjectId
          ? await agentFlowApi.getProject(project.backendProjectId).catch(() => null)
          : null;
        const syncedProject =
          backendProject || (await agentFlowApi.createProject(project));

        if (!cancelled) {
          setProject((current) => ({
            ...syncedProject,
            activeStage: current.activeStage || syncedProject.activeStage,
          }));
          setSyncState({ mode: "online", label: "API connected" });
        }
      } catch {
        if (!cancelled) {
          setSyncState({ mode: "local", label: "Local fallback" });
        }
      }
    }

    connectBackend();

    return () => {
      cancelled = true;
    };
  }, []);

  const activeIndex = stages.findIndex((stage) => stage.id === project.activeStage);
  const activeStage = stages[activeIndex] || stages[0];
  const approvedIds = Object.entries(project.approvals)
    .filter(([, approval]) => approval.approved)
    .map(([id]) => id);
  const progress = Math.round(((approvedIds.length - 1) / (stages.length - 1)) * 100);
  const currentArtifact = project.artifacts[activeStage.artifactKey];
  const schema = artifactSchemas[activeStage.artifactKey];
  const openRisks = project.artifacts.review_report.data.risks.length;
  const generatedFiles = project.generatedFiles || [];
  const chatMessages = project.chatMessages || [];
  const selectedFile =
    generatedFiles.find((file) => file.path === selectedFilePath) || generatedFiles[0];

  const lastSaved = useMemo(
    () =>
      new Intl.DateTimeFormat("en", {
        hour: "numeric",
        minute: "2-digit",
        month: "short",
        day: "numeric",
      }).format(new Date(project.updatedAt)),
    [project.updatedAt]
  );

  function updateIdea(value) {
    commitProject((current) => ({
      ...current,
      idea: value,
      artifacts: generateArtifacts(value, current.answers),
    }));
  }

  function updateAnswer(index, value) {
    commitProject((current) => {
      const answers = { ...current.answers, [index]: value };
      return {
        ...current,
        answers,
        artifacts: generateArtifacts(current.idea, answers),
      };
    });
  }

  function setActiveStage(stageId) {
    commitProject((current) => ({
      ...current,
      activeStage: stageId,
    }));
  }

  function approveCurrentStage() {
    const current = stages[activeIndex];
    const next = stages[activeIndex + 1];

    commitProject((existing) => ({
      ...existing,
      activeStage: next ? next.id : existing.activeStage,
      approvals: {
        ...existing.approvals,
        [current.id]: {
          approved: true,
          approvedAt: new Date().toISOString(),
          note: current.decision,
        },
        ...(next && !existing.approvals[next.id]
          ? {
              [next.id]: {
                approved: false,
                approvedAt: null,
                note: "Waiting for human approval.",
              },
            }
          : {}),
      },
    }), {
      approval: {
        stage: current.id,
        note: current.decision,
      },
    });
  }

  function resetDemo() {
    const nextProject = createInitialProject();
    setProject(nextProject);
    setShowSchema(false);
    queueMicrotask(() => createBackendProject(nextProject));
  }

  async function sendChatMessage(event) {
    event.preventDefault();
    const content = chatInput.trim();
    if (!content) return;

    const localMessage = {
      role: "human",
      content,
      stage: activeStage.id,
      created_at: new Date().toISOString(),
    };
    setChatInput("");

    if (!project.backendProjectId) {
      commitProject((current) => ({
        ...current,
        chatMessages: [...(current.chatMessages || []), localMessage],
      }));
      return;
    }

    try {
      setSyncState({ mode: "saving", label: "Sending chat" });
      const synced = await agentFlowApi.addChatMessage(project.backendProjectId, localMessage);
      setProject((current) => ({ ...synced, activeStage: current.activeStage }));
      setSyncState({ mode: "online", label: "API synced" });
    } catch {
      setSyncState({ mode: "local", label: "Local fallback" });
      setProject((current) => ({
        ...current,
        chatMessages: [...(current.chatMessages || []), localMessage],
      }));
    }
  }

  async function generateRunnableFiles() {
    if (!project.backendProjectId) return;

    try {
      setSyncState({ mode: "saving", label: "Generating files" });
      const synced = await agentFlowApi.generateFiles(project.backendProjectId);
      setProject((current) => ({ ...synced, activeStage: current.activeStage }));
      setSelectedFilePath(synced.generatedFiles?.[0]?.path || "");
      setSyncState({ mode: "online", label: "Files generated" });
    } catch {
      setSyncState({ mode: "local", label: "Local fallback" });
    }
  }

  async function copySelectedFile() {
    if (!selectedFile) return;
    await navigator.clipboard.writeText(selectedFile.content);
  }

  function commitProject(updater, options = {}) {
    setProject((current) => {
      const next = {
        ...updater(current),
        updatedAt: new Date().toISOString(),
      };
      queueMicrotask(() => syncProject(next, options));
      return next;
    });
  }

  async function syncProject(nextProject, options = {}) {
    if (!nextProject.backendProjectId) {
      await createBackendProject(nextProject);
      return;
    }

    try {
      setSyncState({ mode: "saving", label: "Saving to API" });

      let synced = nextProject;
      if (options.approval) {
        await agentFlowApi.approveStage(
          nextProject.backendProjectId,
          options.approval.stage,
          options.approval.note
        );
      }

      synced = await agentFlowApi.updateProject(nextProject.backendProjectId, nextProject);
      setProject((current) => ({
        ...synced,
        activeStage: current.activeStage,
      }));
      setSyncState({ mode: "online", label: "API synced" });
    } catch {
      setSyncState({ mode: "local", label: "Local fallback" });
    }
  }

  async function createBackendProject(nextProject) {
    try {
      setSyncState({ mode: "saving", label: "Creating API project" });
      const synced = await agentFlowApi.createProject(nextProject);
      setProject((current) => ({
        ...synced,
        activeStage: current.activeStage,
      }));
      setSyncState({ mode: "online", label: "API connected" });
    } catch {
      setSyncState({ mode: "local", label: "Local fallback" });
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">
            <GitBranch size={20} />
          </span>
          <div>
            <strong>AgentFlow</strong>
            <small>Human-in-the-loop AI engineering</small>
          </div>
        </div>

        <nav className="stage-list" aria-label="Agent workflow">
          {stages.map((stage, index) => {
            const Icon = stage.icon;
            const isActive = stage.id === activeStage.id;
            const isApproved = approvedIds.includes(stage.id);
            return (
              <button
                className={`stage-button ${isActive ? "active" : ""}`}
                key={stage.id}
                onClick={() => setActiveStage(stage.id)}
                title={`${stage.agent}: ${stage.decision}`}
              >
                <span className={`stage-icon ${isApproved ? "done" : ""}`}>
                  {isApproved ? <Check size={16} /> : <Icon size={16} />}
                </span>
                <span>
                  <strong>{stage.label}</strong>
                  <small>{stage.agent}</small>
                </span>
                <em>{index + 1}</em>
              </button>
            );
          })}
        </nav>

        <div className="progress-panel">
          <div>
            <span>Demo readiness</span>
            <strong>{progress}%</strong>
          </div>
          <div className="progress-track">
            <span style={{ width: `${progress}%` }} />
          </div>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Saved project</p>
            <h1>{project.name}</h1>
            <p className="save-state">
              <Save size={15} />
              Saved locally at {lastSaved}
            </p>
            <p className={`api-state ${syncState.mode}`}>
              <span />
              {syncState.label}
            </p>
          </div>
          <div className="topbar-actions">
            <button className="icon-button" onClick={resetDemo} title="Reset demo">
              <RefreshCcw size={18} />
            </button>
            <button
              className={`icon-button ${showSchema ? "selected" : ""}`}
              onClick={() => setShowSchema((visible) => !visible)}
              title="Toggle artifact schema"
            >
              <FileJson size={18} />
            </button>
            <button className="primary-button" onClick={approveCurrentStage}>
              <UserCheck size={18} />
              Approve step
            </button>
          </div>
        </header>

        <section className="summary-strip">
          <Metric icon={LayoutDashboard} label="Agents" value="6" />
          <Metric icon={UserCheck} label="Approval gates" value="5" />
          <Metric icon={Sparkles} label="Schemas" value={Object.keys(artifactSchemas).length} />
          <Metric icon={AlertTriangle} label="Open risks" value={openRisks} />
        </section>

        <div className="content-grid">
          <section className="panel intake-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Product owner input</p>
                <h2>Idea and clarifying answers</h2>
              </div>
              <span className="status-pill">Auto-saved</span>
            </div>
            <label>
              Product idea
              <textarea
                value={project.idea}
                onChange={(event) => updateIdea(event.target.value)}
              />
            </label>
            <div className="questions">
              {demoQuestions.map((question, index) => (
                <label key={question}>
                  {question}
                  <input
                    value={project.answers[index] || ""}
                    onChange={(event) => updateAnswer(index, event.target.value)}
                  />
                </label>
              ))}
            </div>
          </section>

          <section className="panel artifact-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">{schema.agent} output</p>
                <h2>{currentArtifact.title}</h2>
              </div>
              <span
                className={`status-pill ${
                  approvedIds.includes(activeStage.id) ? "approved" : ""
                }`}
              >
                {approvedIds.includes(activeStage.id) ? "Approved" : "Pending"}
              </span>
            </div>

            {showSchema ? (
              <SchemaCard artifactKey={activeStage.artifactKey} schema={schema} />
            ) : (
              <Artifact artifact={currentArtifact} />
            )}
          </section>
        </div>

        <section className="timeline">
          {stages.map((stage) => {
            const Icon = stage.icon;
            const isActive = stage.id === activeStage.id;
            const isApproved = approvedIds.includes(stage.id);
            return (
              <button
                key={stage.id}
                className={`timeline-step ${isActive ? "active" : ""}`}
                onClick={() => setActiveStage(stage.id)}
                title={stage.decision}
              >
                <Icon size={18} />
                <span>{stage.label}</span>
                {isApproved && <Check size={15} />}
              </button>
            );
          })}
        </section>

        <section className="builder-grid">
          <section className="panel chat-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Human chat</p>
                <h2>Tag the agent team</h2>
              </div>
              <span className="status-pill">{activeStage.label}</span>
            </div>
            <div className="chat-log">
              {chatMessages.map((message, index) => (
                <div className={`chat-message ${message.role}`} key={`${message.created_at}-${index}`}>
                  <strong>{message.role === "human" ? "You" : "AgentFlow"}</strong>
                  <span>{message.content}</span>
                  <small>{message.stage}</small>
                </div>
              ))}
            </div>
            <form className="chat-form" onSubmit={sendChatMessage}>
              <input
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
                placeholder={`Tag ${activeStage.agent}`}
              />
              <button className="icon-button selected" title="Send message">
                <Send size={17} />
              </button>
            </form>
          </section>

          <section className="panel files-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Runnable build</p>
                <h2>Generated FastAPI files</h2>
              </div>
              <div className="file-actions">
                <button className="primary-button" onClick={generateRunnableFiles}>
                  <Code2 size={18} />
                  Generate files
                </button>
                <button className="icon-button" onClick={copySelectedFile} title="Copy selected file">
                  <Copy size={18} />
                </button>
              </div>
            </div>
            <div className="file-workspace">
              <div className="file-list">
                {generatedFiles.map((file) => (
                  <button
                    className={file.path === selectedFile?.path ? "active" : ""}
                    key={file.path}
                    onClick={() => setSelectedFilePath(file.path)}
                  >
                    {file.path}
                  </button>
                ))}
              </div>
              <pre className="code-viewer">
                <code>{selectedFile?.content || "Click Generate files to create a runnable FastAPI starter app."}</code>
              </pre>
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="metric">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Artifact({ artifact }) {
  return (
    <div className="artifact">
      <div className="quality-score">
        <span>Quality score</span>
        <strong>{artifact.score}</strong>
      </div>
      <div className="output-list">
        {flattenArtifact(artifact).map((item) => (
          <div className="output-line" key={item.field}>
            <Play size={14} />
            <span>
              <strong>{formatField(item.field)}:</strong> {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SchemaCard({ artifactKey, schema }) {
  return (
    <div className="schema-card">
      <div className="schema-title">
        <FileJson size={20} />
        <span>{artifactKey}</span>
      </div>
      <div className="output-list">
        {schema.fields.map((field) => (
          <div className="output-line" key={field}>
            <ChevronRight size={16} />
            <span>{field}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatField(value) {
  return value
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

createRoot(document.getElementById("root")).render(<App />);
