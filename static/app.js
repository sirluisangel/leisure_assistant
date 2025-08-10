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

  if (historyData.length === 0) {
    document.getElementById("history").classList.add("hidden");
    return;
  } else {
    document.getElementById("history").classList.remove("hidden");
  }

  historyData.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = `
      bg-white
      rounded-xl
      shadow-lg
      border
      border-gray-200
      p-5
      flex
      flex-col
      md:flex-row
      md:items-center
      gap-4
      hover:shadow-xl
      transition-shadow
      duration-300
      relative
    `;

    const emojiMap = {
      Feliz: "😊",
      Triste: "😢",
      Ansioso: "😰",
      Motivado: "💪",
      Frustrado: "😤",
    };
    const emoji = emojiMap[item.emotion] || "❓";

    let confColorClass = "text-red-600";
    if (item.confidence >= 0.8) confColorClass = "text-green-600";
    else if (item.confidence >= 0.7) confColorClass = "text-yellow-600";

    card.innerHTML = `
      <div class="flex items-center gap-5 flex-shrink-0">
        <div class="text-4xl select-none">${emoji}</div>
        <div>
          <h4 class="text-purple-700 font-extrabold text-xl">${item.emotion}</h4>
          <p class="text-gray-400 text-sm">${item.date}</p>
        </div>
      </div>

      <div class="flex-1 flex flex-col gap-2">
        <p class="text-gray-700 italic line-clamp-4">${item.text}</p>
        <p class="${confColorClass} font-semibold">Confianza: ${(item.confidence * 100).toFixed(0)}%</p>

        <details class="bg-purple-50 border border-purple-200 rounded-md p-3 cursor-pointer select-none">
          <summary class="font-semibold">Recomendación</summary>
          <p class="mt-2 text-gray-800">${item.recommendation}</p>
        </details>
      </div>

      <button
        data-index="${index}"
        title="Eliminar entrada"
        class="absolute top-3 right-3 text-gray-400 hover:text-red-600 text-3xl font-bold transition rounded-full p-1 select-none focus:outline-none focus:ring-2 focus:ring-red-400"
      >
        &times;
      </button>
    `;

    historyList.appendChild(card);
  });

  // Añadir funcionalidad a botones eliminar
  document.querySelectorAll("button[data-index]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = e.target.getAttribute("data-index");
      historyData.splice(idx, 1);
      renderHistory();
    });
  });
}

// Simulación de análisis (puedes reemplazarlo con IA real)
function analyzeFeeling(text) {
  const emotions = ["Feliz", "Triste", "Ansioso", "Motivado", "Frustrado"];
  const emotion = emotions[Math.floor(Math.random() * emotions.length)];
  const confidence = Math.random() * (0.9 - 0.6) + 0.6;
  const recommendation = `Te recomiendo hacer una breve pausa y practicar respiración consciente para manejar la emoción: ${emotion}.`;

  return { emotion, confidence, recommendation };
}

function setConfidenceColor(confidence) {
  confSpan.classList.remove("text-green-600", "text-yellow-600", "text-red-600");
  if (confidence >= 0.8) {
    confSpan.classList.add("text-green-600");
  } else if (confidence >= 0.7) {
    confSpan.classList.add("text-yellow-600");
  } else {
    confSpan.classList.add("text-red-600");
  }
}

function showOutput() {
  outputBox.classList.remove("invisible", "opacity-0");
  outputBox.classList.add("opacity-100");
}

function hideOutput() {
  outputBox.classList.add("opacity-0");
  outputBox.classList.remove("opacity-100");
  setTimeout(() => {
    outputBox.classList.add("invisible");
  }, 300);
}

analyzeBtn.addEventListener("click", () => {
  const text = feelingInput.value.trim();
  if (!text) {
    feelingInput.classList.add("border-red-500", "ring-1", "ring-red-500");
    feelingInput.focus();
    return alert("Por favor escribe cómo te sientes.");
  } else {
    feelingInput.classList.remove("border-red-500", "ring-1", "ring-red-500");
  }

  const { emotion, confidence, recommendation } = analyzeFeeling(text);

  emoSpan.textContent = emotion;
  confSpan.textContent = (confidence * 100).toFixed(0) + "%";
  setConfidenceColor(confidence);
  recDiv.textContent = recommendation;

  showOutput();

  addToHistory(emotion, confidence, recommendation, text);
});

clearBtn.addEventListener("click", () => {
  feelingInput.value = "";
  hideOutput();
});