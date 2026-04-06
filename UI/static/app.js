const form = document.getElementById('transcribe-form');
const transcriptArea = document.getElementById('transcript');
const statusLine = document.getElementById('status');

function setStatus(message, variant = '') {
  statusLine.textContent = message;
  statusLine.className = `status-line ${variant}`.trim();
}

async function transcribe(event) {
  event.preventDefault();
  const pathInput = document.getElementById('audio-path');
  const modelSelect = document.getElementById('model-select');
const languageSelect = document.getElementById('language-select');

  const payload = {
    path: pathInput.value.trim(),
    model: modelSelect.value,
    language: languageSelect.value,
  };

  if (!payload.path) {
    setStatus('Please enter an audio path.', 'error');
    return;
  }

  transcriptArea.value = '';
  setStatus('⏳ Transcribing... hold tight.');

  try {
    const response = await fetch('/transcribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || !data.ok) {
      const message = (data && data.error) ? data.error : 'Transcription failed.';
      setStatus(message, 'error');
      return;
    }

    transcriptArea.value = data.transcript;
    setStatus('✔️ Done.', 'success');
  } catch (error) {
    setStatus(`Request failed: ${error}`, 'error');
  }
}

form.addEventListener('submit', transcribe);
