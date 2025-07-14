from faster_whisper import WhisperModel
import numpy as np
import soundfile as sf
import io
import subprocess
import tempfile
import os
import structlog

logger = structlog.get_logger()

class SpeechProcessor:
    def __init__(self):
        # Use a larger model for better accuracy
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """Transcribe a complete audio file"""
        try:
            logger.info("=== AUDIO PROCESSING DEBUG ===",
                       input_audio_size=len(audio_data),
                       audio_format=audio_format)
            
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
                
                logger.info("✅ Audio loaded", 
                           samples=len(audio_array),
                           sample_rate=sample_rate,
                           duration_seconds=len(audio_array) / sample_rate)
                
                # Check for audio anomalies
                logger.info("Audio statistics",
                           min_val=np.min(audio_array),
                           max_val=np.max(audio_array),
                           mean_val=np.mean(audio_array),
                           std_val=np.std(audio_array),
                           non_zero_samples=np.count_nonzero(audio_array),
                           total_samples=len(audio_array))
                
                # Check for silence at beginning/end
                silence_threshold = 0.01
                start_silence = np.count_nonzero(np.abs(audio_array[:int(sample_rate * 0.5)]) < silence_threshold)
                end_silence = np.count_nonzero(np.abs(audio_array[-int(sample_rate * 0.5):]) < silence_threshold)
                logger.info("Silence analysis",
                           start_silence_samples=start_silence,
                           end_silence_samples=end_silence)
                
                # Normalize audio
                if np.max(np.abs(audio_array)) > 0:
                    audio_array = audio_array / np.max(np.abs(audio_array))
                
                # Transcribe
                logger.info("🎤 Starting transcription...")
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
                    logger.info(f"Segment {i+1}", 
                               text=segment_text,
                               start_time=segment.start,
                               end_time=segment.end)
                
                full_text = " ".join(segment_texts)
                
                logger.info("=== TRANSCRIPTION RESULT ===",
                           raw_transcription=full_text,
                           number_of_segments=len(segment_texts))
                
                return full_text
                
        except Exception as e:
            logger.error("❌ Transcription failed", error=str(e))
            import traceback
            traceback.print_exc()
            return "[TRANSCRIPTION ERROR]"
    
    def _convert_to_wav(self, audio_data: bytes, audio_format: str) -> bytes:
        """Convert audio to WAV format using ffmpeg"""
        try:
            logger.info("🔄 Converting to WAV", audio_format=audio_format)
            
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
            
            logger.info("Running ffmpeg command", command=' '.join(cmd))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error("❌ FFmpeg error", stderr=result.stderr)
                return None
            
            logger.info("✅ FFmpeg conversion successful")
            
            with open(output_path, 'rb') as f:
                wav_data = f.read()
            
            logger.info("📦 WAV file size", size_bytes=len(wav_data))
            
            os.unlink(input_path)
            os.unlink(output_path)
            
            return wav_data
            
        except Exception as e:
            logger.error("❌ Audio conversion error", error=str(e))
            # Clean up on error
            try:
                if 'input_path' in locals():
                    os.unlink(input_path)
                if 'output_path' in locals():
                    os.unlink(output_path)
            except:
                pass
            return None 