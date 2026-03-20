from flask import Flask, render_template, request, jsonify
from forge_lexer import run_lexer
from forge_parser import run_parser

app = Flask(__name__)

# This is our global memory for the web session!
# It will keep your stats saved as long as the server is running.
global_inventory = {}

def format_web_voice(raw_text):
    """Formats the voice text exactly like our God Mode desktop version."""
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
    """Simplified Semantics that directly updates our web memory."""
    i = 0
    while i < len(tokens):
        if tokens[i][0] == 'DATATYPE':
            dtype = tokens[i][1]
            var_name = tokens[i+1][1]
            
            # Math Logic
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if dtype not in ['hp', 'xp']: return False, "Fatal Error: Math on non-numeric type."
                val1, op, val2 = int(tokens[i+3][1]), tokens[i+4][1], int(tokens[i+5][1])
                
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                global_inventory[var_name] = {'type': dtype, 'value': final_val}
                return True, f"Math calculated. {var_name} is now {final_val}."
                
            # Standard Assignment
            else:
                lit_type, raw_val = tokens[i+3][0], tokens[i+3][1].replace('"', '')
                if dtype == 'hp' and lit_type != 'LITERAL_NUM': return False, "Fatal Error: Cannot equip text to HP."
                if dtype == 'lore' and lit_type != 'LITERAL_STR': return False, "Fatal Error: Cannot equip number to Lore."
                
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
    
    # 1. Pre-process voice
    fixed_code = format_web_voice(raw_voice)
    
    # 2. Run Lexer & Parser
    tokens = run_lexer(fixed_code)
    if not run_parser(tokens):
        return jsonify({"status": "error", "message": "Compilation failed. Syntax error detected.", "inventory": global_inventory, "code": fixed_code})
    
    # 3. Run Semantics
    success, msg = run_web_semantics(tokens)
    if not success:
        return jsonify({"status": "error", "message": msg, "inventory": global_inventory, "code": fixed_code})
        
    return jsonify({"status": "success", "message": msg, "inventory": global_inventory, "code": fixed_code})

if __name__ == "__main__":
    app.run(debug=True)