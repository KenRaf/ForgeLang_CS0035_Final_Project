from flask import Flask, render_template, request, jsonify
from forge_lexer import run_lexer
from forge_parser import run_parser
import sys
import io

app = Flask(__name__)

# --- TRUE MEMORY STATE ---
global_inventory = {}
global_level_offsets = {0: 0}  
global_current_level = 0       

TYPE_SIZES = {
    'hp': 4,
    'xp': 4,
    'status': 2,
    'lore': 64
}

def format_web_voice(raw_text):
    raw_text = raw_text.replace('-', ' minus ').replace('+', ' plus ').replace('*', ' times ').replace('x', ' times ')
    words = raw_text.lower().split()
    
    # <--- UPDATED KEYWORD LIST
    keywords = ['hp', 'lore', 'xp', 'status', 'equip', 'done', 'spawn', 'plus', 'minus', 'times', 'begin', 'close']
    
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
    
    # <--- UPDATED ENDSWITH CHECK
    if not final_string.endswith("done") and not final_string.endswith("close"):
        final_string += " done"
    return final_string

def run_web_semantics(tokens):
    global global_inventory, global_level_offsets, global_current_level
    print(f"\n--- STARTING SEMANTIC ANALYSIS (State: Level {global_current_level}) ---")
    i = 0
    
    while i < len(tokens):
        token_type = tokens[i][0]
        token_val = tokens[i][1]
        
        if token_type == 'SCOPE_IN':
            global_current_level += 1
            global_level_offsets[global_current_level] = 0 
            print(f"[SEMANTICS] Scope opened. Dropped to Level {global_current_level}. Offset reset to 0.")
            i += 1
            continue
        elif token_type == 'SCOPE_OUT':
            global_current_level = max(0, global_current_level - 1)
            current_offset = global_level_offsets[global_current_level]
            print(f"[SEMANTICS] Scope closed. Returned to Level {global_current_level}. Resuming at offset {current_offset}.")
            i += 1
            continue
            
        if token_type == 'DATATYPE':
            dtype = token_val
            var_name = tokens[i+1][1]
            space_required = TYPE_SIZES.get(dtype, 4)
            current_offset = global_level_offsets[global_current_level]
            
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if dtype not in ['hp', 'xp']: 
                    return False, "Fatal Error: Math on non-numeric type."
                
                val1, op, val2 = int(tokens[i+3][1]), tokens[i+4][1], int(tokens[i+5][1])
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                print(f"[SEMANTICS] Allocating {space_required} bytes at Level {global_current_level}, Offset {current_offset}.")
                global_inventory[var_name] = {
                    'type': dtype, 'value': final_val, 
                    'level': f"Level {global_current_level}", 
                    'offset': current_offset, 
                    'space': f"{space_required} bytes"
                }
                global_level_offsets[global_current_level] += space_required
                return True, f"Math calculated. {var_name} is now {final_val}."
                
            else:
                lit_type, raw_val = tokens[i+3][0], tokens[i+3][1].replace('"', '')
                if dtype == 'hp' and lit_type != 'LITERAL_NUM': 
                    return False, "Fatal Error: Cannot equip text to HP."
                if dtype == 'lore' and lit_type != 'LITERAL_STR': 
                    return False, "Fatal Error: Cannot equip number to Lore."
                
                print(f"[SEMANTICS] Allocating {space_required} bytes at Level {global_current_level}, Offset {current_offset}.")
                global_inventory[var_name] = {
                    'type': dtype, 'value': raw_val, 
                    'level': f"Level {global_current_level}", 
                    'offset': current_offset, 
                    'space': f"{space_required} bytes"
                }
                global_level_offsets[global_current_level] += space_required
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
            
            if success:
                print("\n" + "="*45)
                print(f"||{'LIVE INVENTORY STATE':^41}||")
                print("="*45)
                print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'VALUE':<10} ||")
                print("-" * 45)
                for var, d in global_inventory.items():
                    print(f"|| {var:<15} | {d['type']:<7} | {str(d['value']):<10} ||")
                print("="*45)
                
                print("\n" + "="*66)
                print(f"||{'COMPILER SYMBOL TABLE (MEMORY MAP)':^62}||")
                print("="*66)
                print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'LEVEL':<7} | {'OFFSET':<6} | {'SPACE':<9} ||")
                print("-" * 66)
                for var, d in global_inventory.items():
                    print(f"|| {var:<15} | {d['type']:<7} | {d['level']:<7} | {str(d['offset']):<6} | {d['space']:<9} ||")
                print("="*66 + "\n")
                
    finally:
        sys.stdout = sys.__stdout__
        
    terminal_logs = captured_output.getvalue()
    
    return jsonify({
        "status": "success" if success else "error",
        "message": msg,
        "inventory": global_inventory,
        "code": fixed_code,
        "terminal_logs": terminal_logs
    })

@app.route('/reset', methods=['POST'])
def reset_memory():
    global global_inventory, global_level_offsets, global_current_level
    
    global_inventory.clear()
    global_level_offsets = {0: 0}
    global_current_level = 0
    
    return jsonify({"status": "success", "message": "Memory purged successfully."})

if __name__ == "__main__":
    app.run(debug=True)