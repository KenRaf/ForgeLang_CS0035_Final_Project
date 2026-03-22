from flask import Flask, render_template, request, jsonify
from forge_lexer import run_lexer
from forge_parser import run_parser
import sys
import io

app = Flask(__name__)

global_inventory = {}
global_level_offsets = {0: 0}  
global_current_level = 0       
global_order_counter = 0     

TYPE_SIZES = {'hp': 4, 'xp': 4, 'status': 2, 'lore': 64}

def format_web_voice(raw_text):
    raw_text = raw_text.replace('-', ' minus ').replace('+', ' plus ').replace('*', ' times ').replace('x', ' times ').replace('=', ' equals ').replace('>', ' greater ').replace('<', ' less ')
    words = raw_text.lower().split()
    final_string = " ".join(words)
    if not final_string.endswith("done") and not final_string.endswith("close"):
        final_string += " done"
    return final_string

def run_web_semantics(tokens):
    global global_inventory, global_level_offsets, global_current_level, global_order_counter
    
    if not tokens: return True, "Ready for input."
    
    print(f"\n--- STARTING SEMANTIC ANALYSIS (State: Level {global_current_level}) ---")
    i = 0
    success_msg = ""
    
    while i < len(tokens):
        token_type, token_val, token_line = tokens[i][0], tokens[i][1], tokens[i][2]
        
        if token_type == 'SCOPE_IN':
            global_current_level += 1
            global_level_offsets[global_current_level] = 0 
            print(f"[SEMANTICS] Line {token_line}: Scope opened. Dropped to Level {global_current_level}. Offset reset to 0.")
            success_msg = f"Scope opened at Level {global_current_level}."
            i += 1
            continue
            
        elif token_type == 'SCOPE_OUT':
            global_current_level = max(0, global_current_level - 1)
            current_offset = global_level_offsets.get(global_current_level, 0)
            
            if i + 5 < len(tokens) and tokens[i+1][0] == 'LOOP_TYPE' and tokens[i+1][1] == 'while':
                cmp_var = tokens[i+2][1]
                cmp_op = tokens[i+3][1]
                cmp_val = tokens[i+4][1]
                print(f"[SEMANTICS] Line {token_line}: Do-While loop closed and condition checked ({cmp_var} {cmp_op} {cmp_val}). Returned to Level {global_current_level}.")
                i += 6
                continue
            else:
                print(f"[SEMANTICS] Line {token_line}: Scope closed. Returned to Level {global_current_level}. Resuming at offset {current_offset}.")
                if not success_msg: success_msg = f"Scope closed. Returned to Level {global_current_level}."
                i += 1
                continue

        elif token_type == 'FUNC_DECL':
            func_name = tokens[i+1][1]
            if func_name not in global_inventory:
                global_order_counter += 1
                order_id = global_order_counter
            else: order_id = global_inventory[func_name]['order']
                
            current_offset = global_level_offsets.get(global_current_level, 0)
            global_inventory[func_name] = {'type': 'skill', 'value': '[Func Block]', 'level': f"Level {global_current_level}", 'level_int': global_current_level, 'offset': current_offset, 'width': "8 bytes", 'width_int': 8, 'order': order_id}
            global_level_offsets[global_current_level] += 8
            print(f"[SEMANTICS] Line {token_line}: Declared skill '{func_name}'. Allocated 8 byte pointer.")
            
            global_current_level += 1
            global_level_offsets[global_current_level] = 0
            print(f"[SEMANTICS] Line {token_line}: Skill Scope opened. Dropped to Level {global_current_level}.")
            i += 3
            continue
            
        elif token_type == 'FUNC_CALL':
            func_name = tokens[i+1][1]
            if func_name not in global_inventory or global_inventory[func_name]['type'] != 'skill':
                return False, {"type": "SEMANTIC ERROR", "line": token_line, "reason": f"Undeclared skill '{func_name}'.", "rule": "You cannot cast a skill that hasn't been declared.", "fix": "Declare it first.", "suggestion": f"skill {func_name} begin ... close"}
            print(f"[SEMANTICS] Line {token_line}: Successfully casted skill '{func_name}'.")
            success_msg = f"Casted {func_name}."
            i += 3
            continue

        elif token_type == 'LOOP_TYPE' and token_val == 'do':
            print(f"[SEMANTICS] Line {token_line}: Do-While Loop started.")
            global_current_level += 1
            global_level_offsets[global_current_level] = 0
            i += 2
            continue
            
        elif token_type == 'LOOP_START':
            l_type = tokens[i+1][1]
            if l_type == 'for':
                dtype = tokens[i+2][1].lower()
                var_name = tokens[i+3][1]
                start_val = tokens[i+5][1]
                end_val = tokens[i+7][1]
                
                if var_name not in global_inventory:
                    global_order_counter += 1
                    order_id = global_order_counter
                else: order_id = global_inventory[var_name]['order']
                    
                space_required = TYPE_SIZES.get(dtype, 4)
                global_current_level += 1
                global_level_offsets[global_current_level] = 0
                current_offset = global_level_offsets[global_current_level]
                
                global_inventory[var_name] = {'type': dtype, 'value': f"{start_val} to {end_val}", 'level': f"Level {global_current_level}", 'level_int': global_current_level, 'offset': current_offset, 'width': f"{space_required} bytes", 'width_int': space_required, 'order': order_id}
                global_level_offsets[global_current_level] += space_required
                print(f"[SEMANTICS] Line {token_line}: For Loop opened. Iterator '{var_name}' bound to Level {global_current_level}.")
                i += 9
                continue
                
            elif l_type == 'while':
                var_name = tokens[i+2][1]
                cmp_op = tokens[i+3][1]
                cmp_val = tokens[i+4][1]
                
                if var_name not in global_inventory:
                    return False, {"type": "SEMANTIC ERROR", "line": token_line, "reason": f"Undeclared variable '{var_name}' in condition.", "rule": "While loops must check an existing variable.", "fix": "Declare it first.", "suggestion": f"hp {var_name} equip 100 done"}
                    
                global_current_level += 1
                global_level_offsets[global_current_level] = 0
                print(f"[SEMANTICS] Line {token_line}: While Loop opened at Level {global_current_level}. Condition bound: {var_name} {cmp_op} {cmp_val}.")
                i += 6
                continue

        elif token_type == 'OUTPUT':
            target_type, target_val = tokens[i+1][0], tokens[i+1][1]
            
            if target_type == 'ID':
                if target_val not in global_inventory:
                    return False, {"type": "SEMANTIC ERROR", "line": token_line, "reason": f"Undeclared variable '{target_val}'.", "rule": "Cannot spawn a variable that does not exist.", "fix": "Declare it first.", "suggestion": f"hp {target_val} equip 100 done"}
                output_val = global_inventory[target_val]['value']
            else:
                output_val = target_val.replace('"', '')
                
            print(f"[SEMANTICS] Line {token_line}: Spawn command triggered.")
            
            print(f"\n" + "▒"*50)
            print(f"▒▒▒ 🖥️  PROGRAM OUTPUT: {output_val} ")
            print(f"▒"*50 + "\n")
            
            if not success_msg: success_msg = f"Spawned output successfully."
            i += 3
            continue

        elif token_type == 'DATATYPE':
            dtype = token_val.lower() 
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
                    return False, {
                        "type": "SEMANTIC ERROR", "line": token_line,
                        "reason": f"Type mismatch. Attempted mathematical operation on '{dtype}' type.",
                        "rule": "Logically inconsistent: Math operators are strictly reserved for numeric stats.",
                        "fix": "Remove the math operator or change the data type.",
                        "suggestion": f"hp {var_name} equip 100 plus 50 done"
                    }
                
                val1, op, val2 = int(tokens[i+3][1]), tokens[i+4][1], int(tokens[i+5][1])
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                print(f"[SEMANTICS] Line {token_line}: Allocating {space_required} bytes at Level {global_current_level}, Offset {current_offset}.")
                global_inventory[var_name] = {'type': dtype, 'value': final_val, 'level': f"Level {global_current_level}", 'level_int': global_current_level, 'offset': current_offset, 'width': f"{space_required} bytes", 'width_int': space_required, 'order': order_id}
                global_level_offsets[global_current_level] += space_required
                success_msg = f"Math calculated. {var_name} is now {final_val}."
                i += 6 if (i + 7 < len(tokens) and tokens[i+6][0] == 'SCOPE_OUT') else 7
                    
            else:
                lit_type, raw_val = tokens[i+3][0], tokens[i+3][1].replace('"', '')
                if dtype == 'hp' and lit_type != 'LITERAL_NUM': 
                    return False, {
                        "type": "SEMANTIC ERROR", "line": token_line,
                        "reason": f"Type mismatch. Attempted to equip text into an 'hp' integer block.",
                        "rule": "Logically inconsistent: The 'hp' stat strictly requires raw numeric values.",
                        "fix": "Provide a raw number without any text.",
                        "suggestion": f"hp {var_name} equip 500 done"
                    }
                if dtype == 'lore' and lit_type != 'LITERAL_STR': 
                    return False, {
                        "type": "SEMANTIC ERROR", "line": token_line,
                        "reason": f"Type mismatch. Attempted to equip a number into a 'lore' string block.",
                        "rule": "Logically inconsistent: The 'lore' data type is for text and requires string literals.",
                        "fix": "Speak it clearly as text, or wrap your written value in quotation marks.",
                        "suggestion": f'lore {var_name} equip "legendary item" done'
                    }
                
                print(f"[SEMANTICS] Line {token_line}: Allocating {space_required} bytes at Level {global_current_level}, Offset {current_offset}.")
                global_inventory[var_name] = {'type': dtype, 'value': raw_val, 'level': f"Level {global_current_level}", 'level_int': global_current_level, 'offset': current_offset, 'width': f"{space_required} bytes", 'width_int': space_required, 'order': order_id}
                global_level_offsets[global_current_level] += space_required
                success_msg = f"Successfully equipped {var_name}."
                i += 4 if (i + 5 < len(tokens) and tokens[i+4][0] == 'SCOPE_OUT') else 5
        else:
            i += 1

    if success_msg: return True, success_msg
    return False, {"type": "SEMANTIC ERROR", "line": 1, "reason": "Unidentified logical inconsistency.", "rule": "Variables must be logically typed.", "fix": "Check spelling.", "suggestion": "hp bossHealth equip 5000 done"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    global global_inventory, global_level_offsets, global_current_level, global_order_counter
    data = request.json
    raw_code, mode = data.get('code', ''), data.get('mode', 'voice') 
    
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        if mode == 'text':
            global_inventory.clear()
            global_level_offsets = {0: 0}
            global_current_level = 0
            global_order_counter = 0  
        
        fixed_code = format_web_voice(raw_code) if mode == 'voice' else raw_code.strip()
        print(f"[{mode.upper()} IN] >>>\n{fixed_code}\n<<<")
            
        success, lex_result = run_lexer(fixed_code)
        if not success:
            print(f"\n[FORGE-AI]: Compilation halted at Lexical Analysis.")
            return jsonify({"status": "error", "message": "Lexical Error.", "code": fixed_code, "error_details": lex_result, "inventory": global_inventory, "terminal_logs": captured_output.getvalue()})
        
        success, parse_result = run_parser(lex_result)
        if not success:
            print(f"\n[FORGE-AI]: Compilation halted at Syntax Analysis.")
            return jsonify({"status": "error", "message": "Syntax Error.", "code": fixed_code, "error_details": parse_result, "inventory": global_inventory, "terminal_logs": captured_output.getvalue()})
            
        success, sem_result = run_web_semantics(lex_result)
        if not success:
            print(f"\n[FORGE-AI]: Compilation halted at Semantic Analysis.")
            return jsonify({"status": "error", "message": "Semantic Error.", "code": fixed_code, "error_details": sem_result, "inventory": global_inventory, "terminal_logs": captured_output.getvalue()})
            
        print(f"\n[FORGE-AI]: {sem_result}")
        sorted_inv = sorted(global_inventory.items(), key=lambda x: x[1]['order'])
        
        if sorted_inv:
            id_len = max([len("IDENTIFIER")] + [len(var) for var, d in sorted_inv])
            type_len = max([len("TYPE")] + [len(d['type']) for var, d in sorted_inv])
            val_len = max([len("VALUE")] + [len(str(d['value'])) for var, d in sorted_inv])
            lvl_len = max([len("LEVEL")] + [len(d['level']) for var, d in sorted_inv])
            off_len = max([len("OFFSET")] + [len(str(d['offset'])) for var, d in sorted_inv])
            width_len = max([len("WIDTH")] + [len(d['width']) for var, d in sorted_inv])

            inv_header = f"|| {'IDENTIFIER'.ljust(id_len)} | {'TYPE'.ljust(type_len)} | {'VALUE'.ljust(val_len)} ||"
            inv_border = "=" * len(inv_header)
            inv_divider = "-" * len(inv_header)

            print("\n" + inv_border)
            print(f"||{'LIVE INVENTORY STATE'.center(len(inv_header)-4)}||")
            print(inv_border)
            print(inv_header)
            print(inv_divider)
            for var, d in sorted_inv:
                print(f"|| {var.ljust(id_len)} | {d['type'].ljust(type_len)} | {str(d['value']).ljust(val_len)} ||")
            print(inv_border)
            
            sym_header = f"|| {'IDENTIFIER'.ljust(id_len)} | {'TYPE'.ljust(type_len)} | {'LEVEL'.ljust(lvl_len)} | {'OFFSET'.ljust(off_len)} | {'WIDTH'.ljust(width_len)} ||"
            sym_border = "=" * len(sym_header)
            sym_divider = "-" * len(sym_header)

            print("\n" + sym_border)
            print(f"||{'COMPILER SYMBOL TABLE (MEMORY MAP)'.center(len(sym_header)-4)}||")
            print(sym_border)
            print(sym_header)
            print(sym_divider)
            
            level_totals = {}
            for var, d in sorted_inv:
                print(f"|| {var.ljust(id_len)} | {d['type'].ljust(type_len)} | {d['level'].ljust(lvl_len)} | {str(d['offset']).ljust(off_len)} | {d['width'].ljust(width_len)} ||")
                lvl = d.get('level_int', int(d['level'].split()[1]))
                width_int = d.get('width_int', int(d['width'].split()[0]))
                level_totals[lvl] = level_totals.get(lvl, 0) + width_int
                
            print(sym_divider)
            for lvl in sorted(level_totals.keys()):
                label = "Global" if lvl == 0 else "Local "
                print(f"|| Total {label} Memory Required (Level {lvl}): {level_totals[lvl]} Bytes")
            print(sym_border + "\n")
                
    finally:
        sys.stdout = sys.__stdout__
        
    return jsonify({"status": "success", "message": sem_result, "code": fixed_code, "inventory": global_inventory, "terminal_logs": captured_output.getvalue()})

@app.route('/reset', methods=['POST'])
def reset_memory():
    global global_inventory, global_level_offsets, global_current_level, global_order_counter
    global_inventory.clear(); global_level_offsets = {0: 0}; global_current_level = 0; global_order_counter = 0  
    return jsonify({"status": "success", "message": "Memory purged successfully."})

if __name__ == "__main__":
    app.run(debug=True)