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
global_order_counter = 0     

TYPE_SIZES = {
    'hp': 4,
    'xp': 4,
    'status': 2,
    'lore': 64
}

def format_web_voice(raw_text):
    raw_text = raw_text.replace('-', ' minus ').replace('+', ' plus ').replace('*', ' times ').replace('x', ' times ')
    words = raw_text.lower().split()
    
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
    
    if not final_string.endswith("done") and not final_string.endswith("close"):
        final_string += " done"
    return final_string

def run_web_semantics(tokens):
    global global_inventory, global_level_offsets, global_current_level, global_order_counter
    print(f"\n--- STARTING SEMANTIC ANALYSIS (State: Level {global_current_level}) ---")
    i = 0
    success_msg = ""
    
    while i < len(tokens):
        token_type = tokens[i][0]
        token_val = tokens[i][1]
        
        if token_type == 'SCOPE_IN':
            global_current_level += 1
            global_level_offsets[global_current_level] = 0 
            print(f"[SEMANTICS] Scope opened. Dropped to Level {global_current_level}.")
            success_msg = f"Scope opened at Level {global_current_level}."
            i += 1
            continue
            
        elif token_type == 'SCOPE_OUT':
            global_current_level = max(0, global_current_level - 1)
            current_offset = global_level_offsets.get(global_current_level, 0)
            print(f"[SEMANTICS] Scope closed. Returned to Level {global_current_level}.")
            if not success_msg: 
                success_msg = f"Scope closed. Returned to Level {global_current_level}."
            i += 1
            continue
            
        elif token_type == 'DATATYPE':
            dtype = token_val
            var_name = tokens[i+1][1]
            space_required = TYPE_SIZES.get(dtype, 4)
            current_offset = global_level_offsets.get(global_current_level, 0)
            
            if var_name not in global_inventory:
                global_order_counter += 1
                order_id = global_order_counter
            else:
                order_id = global_inventory[var_name]['order']
            
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if dtype not in ['hp', 'xp']: 
                    # --- NEW: STRUCTURED SEMANTIC ERROR (MATH) ---
                    return False, {
                        "reason": f"Attempted mathematical operation on '{dtype}' type.",
                        "rule": "Math operators (plus, minus, times) are strictly reserved for numeric stats.",
                        "fix": "Remove the math operator or change the data type to 'hp' or 'xp'.",
                        "suggestion": f"hp {var_name} equip 100 plus 50 done"
                    }
                
                val1, op, val2 = int(tokens[i+3][1]), tokens[i+4][1], int(tokens[i+5][1])
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                global_inventory[var_name] = {
                    'type': dtype, 'value': final_val, 
                    'level': f"Level {global_current_level}", 
                    'offset': current_offset, 
                    'space': f"{space_required} bytes",
                    'order': order_id
                }
                global_level_offsets[global_current_level] += space_required
                success_msg = f"Math calculated. {var_name} is now {final_val}."
                
                if i + 7 < len(tokens) and tokens[i+6][0] == 'SCOPE_OUT':
                    i += 6 
                else:
                    i += 7
                    
            else:
                lit_type, raw_val = tokens[i+3][0], tokens[i+3][1].replace('"', '')
                if dtype == 'hp' and lit_type != 'LITERAL_NUM': 
                    # --- NEW: STRUCTURED SEMANTIC ERROR (TYPE MISMATCH HP) ---
                    return False, {
                        "reason": f"Type mismatch. Attempted to equip text into an 'hp' integer block.",
                        "rule": "The 'hp' (Health Points) data type strictly requires raw numeric values.",
                        "fix": "Provide a raw number without any text.",
                        "suggestion": f"hp {var_name} equip 500 done"
                    }
                if dtype == 'lore' and lit_type != 'LITERAL_STR': 
                    # --- NEW: STRUCTURED SEMANTIC ERROR (TYPE MISMATCH LORE) ---
                    return False, {
                        "reason": f"Type mismatch. Attempted to equip a number into a 'lore' string block.",
                        "rule": "The 'lore' data type is for text and requires string literals.",
                        "fix": "Speak it clearly as text, or wrap your written value in quotation marks.",
                        "suggestion": f'lore {var_name} equip "legendary item" done'
                    }
                
                global_inventory[var_name] = {
                    'type': dtype, 'value': raw_val, 
                    'level': f"Level {global_current_level}", 
                    'offset': current_offset, 
                    'space': f"{space_required} bytes",
                    'order': order_id
                }
                global_level_offsets[global_current_level] += space_required
                success_msg = f"Successfully equipped {var_name}."
                
                if i + 5 < len(tokens) and tokens[i+4][0] == 'SCOPE_OUT':
                    i += 4 
                else:
                    i += 5
        else:
            i += 1

    if success_msg:
        return True, success_msg
        
    # --- FALLBACK SEMANTIC ERROR ---
    return False, {
        "reason": "The Semantic Analyzer could not process the assignment.",
        "rule": "Variables must be properly typed and formatted.",
        "fix": "Check your spelling and ensure no keywords are missing.",
        "suggestion": "hp bossHealth equip 5000 done"
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    raw_code = data.get('code', '')
    mode = data.get('mode', 'voice') 
    
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    fixed_code = ""
    
    try:
        if mode == 'voice':
            fixed_code = format_web_voice(raw_code)
            print(f"[VOICE IN] >>> {fixed_code} <<<")
        else:
            fixed_code = raw_code.strip()
            print(f"[TEXT IN] >>>\n{fixed_code}\n<<<")
            
        tokens = run_lexer(fixed_code)
        
        # --- NEW: PARSER ERROR CATCHING ---
        if not run_parser(tokens):
            msg = "Compilation failed. Syntax error detected."
            print(f"\n[FORGE-AI]: {msg}")
            
            error_details = {
                "reason": "The Parser detected a structural grammar violation.",
                "rule": "A standard ForgeLang assignment must follow: [DataType] [Identifier] [equip] [Value] [done]",
                "fix": "Ensure you are using the exact keywords in the correct mathematical order.",
                "suggestion": "hp enemyHealth equip 100 done"
            }
            
            return jsonify({
                "status": "error", "message": msg, "code": fixed_code,
                "error_details": error_details, "inventory": global_inventory,
                "terminal_logs": captured_output.getvalue()
            })
            
        # --- NEW: SEMANTICS ERROR CATCHING ---
        success, result = run_web_semantics(tokens)
        if not success:
            msg = "Compilation failed. Semantic type error detected."
            print(f"\n[FORGE-AI]: {msg}")
            
            return jsonify({
                "status": "error", "message": msg, "code": fixed_code,
                "error_details": result, "inventory": global_inventory,
                "terminal_logs": captured_output.getvalue()
            })
            
        # --- SUCCESS PATH ---
        print(f"\n[FORGE-AI]: {result}")
        sorted_inv = sorted(global_inventory.items(), key=lambda x: x[1]['order'])
        
        print("\n" + "="*45)
        print(f"||{'LIVE INVENTORY STATE':^41}||")
        print("="*45)
        print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'VALUE':<10} ||")
        print("-" * 45)
        for var, d in sorted_inv:
            print(f"|| {var:<15} | {d['type']:<7} | {str(d['value']):<10} ||")
        print("="*45)
        
        print("\n" + "="*66)
        print(f"||{'COMPILER SYMBOL TABLE (MEMORY MAP)':^62}||")
        print("="*66)
        print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'LEVEL':<7} | {'OFFSET':<6} | {'SPACE':<9} ||")
        print("-" * 66)
        for var, d in sorted_inv:
            print(f"|| {var:<15} | {d['type']:<7} | {d['level']:<7} | {str(d['offset']):<6} | {d['space']:<9} ||")
        print("="*66 + "\n")
                
    finally:
        sys.stdout = sys.__stdout__
        
    return jsonify({
        "status": "success", "message": result, "code": fixed_code,
        "inventory": global_inventory, "terminal_logs": captured_output.getvalue()
    })

@app.route('/reset', methods=['POST'])
def reset_memory():
    global global_inventory, global_level_offsets, global_current_level, global_order_counter
    global_inventory.clear()
    global_level_offsets = {0: 0}
    global_current_level = 0
    global_order_counter = 0  
    return jsonify({"status": "success", "message": "Memory purged successfully."})

if __name__ == "__main__":
    app.run(debug=True)