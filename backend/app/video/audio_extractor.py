from pathlib import Path
import subprocess


class AudioExtractor:
    def __init__(self, video_path: str):
        self.video_path = Path(video_path)

    def extract(self, sample_rate: int = 16000, channels: int = 1) -> Path:
        audio_path = self.video_path.with_suffix(".wav")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", str(self.video_path),
                "-vn",
                "-ac", str(channels),
                "-ar", str(sample_rate),
                "-c:a", "pcm_s16le",
                str(audio_path),
            ],
            check=True,
        )

        return audio_path
