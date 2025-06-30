from faster_whisper import WhisperModel
import numpy as np
import soundfile as sf
import io


class SpeechProcessor:
    def __init__(self):
        self.model = WhisperModel("small", device="cpu", compute_type="int8")

    async def transcribe_stream(self, audio_stream: bytes) -> str:
        try:
            # Convert bytes to numpy array
            with io.BytesIO(audio_stream) as audio_buffer:
                try:
                    audio_array, sample_rate = sf.read(
                        audio_buffer,
                        format='RAW',
                        samplerate=16000,
                        channels=1,
                        subtype='PCM_16'
                    )

                    # Validate audio
                    if len(audio_array) == 0:
                        return "[ERROR: Empty audio]"

                    # Normalize audio
                    audio_array = audio_array.astype(np.float32) / 32768.0

                    # Transcribe
                    segments, _ = self.model.transcribe(audio_array)
                    full_text = " ".join(segment.text for segment in segments)

                    print(f"Raw transcription: {full_text}")  # Debug log
                    return full_text

                except sf.LibsndfileError as e:
                    print(f"Audio decode error: {str(e)}")
                    return "[AUDIO DECODE ERROR]"

        except Exception as e:
            print(f"Transcription failed: {str(e)}")
            return "[TRANSCRIPTION ERROR]"