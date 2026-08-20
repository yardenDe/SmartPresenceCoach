import whisper


class WhisperTranscriber:
    def __init__(self, model_name: str = "turbo"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, file_path: str) -> str:
        result = self.model.transcribe(file_path)
        return result["text"]