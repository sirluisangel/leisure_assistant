// Función para manejar el análisis
async function analyze() {
  const text = document.getElementById('feeling').value.trim();
  if (!text) { 
    alert('Escribe cómo te sientes.'); 
    return; 
  }

  // Desactivar el botón de analizar mientras procesamos la solicitud
  toggleButtons(true);

  try {
    // Llamar al backend para obtener la emoción
    const resp = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const d = await resp.json();

    // Verificar si hubo un error en la predicción
    if (d.error) {
      throw new Error(d.error);
    }

    // Mostrar emoción y confianza en la UI
    document.getElementById('emo').textContent = d.emotion;
    const confidencePercent = (d.confidence * 100).toFixed(1);
    document.getElementById('conf').textContent = `${confidencePercent}%`;

    // Obtener contexto del historial
    const histResp = await fetch('/history');
    const hist = await histResp.json();
    const recent = hist.slice(-6).map(h => h.emocion).join(', ');

    // Solicitar recomendación
    const recResp = await fetch('/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feeling_text: text, detected_emotion: d.emotion, history: recent })
    });
    const recData = await recResp.json();

    // Mostrar recomendación generada
    document.getElementById('rec').textContent = recData.recommendation || 'Sin recomendación';

    // Mostrar sección de resultados
    toggleOutputVisibility(true);

    // Cargar historial actualizado
    loadHistory();

  } catch (error) {
    console.error("Error:", error);
    alert('Hubo un problema al procesar tu solicitud. Intenta de nuevo más tarde.');
  }

  // Reactivar el botón de analizar
  toggleButtons(false);
}

// Función para mostrar/ocultar los resultados
function toggleOutputVisibility(isVisible) {
  const outputSection = document.getElementById('output');
  if (isVisible) {
    outputSection.classList.remove('opacity-0', 'invisible');
    outputSection.classList.add('opacity-100', 'visible');
  } else {
    outputSection.classList.add('opacity-0', 'invisible');
    outputSection.classList.remove('opacity-100', 'visible');
  }
}

// Función para deshabilitar/habilitar botones
function toggleButtons(disable) {
  document.getElementById('analyze').disabled = disable;
  document.getElementById('clear').disabled = disable;
}

// Función para cargar el historial de interacciones
async function loadHistory() {
  try {
    const resp = await fetch('/history');
    const data = await resp.json();
    const container = document.getElementById('history-list');
    const section = document.getElementById('history-section');

    if (!container || !section) {
      console.error("No se encontraron los elementos para el historial");
      return;
    }

    container.innerHTML = '';

    if (!data || data.length === 0) {
      section.classList.add('hidden');
      return;
    }

    section.classList.remove('hidden');
    data.slice(-12).reverse().forEach(e => {
      const card = createHistoryCard(e);
      container.appendChild(card);
    });
  } catch (error) {
    console.error('Error al cargar el historial:', error);
  }
}

// Función para crear una tarjeta de historial con color dinámico
function createHistoryCard(e) {
  const card = document.createElement('div');
  const emotionColor = getEmotionColor(e.emocion);

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

  return card;
}

// Función para determinar el color según la emoción
function getEmotionColor(emo) {
  const emotion = emo.toLowerCase();
  if (emotion.includes('feliz') || emotion.includes('alegr')) return 'bg-green-100 text-green-800';
  if (emotion.includes('triste')) return 'bg-blue-100 text-blue-800';
  if (emotion.includes('enojo') || emotion.includes('ira')) return 'bg-red-100 text-red-800';
  if (emotion.includes('miedo') || emotion.includes('ansiedad')) return 'bg-yellow-100 text-yellow-800';
  return 'bg-gray-200 text-gray-800';
}

// Evento para iniciar el análisis
document.getElementById('analyze').addEventListener('click', analyze);

// Evento para limpiar el área de texto
document.getElementById('clear').addEventListener('click', () => {
  document.getElementById('feeling').value = '';
  document.getElementById('emo').textContent = '';
  document.getElementById('conf').textContent = '';
  document.getElementById('rec').textContent = '';
  toggleOutputVisibility(false);
});

// Cargar el historial al cargar la página
window.addEventListener('load', loadHistory);

// Abrir el historial en una nueva ventana
function abrirHistorial() {
  window.open('/static/history.html', '_blank');
}