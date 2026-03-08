import subprocess
import os

class TTSTools:
    """Tools for synthesizing text-to-speech for Discord voice messages."""

    @staticmethod
    def generate_tts(text, output_file="/tmp/swarm_tts.mp3", voice="en-US-AriaNeural"):
        """
        Synthesize text into a natural-sounding voice using edge-tts.
        Provide the text you want out loud.
        """
        if not text:
            return "[Error] No text provided for TTS."

        try:
            # Using edge-tts CLI
            process = subprocess.Popen(
                ["edge-tts", "--voice", voice, "--text", text, "--write-media", output_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=60)
            
            if process.returncode != 0:
                return f"[Error] TTS generation failed: {stderr}"
                
            msg = f"[Success] TTS generated at {output_file}. "
            msg += f"CRITICAL REQUIREMENT: To send this audio to the user, you MUST include the exact string [ATTACH_AUDIO:{output_file}] somewhere in your FINAL_ANSWER."
            return msg
            
        except FileNotFoundError:
            return "[Error] edge-tts is not installed. Run: pip install edge-tts"
        except Exception as e:
            return f"[Error] TTS failed: {str(e)}"
