import speech_recognition as sr
from faster_whisper import WhisperModel


class SpeechProcessor:
    def __init__(self):
        self.model = WhisperModel("small", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()

    def transcribe_microphone(self):
        """Capture audio from microphone and transcribe"""
        with sr.Microphone(device_index=0) as source:
            print("Speak now...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5)

                with open("temp_audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())

                segments, _ = self.model.transcribe("temp_audio.wav")
                return " ".join(segment.text for segment in segments)

            except sr.WaitTimeoutError:
                raise Exception("No speech detected. Try again.")
            except Exception as e:
                raise Exception(f"Audio processing error: {str(e)}")