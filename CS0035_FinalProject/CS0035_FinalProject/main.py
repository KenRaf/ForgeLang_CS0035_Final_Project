import speech_recognition as sr
import pyttsx3
from forge_lexer import run_lexer
from forge_parser import run_parser
from forge_semantics import run_semantics

# Initialize the Text-to-Speech Engine
tts = pyttsx3.init()
tts.setProperty('rate', 170) # Slower, more robotic AI voice

def speak(text):
    print(f"\n🔊 [FORGE-AI]: {text}")
    tts.say(text)
    tts.runAndWait()

def format_voice_text(raw_text):
    # --- NEW: Intercept Google's helpful math symbols ---
    raw_text = raw_text.replace('-', ' minus ')
    raw_text = raw_text.replace('+', ' plus ')
    raw_text = raw_text.replace('*', ' times ')
    raw_text = raw_text.replace('x', ' times ') # Sometimes it hears 'x' for multiplication
    
    words = raw_text.lower().split()
    keywords = ['hp', 'lore', 'xp', 'status', 'equip', 'done', 'spawn', 'plus', 'minus', 'times']
    
    processed_words = []
    i = 0
    while i < len(words):
        if words[i] in ['hp', 'lore', 'xp', 'status', 'spawn']:
            processed_words.append(words[i]) 
            i += 1
            var_name_parts = []
            while i < len(words) and words[i] not in keywords:
                var_name_parts.append(words[i])
                i += 1
            if var_name_parts:
                camel_case_var = var_name_parts[0] + ''.join(w.capitalize() for w in var_name_parts[1:])
                processed_words.append(camel_case_var)
        else:
            processed_words.append(words[i])
            i += 1
            
    # --- NEW: Auto-fix if the mic cuts off the 'done' keyword ---
    final_string = " ".join(processed_words)
    if not final_string.endswith("done"):
        final_string += " done"
        
    return final_string

def capture_voice_code():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[MIC ACTIVE] Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        
        print("\n[READY] Speak your ForgeLang code now.")
        print("        Try: 'hp boss health equip 100 minus 20 done'")
        
        try:
            audio = recognizer.listen(source, timeout=5) 
            raw_text = recognizer.recognize_google(audio)
            fixed_text = format_voice_text(raw_text)
            print(f"\n[RECEIVED CODE] >>> {fixed_text} <<<")
            return fixed_text
            
        except sr.WaitTimeoutError:
            return None
        except Exception:
            return None

def main():
    print("=== FORGELANG COMPILER v3.0 (GOD MODE) ===")
    speak("Forge engine initialized. Awaiting voice command.")
    
    code = capture_voice_code()
    
    if code:
        tokens = run_lexer(code)
        if not run_parser(tokens):
            speak("Compilation failed. Syntax error detected.")
            return
            
        if not run_semantics(tokens):
            speak("Compilation failed. Fatal type error in semantics.")
            return
            
        speak("Code accepted. Variables successfully equipped to inventory.")
    else:
        speak("No valid command detected. Aborting turn.")

if __name__ == "__main__":
    main()