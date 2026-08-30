

class Transcriber:

    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def transcribe(self, wav_bytes: bytes):

        response = self.client.audio.transcriptions.create(
            file=("audio.wav", wav_bytes),
            model=self.model,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
        )

        return response

