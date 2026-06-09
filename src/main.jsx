import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  Check,
  ChevronRight,
  ClipboardCheck,
  Code2,
  Database,
  FileText,
  GitBranch,
  LayoutDashboard,
  Play,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  TestTube2,
  UserCheck,
} from "lucide-react";
import "./styles.css";

const stages = [
  {
    id: "intake",
    label: "Idea Intake",
    agent: "PM Agent",
    icon: FileText,
    decision: "Answer questions",
  },
  {
    id: "prd",
    label: "PRD",
    agent: "Product Manager",
    icon: ClipboardCheck,
    decision: "Approve scope",
  },
  {
    id: "architecture",
    label: "Architecture",
    agent: "Architect Agent",
    icon: Database,
    decision: "Approve design",
  },
  {
    id: "backend",
    label: "Backend Code",
    agent: "Backend Agent",
    icon: Code2,
    decision: "Review files",
  },
  {
    id: "qa",
    label: "QA Plan",
    agent: "QA Agent",
    icon: TestTube2,
    decision: "Approve tests",
  },
  {
    id: "review",
    label: "Review",
    agent: "Reviewer Agent",
    icon: ShieldCheck,
    decision: "Request changes",
  },
];

const demoIdea =
  "Build an appointment booking system for a dental clinic with patients, dentists, availability slots, reminders, and admin approval.";

const questionBank = [
  "Who can create appointments: patients only, staff only, or both?",
  "Should dentists define availability manually or sync it from a calendar?",
  "Do appointments need payment before confirmation?",
  "What reminder channels are required: email, SMS, or both?",
  "Can admins override booking conflicts in emergencies?",
];

const artifacts = {
  prd: {
    title: "Generated PRD",
    score: 91,
    body: [
      "Goal: let patients request dental appointments while admins manage dentist availability and booking approvals.",
      "Primary users: patients, clinic admins, dentists.",
      "Core user stories: book appointment, cancel appointment, manage availability, review pending bookings, send reminders.",
      "Acceptance criteria: prevent double-booking, validate patient contact info, show available time slots, record approval history.",
    ],
  },
  architecture: {
    title: "Architecture Output",
    score: 88,
    body: [
      "Tables: users, patients, dentists, availability_slots, appointments, reminders, audit_events.",
      "API routes: POST /appointments, GET /availability, PATCH /appointments/:id/status, POST /reminders/test.",
      "Services: scheduling validator, reminder dispatcher, admin approval workflow, audit logger.",
      "Approval gate: human reviews schema and route contract before code generation.",
    ],
  },
  backend: {
    title: "Backend Code Plan",
    score: 84,
    body: [
      "FastAPI routers for appointments, availability, auth placeholder, and admin review.",
      "SQLAlchemy models with appointment status enum: pending, approved, cancelled, completed.",
      "Validation checks for duplicate appointments, missing patient details, unavailable slots, and past dates.",
      "Generated files preview: app/main.py, app/models.py, app/routes/appointments.py, app/services/scheduling.py.",
    ],
  },
  qa: {
    title: "QA Test Cases",
    score: 89,
    body: [
      "Test booking succeeds when a dentist has an open slot.",
      "Test booking fails when another appointment already owns that slot.",
      "Test invalid phone and email inputs return validation errors.",
      "Manual QA: create patient, request booking, approve as admin, confirm reminder event is logged.",
    ],
  },
  review: {
    title: "Reviewer Report",
    score: 82,
    body: [
      "Strength: clear approval gates and practical API boundaries.",
      "Risk: auth is still a placeholder; do not expose admin actions without role checks.",
      "Risk: reminders need retry handling and delivery status tracking.",
      "Recommendation: add rate limits to appointment creation before public demo.",
    ],
  },
};

function App() {
  const [idea, setIdea] = useState(demoIdea);
  const [activeStage, setActiveStage] = useState("intake");
  const [approved, setApproved] = useState(["intake"]);
  const [answers, setAnswers] = useState({
    0: "Both patients and staff can create appointments.",
    1: "Admins define availability manually for the MVP.",
    2: "No payment in MVP.",
    3: "Email reminders first.",
    4: "Admins can override conflicts with an audit reason.",
  });

  const activeIndex = stages.findIndex((stage) => stage.id === activeStage);
  const progress = Math.round(((approved.length - 1) / (stages.length - 1)) * 100);

  const currentArtifact = useMemo(() => {
    if (activeStage === "intake") return null;
    return artifacts[activeStage];
  }, [activeStage]);

  function approveCurrentStage() {
    const current = stages[activeIndex];
    const next = stages[activeIndex + 1];
    setApproved((items) =>
      items.includes(current.id) ? items : [...items, current.id]
    );
    if (next) {
      setApproved((items) => (items.includes(next.id) ? items : [...items, next.id]));
      setActiveStage(next.id);
    }
  }

  function resetDemo() {
    setIdea(demoIdea);
    setActiveStage("intake");
    setApproved(["intake"]);
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
            const isActive = stage.id === activeStage;
            const isApproved = approved.includes(stage.id);
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
            <p className="eyebrow">MVP build</p>
            <h1>Dental clinic booking workflow</h1>
          </div>
          <div className="topbar-actions">
            <button className="icon-button" onClick={resetDemo} title="Reset demo">
              <RefreshCcw size={18} />
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
          <Metric icon={Sparkles} label="Artifacts" value="PRD/API/QA" />
          <Metric icon={AlertTriangle} label="Open risks" value="2" />
        </section>

        <div className="content-grid">
          <section className="panel intake-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Product owner input</p>
                <h2>Idea and clarifying answers</h2>
              </div>
              <span className="status-pill">Editable</span>
            </div>
            <label>
              Product idea
              <textarea value={idea} onChange={(event) => setIdea(event.target.value)} />
            </label>
            <div className="questions">
              {questionBank.map((question, index) => (
                <label key={question}>
                  {question}
                  <input
                    value={answers[index] || ""}
                    onChange={(event) =>
                      setAnswers((current) => ({
                        ...current,
                        [index]: event.target.value,
                      }))
                    }
                  />
                </label>
              ))}
            </div>
          </section>

          <section className="panel artifact-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">
                  {stages[activeIndex].agent} output
                </p>
                <h2>{currentArtifact ? currentArtifact.title : "Clarifying Questions"}</h2>
              </div>
              <span className="status-pill approved">
                {approved.includes(activeStage) ? "Ready" : "Pending"}
              </span>
            </div>

            {currentArtifact ? (
              <Artifact artifact={currentArtifact} />
            ) : (
              <div className="question-preview">
                {questionBank.map((question) => (
                  <div className="output-line" key={question}>
                    <ChevronRight size={16} />
                    <span>{question}</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        <section className="timeline">
          {stages.map((stage) => {
            const Icon = stage.icon;
            const isActive = stage.id === activeStage;
            const isApproved = approved.includes(stage.id);
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
        {artifact.body.map((item) => (
          <div className="output-line" key={item}>
            <Play size={14} />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
