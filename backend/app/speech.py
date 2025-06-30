from faster_whisper import WhisperModel
import numpy as np
import soundfile as sf
import io
import subprocess
import tempfile
import os


class SpeechProcessor:
    def __init__(self):
        # Use a larger model for better accuracy
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe a complete audio file"""
        try:
            print(f"=== AUDIO PROCESSING DEBUG ===")
            print(f"Input audio size: {len(audio_data)} bytes")
            print(f"Audio format: {audio_format}")
            
            # Convert audio to WAV format that Whisper can understand
            wav_data = self._convert_to_wav(audio_data, audio_format)
            
            if wav_data is None:
                return "[AUDIO CONVERSION ERROR]"
            
            # Load audio as numpy array
            with io.BytesIO(wav_data) as audio_buffer:
                audio_array, sample_rate = sf.read(audio_buffer, dtype=np.float32)
                
                # Ensure mono channel
                if len(audio_array.shape) > 1:
                    audio_array = audio_array[:, 0]
                
                print(f"✅ Audio loaded: {len(audio_array)} samples at {sample_rate}Hz")
                print(f"Audio duration: {len(audio_array) / sample_rate:.2f} seconds")
                
                # Check for audio anomalies
                print(f"Audio statistics:")
                print(f"  Min/Max: {np.min(audio_array):.4f} / {np.max(audio_array):.4f}")
                print(f"  Mean/Std: {np.mean(audio_array):.4f} / {np.std(audio_array):.4f}")
                print(f"  Non-zero samples: {np.count_nonzero(audio_array)} / {len(audio_array)}")
                
                # Check for silence at beginning/end
                silence_threshold = 0.01
                start_silence = np.count_nonzero(np.abs(audio_array[:int(sample_rate * 0.5)]) < silence_threshold)
                end_silence = np.count_nonzero(np.abs(audio_array[-int(sample_rate * 0.5):]) < silence_threshold)
                print(f"  Silent samples (first 0.5s): {start_silence}")
                print(f"  Silent samples (last 0.5s): {end_silence}")
                
                # Normalize audio
                if np.max(np.abs(audio_array)) > 0:
                    audio_array = audio_array / np.max(np.abs(audio_array))
                
                # Transcribe
                print("🎤 Starting transcription...")
                segments, _ = self.model.transcribe(
                    audio_array,
                    language="en",
                    task="transcribe",
                    beam_size=1,
                    best_of=1,
                    temperature=0.0,
                    condition_on_previous_text=False,
                    initial_prompt=None
                )
                
                segment_texts = []
                for i, segment in enumerate(segments):
                    segment_text = segment.text.strip()
                    segment_texts.append(segment_text)
                    print(f"  Segment {i+1}: '{segment_text}' (start: {segment.start:.2f}s, end: {segment.end:.2f}s)")
                
                full_text = " ".join(segment_texts)
                
                print(f"=== TRANSCRIPTION RESULT ===")
                print(f"Raw transcription: '{full_text}'")
                print(f"Number of segments: {len(segment_texts)}")
                print(f"================================")
                
                return full_text
                
        except Exception as e:
            print(f"❌ Transcription failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return "[TRANSCRIPTION ERROR]"
    
    def _convert_to_wav(self, audio_data: bytes, audio_format: str) -> bytes:
        """Convert audio to WAV format using ffmpeg"""
        try:
            print(f"🔄 Converting {audio_format} to WAV...")
            
            with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y', 
                output_path
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ FFmpeg error: {result.stderr}")
                return None
            
            print("✅ FFmpeg conversion successful")
            
            with open(output_path, 'rb') as f:
                wav_data = f.read()
            
            print(f"📦 WAV file size: {len(wav_data)} bytes")
            
            os.unlink(input_path)
            os.unlink(output_path)
            
            return wav_data
            
        except Exception as e:
            print(f"❌ Audio conversion error: {str(e)}")
            # Clean up on error
            try:
                if 'input_path' in locals():
                    os.unlink(input_path)
                if 'output_path' in locals():
                    os.unlink(output_path)
            except:
                pass
            return None