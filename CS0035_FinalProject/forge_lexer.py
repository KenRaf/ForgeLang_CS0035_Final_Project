import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    
    tokens = []
    # Split the code into individual lines to track numbers
    lines = source_code.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        token_pattern = r'".*?"|\w+|[^\w\s]'
        raw_tokens = re.findall(token_pattern, line)
        
        for word in raw_tokens:
            w_lower = word.lower() 
            
            if w_lower in ['hp', 'lore', 'xp', 'status']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> DATATYPE")
                tokens.append(('DATATYPE', word, line_num))
            elif w_lower == 'begin':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> SCOPE_IN")
                tokens.append(('SCOPE_IN', word, line_num))
            elif w_lower == 'close':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> SCOPE_OUT")
                tokens.append(('SCOPE_OUT', word, line_num))
            elif w_lower == 'spawn':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> OUTPUT")
                tokens.append(('OUTPUT', word, line_num))
            elif w_lower == 'equip':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> ASSIGN")
                tokens.append(('ASSIGN', word, line_num))
            elif w_lower == 'done':
                print(f"[LEXER] Line {line_num}: Found '{word}' -> DELIM")
                tokens.append(('DELIM', word, line_num))
            elif w_lower in ['plus', 'minus', 'times']:
                print(f"[LEXER] Line {line_num}: Found '{word}' -> MATH_OP")
                tokens.append(('MATH_OP', word, line_num))
            elif word.startswith('"') and word.endswith('"'):
                print(f"[LEXER] Line {line_num}: Found {word} -> STRING")
                tokens.append(('LITERAL_STR', word, line_num))
            elif word.isdigit():
                print(f"[LEXER] Line {line_num}: Found '{word}' -> NUMBER")
                tokens.append(('LITERAL_NUM', word, line_num))
            elif word.isalnum():
                if word[0].isdigit():
                    return False, {
                        "type": "LEXICAL ERROR", "line": line_num,
                        "reason": f"Malformed identifier '{word}'.",
                        "rule": "Variables cannot start with a number.",
                        "fix": "Remove the numbers from the beginning of the variable name.",
                        "suggestion": f"hp {word.lstrip('0123456789')} equip 400 done"
                    }
                print(f"[LEXER] Line {line_num}: Found '{word}' -> IDENTIFIER")
                tokens.append(('ID', word, line_num))
            else:
                return False, {
                    "type": "LEXICAL ERROR", "line": line_num,
                    "reason": f"Illegal character '{word}' detected.",
                    "rule": "Symbols not in the language's alphabet are strictly rejected.",
                    "fix": "Remove the invalid symbol.",
                    "suggestion": "Stick to letters, numbers, and allowed ForgeLang keywords."
                }
            
    print("Lexical Analysis Complete.")
    return True, tokens