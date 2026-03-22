def run_parser(tokens):
    print("\n--- STARTING SYNTAX ANALYSIS ---")
    i = 0
    while i < len(tokens):
        tok_type, tok_val, tok_line = tokens[i][0], tokens[i][1], tokens[i][2]

        if tok_type == 'SCOPE_IN':
            print(f"[PARSER] Line {tok_line}: Valid scope modifier 'begin'.")
            i += 1
            continue
            
        # --- DO-WHILE CLOSURE LOGIC ---
        if tok_type == 'SCOPE_OUT':
            if i + 5 < len(tokens) and tokens[i+1][0] == 'LOOP_TYPE' and tokens[i+1][1] == 'while':
                if tokens[i+2][0] != 'ID' or tokens[i+3][0] != 'COMPARE_OP' or not tokens[i+4][0].startswith('LITERAL') or tokens[i+5][0] != 'DELIM':
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed do-while exit.", "rule": "Requires: close while [ID] [Compare] [Value] done", "fix": "Check syntax.", "suggestion": "close while playerHealth greater 0 done"}
                print(f"[PARSER] Line {tok_line}: Valid do-while closure sequence.")
                i += 6
                continue
            else:
                print(f"[PARSER] Line {tok_line}: Valid scope modifier 'close'.")
                i += 1
                continue

        # --- FUNCTIONS ---
        if tok_type == 'FUNC_DECL': 
            if i+2 >= len(tokens) or tokens[i+1][0] != 'ID' or tokens[i+2][0] != 'SCOPE_IN':
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed skill declaration.", "rule": "Requires: skill [Name] begin", "fix": "Follow correct format.", "suggestion": "skill healSpell begin"}
            print(f"[PARSER] Line {tok_line}: Valid function declaration.")
            i += 3
            continue

        if tok_type == 'FUNC_CALL': 
            if i+2 >= len(tokens) or tokens[i+1][0] != 'ID' or tokens[i+2][0] != 'DELIM':
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed cast.", "rule": "Requires: cast [Name] done", "fix": "Follow correct format.", "suggestion": "cast healSpell done"}
            print(f"[PARSER] Line {tok_line}: Valid function call.")
            i += 3
            continue

        # --- LOOPS ---
        if tok_type == 'LOOP_START': 
            if i+1 < len(tokens) and tokens[i+1][1] == 'for':
                if i+8 >= len(tokens) or tokens[i+2][0] != 'DATATYPE' or tokens[i+3][0] != 'ID' or tokens[i+4][0] != 'ASSIGN' or not tokens[i+5][0].startswith('LITERAL') or tokens[i+6][0] != 'TO' or not tokens[i+7][0].startswith('LITERAL') or tokens[i+8][0] != 'SCOPE_IN':
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed for loop.", "rule": "Requires: loop for [Type] [ID] equip [Val] to [Val] begin", "fix": "Check your syntax.", "suggestion": "loop for hp count equip 1 to 5 begin"}
                print(f"[PARSER] Line {tok_line}: Valid FOR loop structure.")
                i += 9
                continue
            
            elif i+1 < len(tokens) and tokens[i+1][1] == 'while':
                if i+5 >= len(tokens) or tokens[i+2][0] != 'ID' or tokens[i+3][0] != 'COMPARE_OP' or not tokens[i+4][0].startswith('LITERAL') or tokens[i+5][0] != 'SCOPE_IN':
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed while loop.", "rule": "Requires: loop while [ID] [Compare] [Val] begin", "fix": "Check your syntax.", "suggestion": "loop while bossHealth greater 0 begin"}
                print(f"[PARSER] Line {tok_line}: Valid WHILE loop structure.")
                i += 6
                continue

        if tok_type == 'LOOP_TYPE' and tok_val == 'do':
            if i+1 >= len(tokens) or tokens[i+1][0] != 'SCOPE_IN':
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Malformed do loop.", "rule": "Requires: do begin", "fix": "Add 'begin'.", "suggestion": "do begin"}
            print(f"[PARSER] Line {tok_line}: Valid DO loop start.")
            i += 2
            continue

        # --- STANDARD ASSIGNMENTS ---
        if tok_type == 'DATATYPE':
            if i + 1 >= len(tokens) or tokens[i+1][0] != 'ID':
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing variable name.", "rule": "An identifier must follow the data type.", "fix": "Add a valid name after the type.", "suggestion": f"{tok_val} myVar equip 100 done"}
            if i + 2 >= len(tokens) or tokens[i+2][0] != 'ASSIGN':
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing 'equip' operator.", "rule": "You must use 'equip' to assign a value.", "fix": "Add 'equip' after the variable name.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip 100 done"}
            if i + 3 >= len(tokens) or not tokens[i+3][0].startswith('LITERAL'):
                return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing assignment value.", "rule": "You must provide a value after 'equip'.", "fix": "Add a number or text string.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip 100 done"}

            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if i + 5 >= len(tokens) or not tokens[i+5][0].startswith('LITERAL'):
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing second value for math operation.", "rule": "Math operators require a value on both sides.", "fix": "Add a number after the operator.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} plus 50 done"}
                next_idx = i + 6
                if next_idx < len(tokens) and tokens[next_idx][0] == 'SCOPE_OUT': next_idx += 1
                if next_idx >= len(tokens) or tokens[next_idx][0] != 'DELIM':
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing delimiter or punctuation.", "rule": "Every statement must end with 'done'.", "fix": "Add 'done' at the end.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} plus 50 done"}
                print(f"[PARSER] Line {tok_line}: Math structure valid.")
                i = next_idx + 1 
            else:
                next_idx = i + 4
                if next_idx < len(tokens) and tokens[next_idx][0] == 'SCOPE_OUT': next_idx += 1
                if next_idx >= len(tokens) or tokens[next_idx][0] != 'DELIM':
                    if next_idx < len(tokens):
                         return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": f"Unexpected token '{tokens[next_idx][1]}' before 'done'.", "rule": "Standard assignments require exactly: [Type] [Name] [equip] [Value] [done].", "fix": "Remove the extra words.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} done"}
                    return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": "Missing delimiter or punctuation.", "rule": "Every statement must end with 'done'.", "fix": "Add 'done' at the end.", "suggestion": f"{tok_val} {tokens[i+1][1]} equip {tokens[i+3][1]} done"}
                print(f"[PARSER] Line {tok_line}: Standard structure valid.")
                i = next_idx + 1 
        else:
            return False, {"type": "SYNTAX ERROR", "line": tok_line, "reason": f"Incorrect keyword usage: '{tok_val}'.", "rule": "Statements must begin with a valid DataType, Loop, Skill, or Scope.", "fix": "Start the line with a valid declaration keyword.", "suggestion": "hp playerHealth equip 100 done"}

    print("Syntax Analysis Complete.")
    return True, {}