import re
import torch
from transformers import pipeline
from wiktionary_defs.fill_with_wikt import (
    json_dump_entries,
    get_entries,
    load_wiktextract,
)
from flask import Flask, request, send_from_directory


class TranscriptionProcessor:
    def __init__(self, wikt_path: str, model_name="vinai/PhoWhisper-medium"):
        print("Loading Wiktionary data...")
        self.wikt_df = load_wiktextract(wikt_path)
        print(f"Loading the transcriber model {model_name}...")
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        # self.sampling_rate = self.transcriber.feature_extractor.sampling_rate

    def get_wikt_entry(self, word: str) -> dict:
        found_entries = get_entries(self.wikt_df, word)
        if not found_entries.empty:
            json_str, short_str = json_dump_entries(found_entries, word=word)
        else:
            json_str, short_str = "", ""

        return {
            "json": json_str,
            "short": short_str,
        }

    def process_audio(
        self, audio_bytes: bytes, max_n_gram: int = 4
    ) -> tuple[str, dict]:
        # Assume the audio is in a correct format for ffmpeg to read
        # and has the correct sampling rate TODO: Convert this first? see if ffmpeg
        # can handle it.
        transcription: str = self.transcriber(audio_bytes)["text"]
        word_splits = re.sub(r"(^\W|\W$)", "", transcription).split()

        result_dict = {}
        for n in range(1, max_n_gram + 1):
            for j in range(len(word_splits)):
                word = " ".join(word_splits[j : j + n])
                if word in result_dict:
                    continue

                result = self.get_wikt_entry(word)
                result_dict[word] = result

        return transcription, {k: v for k, v in result_dict.items() if v["json"]}


if __name__ == "__main__":
    app = Flask(__name__)
    processor = TranscriptionProcessor(
        wikt_path="/mnt/SSDSHARED/VN/wikt/kaikki.org-dictionary-Vietnamese.jsonl",
        model_name="vinai/PhoWhisper-medium",
    )

    @app.route("/process_audio", methods=["POST"])
    def process_audio():
        if "audio" not in request.files:
            return "No audio file found", 400

        audio_file = request.files["audio"].read()

        if "max_n_gram" in request.form:
            max_n_gram = int(request.form["max_n_gram"])
        else:
            max_n_gram = 4

        transcription, result = processor.process_audio(audio_file, max_n_gram)
        print("Finished processing audio")
        print(transcription, result)

        return {"transcription": transcription, "result": result}

    @app.route("/")
    def serve_gui():
        return send_from_directory(
            "/home/ducha/Workspace/python/cloze-wikt-cards/asr-adder/client-gui",
            "gui.html",
        )

    app.run(debug=False)