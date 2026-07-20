"use strict";

const state = {
  conversationTurns: [],
  urgentLock: false
};

const safeProfile = {
  schema_version: "1.0.0",
  patient_reference: "PATIENT_0044",
  journey_phase: "BASELINE_ASSESSMENT",
  clinical_supervision: true,
  baseline: {
    age_band: "40_49",
    sex_recorded_for_clinical_context: "NOT_RECORDED",
    height_cm: null,
    weight_kg: null,
    goals: [
      "Prepare for a clinician-led baseline discussion",
      "Understand monitoring, safety and uncertainty"
    ]
  },
  monitoring_inputs: {
    last_clinical_review_date: null,
    data_completeness: "PARTIAL_FOR_DISCUSSION",
    known_conditions: [],
    current_medicines_discussed_with_clinician: false
  },
  symptom_flags: ["NONE"],
  consent: {
    pseudonymised_processing_confirmed: true,
    educational_use_acknowledged: true
  }
};

function byId(id) {
  return document.getElementById(id);
}

function clearNode(node) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

function textElement(tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = String(text);
  if (className) {
    element.className = className;
  }
  return element;
}

function listElement(values) {
  const list = document.createElement("ul");
  const items = Array.isArray(values) && values.length ? values : ["None recorded"];
  items.forEach((value) => {
    const text = typeof value === "object" ? JSON.stringify(value) : String(value);
    list.appendChild(textElement("li", text));
  });
  return list;
}

async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    cache: "no-store",
    body: JSON.stringify(payload)
  });
  const value = await response.json();
  if (!response.ok || value.valid !== true) {
    throw new Error(value.error || "Controlled request failed");
  }
  return value;
}

function setMessage(node, text, kind) {
  node.textContent = text;
  node.className = "message" + (kind ? " " + kind : "");
}

function renderReport(report) {
  const output = byId("reportOutput");
  clearNode(output);
  output.hidden = false;

  const summary = document.createElement("section");
  summary.appendChild(textElement("h3", "Report control"));
  const badge = textElement("span", report.report_state, "state-badge");
  if (report.report_state === "URGENT_CLINICAL_ROUTING") {
    badge.classList.add("urgent");
  }
  summary.appendChild(badge);
  summary.appendChild(textElement("p", "Report ID: " + report.report_id));
  summary.appendChild(textElement("p", "Patient reference: " + report.patient_reference));
  summary.appendChild(textElement("p", "Journey phase: " + report.journey_phase));
  output.appendChild(summary);

  const safety = document.createElement("section");
  safety.appendChild(textElement("h3", "Safety routing"));
  safety.appendChild(textElement("p", report.safety.routing || "Not recorded"));
  safety.appendChild(listElement(report.safety.flags));
  output.appendChild(safety);

  const prompts = document.createElement("section");
  prompts.appendChild(textElement("h3", "Clinician discussion prompts"));
  prompts.appendChild(listElement(report.clinician_discussion_prompts));
  output.appendChild(prompts);

  const sources = document.createElement("section");
  sources.appendChild(textElement("h3", "Source provenance"));
  sources.appendChild(listElement((report.sources || []).map((source) => source.repository_path)));
  output.appendChild(sources);
}

function renderConversation(conversation) {
  const output = byId("conversationOutput");
  clearNode(output);
  (conversation.exchanges || []).forEach((exchange) => {
    const item = document.createElement("li");
    item.className = "exchange";
    if (exchange.response_state === "URGENT_CLINICAL_ROUTING") {
      item.classList.add("urgent");
    }
    if (exchange.response_state.indexOf("REFUSED") >= 0 || exchange.response_state.indexOf("REJECTED") >= 0) {
      item.classList.add("refused");
    }
    item.appendChild(textElement("p", "Turn " + exchange.turn_number + " | " + exchange.response_state, "state-badge"));
    item.appendChild(textElement("p", exchange.answer));
    item.appendChild(textElement("p", "Sources: " + (exchange.sources || []).map((source) => source.repository_path).join("; "), "source-list"));
    output.appendChild(item);
  });
  state.urgentLock = conversation.urgent_lock === true;
  byId("askQuestion").disabled = state.urgentLock;
  if (state.urgentLock) {
    setMessage(byId("conversationMessage"), "Urgent routing is locked for this session. Start a new session only after seeking immediate clinical help.", "error");
  }
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((tab) => {
      const active = tab === button;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    });
    document.querySelectorAll(".panel").forEach((panel) => {
      const active = panel.id === button.dataset.panel;
      panel.classList.toggle("active", active);
      panel.hidden = !active;
    });
  });
});

byId("loadProfileExample").addEventListener("click", () => {
  byId("profileInput").value = JSON.stringify(safeProfile, null, 2);
  setMessage(byId("reportMessage"), "Safe pseudonymous example loaded.", "success");
});

byId("clearReport").addEventListener("click", () => {
  byId("profileInput").value = "";
  byId("reportOutput").hidden = true;
  clearNode(byId("reportOutput"));
  setMessage(byId("reportMessage"), "");
});

byId("generateReport").addEventListener("click", async () => {
  const message = byId("reportMessage");
  setMessage(message, "Generating through the controlled Build 0043 engine...");
  try {
    const profile = JSON.parse(byId("profileInput").value);
    const result = await postJson("/api/report", {profile});
    renderReport(result.report);
    setMessage(message, "Report generated for clinician discussion.", "success");
  } catch (error) {
    setMessage(message, error.message, "error");
  }
});

byId("askQuestion").addEventListener("click", async () => {
  const message = byId("conversationMessage");
  if (state.urgentLock) {
    setMessage(message, "This session is locked in urgent clinical routing.", "error");
    return;
  }
  const queryText = byId("questionInput").value.trim();
  if (queryText.length < 3) {
    setMessage(message, "Enter a question of at least three characters.", "error");
    return;
  }
  state.conversationTurns.push({
    query_text: queryText,
    query_mode: byId("queryMode").value,
    personalised_medical_request: byId("personalisedRequest").checked
  });
  const session = {
    schema_version: "1.0.0",
    session_reference: byId("sessionReference").value.trim(),
    audience: "PATIENT_DISCUSSION_SUPPORT",
    patient_reference: byId("patientReference").value.trim(),
    turns: state.conversationTurns
  };
  setMessage(message, "Querying the installed evidence baseline...");
  try {
    const result = await postJson("/api/conversation", {session});
    renderConversation(result.conversation);
    setMessage(message, "Controlled response completed.", "success");
  } catch (error) {
    state.conversationTurns.pop();
    setMessage(message, error.message, "error");
  }
});

byId("resetConversation").addEventListener("click", () => {
  state.conversationTurns = [];
  state.urgentLock = false;
  clearNode(byId("conversationOutput"));
  byId("questionInput").value = "";
  byId("personalisedRequest").checked = false;
  byId("askQuestion").disabled = false;
  setMessage(byId("conversationMessage"), "Session reset. No conversation history was persisted.", "success");
});

async function healthCheck() {
  const status = byId("healthStatus");
  try {
    const response = await fetch("/api/health", {cache: "no-store"});
    const value = await response.json();
    if (!response.ok || value.status !== "ok") {
      throw new Error("Local service unavailable");
    }
    status.textContent = "Local service: ready";
    status.classList.add("ok");
  } catch (error) {
    status.textContent = "Local service: unavailable";
    status.classList.add("fail");
  }
}

byId("profileInput").value = JSON.stringify(safeProfile, null, 2);
healthCheck();
