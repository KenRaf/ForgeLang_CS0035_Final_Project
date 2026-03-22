import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    tokens = []
    lines = source_code.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        # Regex to match strings in quotes, alphanumeric words, or single symbols
        token_pattern = r'".*?"|\w+|[^\w\s]'
        raw_tokens = re.findall(token_pattern, line)
        
        for word in raw_tokens:
            w_lower = word.lower() 
            
            # --- DATA TYPES ---
            # hp: Represents standard integer (e.g., Health Points -> int)
            # xp: Represents standard integer (e.g., Experience Points -> int)
            # status: Represents small integer/boolean (e.g., 1 or 0 -> bool/short)
            # lore: Represents text strings (e.g., "Sword of Light" -> string)
            if w_lower in ['hp', 'lore', 'xp', 'status']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> DATATYPE")
                tokens.append(('DATATYPE', word, line_num))
            
            # --- SCOPE MANAGEMENT ---
            # begin: Represents the opening of a scope block (like '{' in C++)
            elif w_lower == 'begin':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> SCOPE_IN")
                tokens.append(('SCOPE_IN', word, line_num))
            # close: Represents the closing of a scope block (like '}' in C++)
            elif w_lower == 'close':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> SCOPE_OUT")
                tokens.append(('SCOPE_OUT', word, line_num))
            
            # --- ASSIGNMENT & DELIMITERS ---
            # equip: Represents the assignment operator (like '=' in C++)
            elif w_lower == 'equip':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> ASSIGN")
                tokens.append(('ASSIGN', word, line_num))
            # done: Represents the end of a statement (like ';' in C++)
            elif w_lower == 'done':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> DELIM")
                tokens.append(('DELIM', word, line_num))
            
            # --- MATH OPERATIONS ---
            # plus (+), minus (-), times (*)
            elif w_lower in ['plus', 'minus', 'times']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> MATH_OP")
                tokens.append(('MATH_OP', word, line_num))
                
            # --- FUNCTIONS & LOOPS ---
            # skill: Represents function declaration (like 'void' or 'function' keyword)
            elif w_lower == 'skill':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> FUNC_DECL")
                tokens.append(('FUNC_DECL', word, line_num))
            # cast: Represents calling a function (e.g., executing the skill)
            elif w_lower == 'cast':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> FUNC_CALL")
                tokens.append(('FUNC_CALL', word, line_num))
            # loop: Represents the start of a loop statement keyword
            elif w_lower == 'loop':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> LOOP_START")
                tokens.append(('LOOP_START', word, line_num))
            # for, while, do: The specific type of loop being executed
            elif w_lower in ['for', 'while', 'do']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> LOOP_TYPE")
                tokens.append(('LOOP_TYPE', word, line_num))
            # to: Range operator used in for-loops (e.g., 1 'to' 5)
            elif w_lower == 'to':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> TO_OP")
                tokens.append(('TO', word, line_num))
            # greater (>), less (<), equals (==): Relational operators for while loops
            elif w_lower in ['greater', 'less', 'equals']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> COMPARE_OP")
                tokens.append(('COMPARE_OP', word, line_num))
                
            # --- OUTPUT COMMAND ---
            # spawn: Represents the print command (like 'cout' in C++ or 'print' in Python)
            elif w_lower == 'spawn':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> OUTPUT")
                tokens.append(('OUTPUT', word, line_num))
            # ------------------------------
            
            # --- LITERALS & IDENTIFIERS ---
            elif word.startswith('"') and word.endswith('"'):
                print(f"[LEXER] Line {line_num}: Found {word} -> STRING")
                tokens.append(('LITERAL_STR', word, line_num))
            elif word.isdigit():
                print(f"[LEXER] Line {line_num}: Found '{word}' -> NUMBER")
                tokens.append(('LITERAL_NUM', word, line_num))
            elif word.isalnum():
                if word[0].isdigit():
                    return False, {"type": "LEXICAL ERROR", "line": line_num, "reason": f"Malformed identifier '{word}'.", "rule": "Variables cannot start with a number.", "fix": "Remove the numbers.", "suggestion": f"hp {word.lstrip('0123456789')} equip 400 done"}
                print(f"[LEXER] Line {line_num}: Found '{word}' -> IDENTIFIER")
                tokens.append(('ID', word, line_num))
            else:
                return False, {"type": "LEXICAL ERROR", "line": line_num, "reason": f"Illegal character '{word}'.", "rule": "Symbols not in the alphabet are rejected.", "fix": "Remove it.", "suggestion": "Use letters/numbers."}
            
    print("Lexical Analysis Complete.")
    return True, tokens