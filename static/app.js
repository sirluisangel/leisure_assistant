async function analyze() {
  const text = document.getElementById('feeling').value.trim();
  if (!text) { alert('Escribe cómo te sientes.'); return; }

  const resp = await fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  const d = await resp.json();

  document.getElementById('emo').textContent = d.emotion;

  const confidencePercent = (d.confidence * 100).toFixed(1);
  document.getElementById('conf').textContent = confidencePercent + '%';

  // obtener contexto del historial
  const histResp = await fetch('/history');
  const hist = await histResp.json();
  const recent = hist.slice(-6).map(h => h.emocion).join(', ');

  // solicitar recomendación
  const recResp = await fetch('/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feeling_text: text, detected_emotion: d.emotion, history: recent })
  });
  const recData = await recResp.json();

  document.getElementById('rec').textContent = recData.recommendation;

  const outputSection = document.getElementById('output');
  outputSection.classList.remove('opacity-0', 'invisible');
  outputSection.classList.add('opacity-100', 'visible');

  showOutput();
  loadHistory();
}

async function loadHistory() {
  const resp = await fetch('/history');
  const data = await resp.json();
  const container = document.getElementById('history-list');
  const section = document.getElementById('history-section');

  if (!container) {
    console.error("No se encontró el contenedor history-list");
    return;
  }
  if (!section) {
    console.error("No se encontró el contenedor history-section");
    return;
  }

  container.innerHTML = '';

  if (!data || data.length === 0) {
    section.classList.add('hidden');
    return;
  }

  section.classList.remove('hidden');

  data.slice(-12).reverse().forEach(e => {
    const card = document.createElement('div');

    // Color dinámico por emoción
    let emotionColor = 'bg-gray-200 text-gray-800';
    const emo = e.emocion?.toLowerCase();
    if (emo.includes('feliz') || emo.includes('alegr')) emotionColor = 'bg-green-100 text-green-800';
    else if (emo.includes('triste')) emotionColor = 'bg-blue-100 text-blue-800';
    else if (emo.includes('enojo') || emo.includes('ira')) emotionColor = 'bg-red-100 text-red-800';
    else if (emo.includes('miedo') || emo.includes('ansiedad')) emotionColor = 'bg-yellow-100 text-yellow-800';

    const recText = e.recomendacion || 'Sin recomendación';
    const recHTML = recText.replace(/\n/g, '<br/>');

    card.className = 'p-4 bg-white rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition';
    card.innerHTML = `
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-gray-500">${new Date(e.fecha).toLocaleString()}</span>
        <span class="px-2 py-1 rounded-full text-xs font-medium ${emotionColor}">
          ${e.emocion}
        </span>
      </div>
      <p class="text-gray-700 mb-2">${e.texto}</p>
      <p class="text-sm text-gray-500">${recHTML}</p>
    `;

    container.appendChild(card);
  });
}


document.getElementById('analyze').addEventListener('click', analyze);
document.getElementById('clear').addEventListener('click', () => {
  document.getElementById('feeling').value = '';
});
window.addEventListener('load', loadHistory);

function abrirHistorial() {
  window.open('/static/history.html', '_blank');
}