def run_semantics(tokens):
    print("\n--- STARTING SEMANTIC ANALYSIS ---")
    symbol_table = {}
    i = 0
    
    while i < len(tokens):
        if tokens[i][0] == 'DATATYPE':
            dtype = tokens[i][1]
            var_name = tokens[i+1][1]
            
            # --- MATH LOGIC ---
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                if dtype not in ['hp', 'xp']:
                    print(f"[SEMANTICS] FATAL ERROR: Cannot perform math on non-numeric '{dtype}'.")
                    return False
                
                val1 = int(tokens[i+3][1])
                op = tokens[i+4][1]
                val2 = int(tokens[i+5][1])
                
                if op == 'plus': final_val = val1 + val2
                elif op == 'minus': final_val = val1 - val2
                elif op == 'times': final_val = val1 * val2
                
                print(f"[SEMANTICS] Math recognized. Calculating: {val1} {op} {val2} = {final_val}")
                symbol_table[var_name] = {'type': dtype, 'value': final_val}
                i += 7
                
            # --- STANDARD ASSIGNMENT LOGIC ---
            else:
                lit_type = tokens[i+3][0]
                raw_val = tokens[i+3][1]
                
                if dtype == 'hp' and lit_type != 'LITERAL_NUM':
                    print(f"[SEMANTICS] FATAL ERROR: Cannot equip STRING into numeric 'hp' stat.")
                    return False
                if dtype == 'lore' and lit_type != 'LITERAL_STR':
                    print(f"[SEMANTICS] FATAL ERROR: Cannot equip NUMBER into text 'lore' stat.")
                    return False
                    
                val = raw_val.replace('"', '')
                print(f"[SEMANTICS] Types match. Binding '{var_name}' to Symbol Table.")
                symbol_table[var_name] = {'type': dtype, 'value': val}
                i += 5
        else:
            i += 1
            
    # --- LIVE INVENTORY HUD ---
    print("\n" + "="*45)
    print(f"||{'LIVE INVENTORY (SYMBOL TABLE)':^41}||")
    print("="*45)
    print(f"|| {'IDENTIFIER':<15} | {'TYPE':<7} | {'VALUE':<10} ||")
    print("-" * 45)
    for var, data in symbol_table.items():
        print(f"|| {var:<15} | {data['type']:<7} | {data['value']:<10} ||")
    print("="*45 + "\n")
    
    return True