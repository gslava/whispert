# Whisper Terminal UI

A minimal Flask-based interface styled like an old-school terminal. It wraps the `whisper.cpp` CLI so you can paste an audio file path, choose one of the locally downloaded models, and read the transcript in the browser.

## Quickstart
1. Create a virtual environment (optional but recommended):
   ```bash
   cd UI
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the server from the repo root so the relative paths resolve:
   ```bash
   FLASK_APP=UI.app FLASK_ENV=development flask run
   ```
   The UI will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Usage Notes
- `whisper.cpp` must already be built (`build/bin/whisper-cli` must exist).
- The following models are pre-wired in the dropdown: `ggml-small.bin`, `ggml-medium.bin`, `ggml-large-v3.bin`, `ggml-large-v3-turbo.bin`.
- `ffmpeg` is used server-side to convert any supported input format into mono 16 kHz WAV before transcription.
- Transcripts render in the text area with classic terminal colors; field focus states glow green to mimic iTerm aesthetics.

## Customisation
- Modify `MODELS` in `UI/app.py` to add or remove local models.
- Update the CSS in `UI/static/style.css` to tweak the theme.
