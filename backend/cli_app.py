from speech_to_text import SpeechProcessor
from code_generator import CodeGenerator


def main():
    print("=== CodeVoice AI Assistant ===")

    try:
        speech_processor = SpeechProcessor()
        code_gen = CodeGenerator()
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        return

    while True:
        try:
            text = speech_processor.transcribe_microphone()
            print(f"\nYou said: {text}")

            print("\nGenerating code...")
            code = code_gen.generate_code(text)

            if code:
                print("\n=== Generated Code ===")
                print(code)
                print("======================")

            print("\nPress Ctrl+C to exit or speak again...")

        except KeyboardInterrupt:
            print("\nExiting CodeVoice...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue


if __name__ == "__main__":
    main()