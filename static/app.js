const feelingInput = document.getElementById("feeling");
const analyzeBtn = document.getElementById("analyze");
const clearBtn = document.getElementById("clear");
const outputBox = document.getElementById("output");
const emoSpan = document.getElementById("emo");
const confSpan = document.getElementById("conf");
const recDiv = document.getElementById("rec");
const historyList = document.getElementById("history-list");

// Historial en memoria
let historyData = [];

function addToHistory(emotion, confidence, recommendation, text) {
  const date = new Date().toLocaleString();

  historyData.unshift({ emotion, confidence, recommendation, text, date });
  renderHistory();
}

function renderHistory() {
  historyList.innerHTML = "";

  historyData.forEach(item => {
    const card = document.createElement("div");
    card.className = "p-4 bg-purple-50 border border-purple-200 rounded-lg shadow-sm hover:shadow-md transition";

    card.innerHTML = `
      <div class="flex justify-between items-center mb-2">
        <span class="text-purple-700 font-semibold">${item.emotion}</span>
        <span class="text-sm text-gray-500">${item.date}</span>
      </div>
      <p class="text-sm text-gray-700 mb-2"><em>"${item.text}"</em></p>
      <p class="text-xs text-gray-500">Confianza: ${item.confidence}</p>
      <div class="mt-2 bg-white rounded p-2 text-gray-700 text-sm border border-gray-200">
        ${item.recommendation}
      </div>
    `;
    historyList.appendChild(card);
  });
}

// Simulación de análisis (puedes reemplazarlo con IA real)
function analyzeFeeling(text) {
  // Aquí iría tu lógica de IA
  const emotions = ["Feliz", "Triste", "Ansioso", "Motivado", "Frustrado"];
  const emotion = emotions[Math.floor(Math.random() * emotions.length)];
  const confidence = (Math.random() * (0.9 - 0.6) + 0.6).toFixed(2);
  const recommendation = `Te recomiendo hacer una breve pausa y practicar respiración consciente para manejar la emoción: ${emotion}.`;

  return { emotion, confidence, recommendation };
}

analyzeBtn.addEventListener("click", () => {
  const text = feelingInput.value.trim();
  if (!text) return alert("Por favor escribe cómo te sientes.");

  const { emotion, confidence, recommendation } = analyzeFeeling(text);

  emoSpan.textContent = emotion;
  confSpan.textContent = confidence;
  recDiv.textContent = recommendation;

  outputBox.classList.remove("hidden");

  addToHistory(emotion, confidence, recommendation, text);
});

clearBtn.addEventListener("click", () => {
  feelingInput.value = "";
  outputBox.classList.add("hidden");
});
