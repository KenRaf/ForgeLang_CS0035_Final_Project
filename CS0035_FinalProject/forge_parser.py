def run_parser(tokens):
    print("\n--- STARTING SYNTAX ANALYSIS ---")
    i = 0
    while i < len(tokens):
        tok_type, tok_val = tokens[i][0], tokens[i][1]

        if tok_type in ['SCOPE_IN', 'SCOPE_OUT']:
            print(f"[PARSER] Valid scope modifier '{tok_val}' found.")
            i += 1
            continue

        if tok_type == 'DATATYPE':
            if i + 1 >= len(tokens) or tokens[i+1][0] != 'ID':
                return False, {"type": "SYNTAX ERROR", "reason": "Missing variable name.", "rule": "An identifier must follow the data type.", "fix": "Add a valid name after the type.", "suggestion": f"{tok_val} myVar equip 100 done"}
            
            if i + 2 >= len(tokens) or tokens[i+2][0] != 'ASSIGN':
                return False, {"type": "SYNTAX ERROR", "reason": "Missing 'equip' operator.", "rule": "You must use 'equip' to assign a value.", "fix": "Add 'equip' after the variable name.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip 100 done"}
            
            if i + 3 >= len(tokens) or not tokens[i+3][0].startswith('LITERAL'):
                return False, {"type": "SYNTAX ERROR", "reason": "Missing assignment value.", "rule": "You must provide a value after 'equip'.", "fix": "Add a number or text string.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip 100 done"}

            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                print("[PARSER] Evaluating Math Rule: [DATATYPE] [ID] [ASSIGN] [LITERAL] [MATH_OP] [LITERAL] [DELIM]")
                if i + 5 >= len(tokens) or not tokens[i+5][0].startswith('LITERAL'):
                    return False, {"type": "SYNTAX ERROR", "reason": "Missing second value for math operation.", "rule": "Math operators require a value on both sides.", "fix": "Add a number after the operator.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} plus 50 done"}
                
                next_idx = i + 6
                if next_idx < len(tokens) and tokens[next_idx][0] == 'SCOPE_OUT':
                    next_idx += 1
                    
                if next_idx >= len(tokens) or tokens[next_idx][0] != 'DELIM':
                    return False, {"type": "SYNTAX ERROR", "reason": "Missing delimiter or punctuation.", "rule": "Every statement must end with 'done'.", "fix": "Add 'done' at the end.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} plus 50 done"}
                    
                print("[PARSER] Math structure matches expected rule perfectly.")
                i = next_idx + 1 
            else:
                print("[PARSER] Evaluating Standard Rule: [DATATYPE] [ID] [ASSIGN] [LITERAL] [DELIM]")
                next_idx = i + 4
                if next_idx < len(tokens) and tokens[next_idx][0] == 'SCOPE_OUT':
                    next_idx += 1
                    
                if next_idx >= len(tokens) or tokens[next_idx][0] != 'DELIM':
                    if next_idx < len(tokens):
                         return False, {"type": "SYNTAX ERROR", "reason": f"Unexpected token '{tokens[next_idx][1]}' before 'done'.", "rule": "Standard assignments require exactly: [Type] [Name] [equip] [Value] [done].", "fix": "Remove the extra words.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} done"}
                    return False, {"type": "SYNTAX ERROR", "reason": "Missing delimiter or punctuation.", "rule": "Every statement must end with 'done'.", "fix": "Add 'done' at the end.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} done"}
                
                print("[PARSER] Standard structure matches expected rule perfectly.")
                i = next_idx + 1 
        else:
            return False, {"type": "SYNTAX ERROR", "reason": f"Incorrect keyword usage: '{tok_val}'.", "rule": "Statements must begin with a valid DataType (hp, xp, lore) or Scope modifier (begin).", "fix": "Start the line with a valid declaration keyword.", "suggestion": "hp playerHealth equip 100 done"}

    print("Syntax Analysis Complete. No structural errors.")
    return True, {}