def run_parser(tokens):
    print("\n--- STARTING SYNTAX ANALYSIS ---")
    i = 0
    while i < len(tokens):
        if tokens[i][0] in ['SCOPE_IN', 'SCOPE_OUT']:
            print(f"[PARSER] Valid scope modifier found.")
            i += 1
            continue
            
        if tokens[i][0] == 'DATATYPE':
            has_math = False
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                has_math = True
            
            if has_math:
                print("[PARSER] Evaluating Math Rule...")
                # Allow 'close' at the end of math
                if i + 7 < len(tokens) and tokens[i+6][0] == 'SCOPE_OUT' and tokens[i+7][0] == 'DELIM':
                    print("[PARSER] Math structure + Scope Out matches perfectly.")
                    i += 8
                elif i + 6 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+6][0] == 'DELIM':
                    print("[PARSER] Math structure matches expected rule perfectly.")
                    i += 7
                else:
                    print("[PARSER] SYNTAX ERROR in math operation.")
                    return False
            else:
                print("[PARSER] Evaluating Standard Rule...")
                # Allow 'close' at the end of standard assignment
                if i + 5 < len(tokens) and tokens[i+4][0] == 'SCOPE_OUT' and tokens[i+5][0] == 'DELIM':
                    print("[PARSER] Standard structure + Scope Out matches perfectly.")
                    i += 6
                elif i + 4 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+4][0] == 'DELIM':
                    print("[PARSER] Standard structure matches expected rule perfectly.")
                    i += 5
                else:
                    print("[PARSER] SYNTAX ERROR: Incomplete statement.")
                    return False
        else:
            i += 1
            
    print("Syntax Analysis Complete. No structural errors.")
    return True