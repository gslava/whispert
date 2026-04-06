import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parents[1]
WHISPER_BIN = BASE_DIR / "build" / "bin" / "whisper-cli"
MODELS = {
    "small": BASE_DIR / "models" / "ggml-small.bin",
    "medium": BASE_DIR / "models" / "ggml-medium.bin",
    "large-v3": BASE_DIR / "models" / "ggml-large-v3.bin",
    "large-v3-turbo": BASE_DIR / "models" / "ggml-large-v3-turbo.bin",
}

LANG_CHOICES = [
    ("auto", "Auto-detect"),
    ("en", "English"),
    ("uk", "Ukrainian"),
    ("pl", "Polish"),
    ("de", "German"),
    ("fr", "French"),
    ("es", "Spanish"),
]

LANG_SET = {code for code, _ in LANG_CHOICES}

app = Flask(__name__)


def validate_environment(model_key: str, audio_path: Path):
    errors = []

    if not WHISPER_BIN.exists():
        errors.append(
            "whisper-cli binary not found. Build the project with 'cmake --build build -j' first."
        )

    model_path = MODELS.get(model_key)
    if not model_path or not model_path.exists():
        errors.append(
            f"Model '{model_key}' is not available. Run the download script so that {model_path} exists."
        )

    if not audio_path.exists():
        errors.append(f"Audio file '{audio_path}' not found.")

    if audio_path.exists() and audio_path.is_dir():
        errors.append("Audio path points to a directory. Provide a file path instead.")

    return errors, model_path


@app.route("/")
def index():
    return render_template("index.html", models=MODELS, languages=LANG_CHOICES)


@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json(force=True)
    input_path = Path(data.get("path", "")).expanduser()
    model_key = data.get("model", "small")
    language = (data.get("language", "auto") or "auto").strip()

    if language not in LANG_SET:
        return jsonify({"ok": False, "error": f"Unsupported language code: {language}"}), 400

    errors, model_path = validate_environment(model_key, input_path)
    if errors:
        return jsonify({"ok": False, "error": "\n".join(errors)}), 400

    try:
        with tempfile.TemporaryDirectory(prefix="whisper-ui-") as tmpdir:
            tmp_wav = Path(tmpdir) / "input.wav"

            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ar",
                "16000",
                "-ac",
                "1",
                str(tmp_wav),
            ]
            ffmpeg_proc = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
            )
            if ffmpeg_proc.returncode != 0:
                return (
                    jsonify({
                        "ok": False,
                        "error": "ffmpeg conversion failed:\n" + ffmpeg_proc.stderr.strip(),
                    }),
                    400,
                )

            transcribe_cmd = [
                str(WHISPER_BIN),
                "-m",
                str(model_path),
                "-f",
                str(tmp_wav),
                "--language",
                language,
                "-np",
                "-nt",
            ]
            whisper_proc = subprocess.run(
                transcribe_cmd,
                capture_output=True,
                text=True,
            )
            if whisper_proc.returncode != 0:
                return (
                    jsonify({
                        "ok": False,
                        "error": "whisper-cli failed:\n" + whisper_proc.stderr.strip(),
                    }),
                    500,
                )

    except FileNotFoundError as exc:
        return (
            jsonify({
                "ok": False,
                "error": f"Required executable not found: {exc}",
            }),
            500,
        )
    except Exception as exc:  # pragma: no cover
        return (
            jsonify({
                "ok": False,
                "error": f"Unexpected error: {exc}",
            }),
            500,
        )

    transcript = whisper_proc.stdout.strip()
    if not transcript:
        transcript = "No transcript returned."

    return jsonify({"ok": True, "transcript": transcript})


if __name__ == "__main__":
    app.run(debug=True)
