from flask import Flask, render_template, request, jsonify
from forge_lexer import run_lexer
from forge_parser import run_parser
import sys
import io

app = Flask(__name__)

global_inventory = {}

def format_web_voice(raw_text):
    raw_text = raw_text.replace('-', ' minus ').replace('+', ' plus ').replace('*', ' times ').replace('x', ' times ')
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
            
    final_string = " ".join(processed_words)
    if not final_string.endswith("done"):
        final_string += " done"
    return final_string

def run_web_semantics(tokens):
    print("\n--- STARTING SEMANTIC ANALYSIS ---")
    i = 0
    while i < len(tokens):
        if tokens[i][0] == 'DATATYPE':
            dtype = tokens[i][1]
            var_name = tokens[i+1][1]
            
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if dtype not in ['hp', 'xp']: 
                    print(f"[SEMANTICS] FATAL ERROR: Cannot perform math on non-numeric '{dtype}'.")
                    return False, "Fatal Error: Math on non-numeric type."
                
                val1, op, val2 = int(tokens[i+3][1]), tokens[i+4][1], int(tokens[i+5][1])
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                print(f"[SEMANTICS] Math recognized. Calculating: {val1} {op} {val2} = {final_val}")
                global_inventory[var_name] = {'type': dtype, 'value': final_val}
                return True, f"Math calculated. {var_name} is now {final_val}."
                
            else:
                lit_type, raw_val = tokens[i+3][0], tokens[i+3][1].replace('"', '')
                if dtype == 'hp' and lit_type != 'LITERAL_NUM': 
                    print(f"[SEMANTICS] FATAL ERROR: Cannot equip STRING into numeric 'hp' stat.")
                    return False, "Fatal Error: Cannot equip text to HP."
                if dtype == 'lore' and lit_type != 'LITERAL_STR': 
                    print(f"[SEMANTICS] FATAL ERROR: Cannot equip NUMBER into text 'lore' stat.")
                    return False, "Fatal Error: Cannot equip number to Lore."
                
                print(f"[SEMANTICS] Types match. Binding '{var_name}' to Symbol Table.")
                global_inventory[var_name] = {'type': dtype, 'value': raw_val}
                return True, f"Successfully equipped {var_name}."
        i += 1
    return False, "Unknown semantic error."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    raw_voice = data.get('code', '')
    
    # [STREAM INTERCEPTION START] 
    # Hijack Python's print function and route it to 'captured_output'
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    success = False
    msg = ""
    fixed_code = ""
    
    try:
        fixed_code = format_web_voice(raw_voice)
        print(f"[RECEIVED CODE] >>> {fixed_code} <<<")
        
        tokens = run_lexer(fixed_code)
        
        if not run_parser(tokens):
            msg = "Compilation failed. Syntax error detected."
            print(f"\n[FORGE-AI]: {msg}")
        else:
            success, msg = run_web_semantics(tokens)
            print(f"\n[FORGE-AI]: {msg}")
            
            # Print the UI table to the hidden terminal logs if successful
            if success:
                print("\n" + "="*45)
                print(f"||{'LIVE INVENTORY (SYMBOL TABLE)':^41}||")
                print("="*45)
                print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'VALUE':<10} ||")
                print("-" * 45)
                for var, d in global_inventory.items():
                    print(f"|| {var:<15} | {d['type']:<7} | {d['value']:<10} ||")
                print("="*45 + "\n")
                
    finally:
        # [STREAM INTERCEPTION END]
        # Always give print() back to the system
        sys.stdout = sys.__stdout__
        
    # Grab all the print statements we hijacked as a single text block
    terminal_logs = captured_output.getvalue()
    
    return jsonify({
        "status": "success" if success else "error",
        "message": msg,
        "inventory": global_inventory,
        "code": fixed_code,
        "terminal_logs": terminal_logs
    })

if __name__ == "__main__":
    app.run(debug=True)