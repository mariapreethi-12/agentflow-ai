export const artifactSchemas = {
  clarifying_questions: {
    agent: "PM Agent",
    fields: ["questions", "assumptions", "decision_required"],
  },
  prd: {
    agent: "Product Manager Agent",
    fields: ["goal", "users", "user_stories", "acceptance_criteria", "scope_notes"],
  },
  architecture: {
    agent: "Architect Agent",
    fields: ["tables", "api_routes", "services", "approval_gate"],
  },
  backend_plan: {
    agent: "Backend Engineer Agent",
    fields: ["framework", "files", "validation_rules", "implementation_notes"],
  },
  qa_plan: {
    agent: "QA Agent",
    fields: ["unit_tests", "api_tests", "edge_cases", "manual_checklist"],
  },
  review_report: {
    agent: "Code Reviewer Agent",
    fields: ["score", "strengths", "risks", "recommendations"],
  },
};

export const demoQuestions = [
  "Who can create appointments: patients only, staff only, or both?",
  "Should dentists define availability manually or sync it from a calendar?",
  "Do appointments need payment before confirmation?",
  "What reminder channels are required: email, SMS, or both?",
  "Can admins override booking conflicts in emergencies?",
];

export const demoAnswers = {
  0: "Both patients and staff can create appointments.",
  1: "Admins define availability manually for the MVP.",
  2: "No payment in MVP.",
  3: "Email reminders first.",
  4: "Admins can override conflicts with an audit reason.",
};

export const demoIdea =
  "Build an appointment booking system for a dental clinic with patients, dentists, availability slots, reminders, and admin approval.";

export function createInitialProject() {
  const now = new Date().toISOString();

  return {
    id: crypto.randomUUID(),
    name: "Dental clinic booking workflow",
    idea: demoIdea,
    answers: demoAnswers,
    activeStage: "intake",
    approvals: {
      intake: {
        approved: true,
        approvedAt: now,
        note: "Demo project initialized.",
      },
    },
    artifacts: generateArtifacts(demoIdea, demoAnswers),
    createdAt: now,
    updatedAt: now,
  };
}

export function generateArtifacts(idea, answers) {
  const answerList = Object.values(answers).filter(Boolean);
  const reminderChoice = answerList.find((answer) =>
    answer.toLowerCase().includes("reminder")
  );
  const paymentChoice = answerList.find((answer) =>
    answer.toLowerCase().includes("payment")
  );

  return {
    clarifying_questions: {
      schema: "clarifying_questions",
      title: "Clarifying Questions",
      score: 94,
      generatedAt: new Date().toISOString(),
      data: {
        questions: demoQuestions,
        assumptions: [
          "The MVP focuses on one clinic location.",
          "Role-based access can start with patient and admin users.",
          "Dentist availability is managed inside AgentFlow's generated app.",
        ],
        decision_required: "Confirm who can book and how reminders should work.",
      },
    },
    prd: {
      schema: "prd",
      title: "Generated PRD",
      score: 91,
      generatedAt: new Date().toISOString(),
      data: {
        goal:
          "Let patients request dental appointments while admins manage dentist availability and booking approvals.",
        users: ["Patients", "Clinic admins", "Dentists"],
        user_stories: [
          "As a patient, I can request an appointment from available dentist slots.",
          "As an admin, I can approve, reject, or reschedule pending appointments.",
          "As a dentist, I can see my upcoming appointments and availability.",
        ],
        acceptance_criteria: [
          "The system prevents double-booking for the same dentist and time slot.",
          "Patients must provide valid contact details before requesting an appointment.",
          "Every approval or override is recorded in an audit trail.",
        ],
        scope_notes: [
          idea,
          reminderChoice || "Email reminders are included in the MVP.",
          paymentChoice || "Payments stay out of scope for the first build.",
        ],
      },
    },
    architecture: {
      schema: "architecture",
      title: "Architecture Output",
      score: 88,
      generatedAt: new Date().toISOString(),
      data: {
        tables: [
          "users",
          "patients",
          "dentists",
          "availability_slots",
          "appointments",
          "reminders",
          "audit_events",
        ],
        api_routes: [
          "POST /appointments",
          "GET /availability",
          "PATCH /appointments/:id/status",
          "POST /reminders/test",
        ],
        services: [
          "Scheduling validator",
          "Reminder dispatcher",
          "Admin approval workflow",
          "Audit logger",
        ],
        approval_gate:
          "Human reviews schema and route contract before code generation.",
      },
    },
    backend_plan: {
      schema: "backend_plan",
      title: "Backend Code Plan",
      score: 84,
      generatedAt: new Date().toISOString(),
      data: {
        framework: "FastAPI with SQLAlchemy and PostgreSQL",
        files: [
          "app/main.py",
          "app/models.py",
          "app/routes/appointments.py",
          "app/routes/availability.py",
          "app/services/scheduling.py",
        ],
        validation_rules: [
          "Reject duplicate appointments for the same dentist and slot.",
          "Reject appointments with missing patient contact details.",
          "Reject bookings for past dates or unavailable slots.",
        ],
        implementation_notes: [
          "Use an appointment status enum: pending, approved, cancelled, completed.",
          "Keep auth as a placeholder until the backend milestone.",
        ],
      },
    },
    qa_plan: {
      schema: "qa_plan",
      title: "QA Test Cases",
      score: 89,
      generatedAt: new Date().toISOString(),
      data: {
        unit_tests: [
          "Scheduling validator detects conflicts.",
          "Appointment status transitions follow approval rules.",
        ],
        api_tests: [
          "POST /appointments succeeds for an open slot.",
          "POST /appointments fails for duplicate slots.",
          "PATCH /appointments/:id/status requires admin role.",
        ],
        edge_cases: [
          "Invalid email or phone number.",
          "Appointment requested outside clinic hours.",
          "Admin override without audit reason.",
        ],
        manual_checklist: [
          "Create patient.",
          "Request booking.",
          "Approve as admin.",
          "Confirm reminder event is logged.",
        ],
      },
    },
    review_report: {
      schema: "review_report",
      title: "Reviewer Report",
      score: 82,
      generatedAt: new Date().toISOString(),
      data: {
        score: 82,
        strengths: [
          "Clear approval gates.",
          "Practical API boundaries.",
          "Good demo scenario for recruiters.",
        ],
        risks: [
          "Auth is still a placeholder.",
          "Reminder retry handling needs a real implementation.",
        ],
        recommendations: [
          "Add role checks before exposing admin actions.",
          "Add rate limits to appointment creation before a public demo.",
          "Track reminder delivery status.",
        ],
      },
    },
  };
}

export function flattenArtifact(artifact) {
  if (!artifact) return [];

  return Object.entries(artifact.data).map(([field, value]) => ({
    field,
    value: Array.isArray(value) ? value.join("; ") : String(value),
  }));
}
