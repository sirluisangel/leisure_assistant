async function analyze() {
  const text = document.getElementById('feeling').value.trim();
  if (!text) { alert('Escribe cómo te sientes.'); return; }
  const resp = await fetch('/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
  const d = await resp.json();
  document.getElementById('emo').textContent = d.emotion;
  document.getElementById('conf').textContent = d.confidence;
  // get history context
  const histResp = await fetch('/history');
  const hist = await histResp.json();
  const recent = hist.slice(-6).map(h => h.emocion).join(', ');
  // request recommendation
  const recResp = await fetch('/recommend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ feeling_text: text, detected_emotion: d.emotion, history: recent }) });
  const recData = await recResp.json();
  document.getElementById('rec').textContent = recData.recommendation;
  document.getElementById('output').classList.remove('hidden');
  loadHistory();
}

async function loadHistory() {
  const resp = await fetch('/history');
  const data = await resp.json();
  const container = document.getElementById('history-list');
  container.innerHTML = '';
  if (!data || data.length === 0) { container.textContent = 'Aún no hay historial.'; return; }
  data.slice(-12).reverse().forEach(e => {
    const div = document.createElement('div');
    div.className = 'history-entry';
    div.innerHTML = `<strong>${(new Date(e.fecha)).toLocaleString()}</strong> — <em>${e.emocion}</em><br/>${e.texto}<br/><small>${e.recomendacion}</small>`;
    container.appendChild(div);
  });
}

document.getElementById('analyze').addEventListener('click', analyze);
document.getElementById('clear').addEventListener('click', () => { document.getElementById('feeling').value = ''; });
window.addEventListener('load', loadHistory);