async function askQuestion() {
  const question = document.getElementById("question").value;

  const res = await fetch(`${API}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const data = await res.json();
  const answer = data.answer;

  // ===== RISK BADGE =====
  const badge = document.getElementById("riskBadge");
  badge.innerText = answer.risk_level;

  badge.className = "badge"; // reset

  if (answer.risk_level === "HIGH") badge.classList.add("high");
  else if (answer.risk_level === "MEDIUM") badge.classList.add("medium");
  else badge.classList.add("low");

  // ===== CONFIDENCE =====
  const confidencePercent = answer.confidence * 100;

  document.getElementById("confidenceText").innerText =
    "Confidence: " + confidencePercent.toFixed(0) + "%";

  document.getElementById("confidenceFill").style.width =
    confidencePercent + "%";

  // ===== MISSING CLAUSES =====
  const missingList = document.getElementById("missing");
  missingList.innerHTML = "";

  answer.missing_clauses.forEach(c => {
    const li = document.createElement("li");
    li.innerText = c;
    missingList.appendChild(li);
  });

  // ===== SUSPICIOUS TERMS =====
  const suspiciousList = document.getElementById("suspicious");
  suspiciousList.innerHTML = "";

  answer.suspicious_terms.forEach(s => {
    const li = document.createElement("li");
    li.innerText = s;
    suspiciousList.appendChild(li);
  });

  // ===== EXPLANATION =====
  const explanationList = document.getElementById("explanations");
  explanationList.innerHTML = "";

  answer.explanation.forEach(e => {
    const li = document.createElement("li");
    li.innerText = e;
    explanationList.appendChild(li);
  });
}