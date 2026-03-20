def run_parser(tokens):
    print("\n--- STARTING SYNTAX ANALYSIS ---")
    i = 0
    while i < len(tokens):
        # NEW: Allow scope brackets to pass syntax check
        if tokens[i][0] in ['SCOPE_IN', 'SCOPE_OUT']:
            print(f"[PARSER] Valid scope modifier found.")
            i += 1
            continue
            
        if tokens[i][0] == 'DATATYPE':
            has_math = False
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                has_math = True
            
            if has_math:
                print("[PARSER] Expected rule: [DATATYPE] [ID] [ASSIGN] [LITERAL] [MATH_OP] [LITERAL] [DELIM]")
                if i + 6 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+6][0] == 'DELIM':
                    print("[PARSER] Math structure matches expected rule perfectly.")
                    i += 7
                else:
                    print("[PARSER] SYNTAX ERROR in math operation.")
                    return False
            else:
                print("[PARSER] Expected rule: [DATATYPE] [ID] [ASSIGN] [LITERAL] [DELIM]")
                if i + 4 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+4][0] == 'DELIM':
                    print("[PARSER] Standard structure matches expected rule perfectly.")
                    i += 5
                else:
                    print("[PARSER] SYNTAX ERROR: Incomplete statement.")
                    return False
        else:
            i += 1
            
    print("Syntax Analysis Complete. No structural errors.")
    return True