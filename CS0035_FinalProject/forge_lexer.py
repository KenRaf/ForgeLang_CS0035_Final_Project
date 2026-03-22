import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    
    token_pattern = r'".*?"|\w+|[^\w\s]'
    raw_tokens = re.findall(token_pattern, source_code)
    
    tokens = []
    for word in raw_tokens:
        w_lower = word.lower() 
        
        if w_lower in ['hp', 'lore', 'xp', 'status']:
            print(f"[LEXER] Found '{word}' -> Identified as DATATYPE")
            tokens.append(('DATATYPE', word))
        elif w_lower == 'begin':
            print(f"[LEXER] Found '{word}' -> Identified as SCOPE_IN")
            tokens.append(('SCOPE_IN', word))
        elif w_lower == 'close':
            print(f"[LEXER] Found '{word}' -> Identified as SCOPE_OUT")
            tokens.append(('SCOPE_OUT', word))
        elif w_lower == 'spawn':
            print(f"[LEXER] Found '{word}' -> Identified as OUTPUT_KEYWORD")
            tokens.append(('OUTPUT', word))
        elif w_lower == 'equip':
            print(f"[LEXER] Found '{word}' -> Identified as ASSIGN_OPERATOR")
            tokens.append(('ASSIGN', word))
        elif w_lower == 'done':
            print(f"[LEXER] Found '{word}' -> Identified as DELIMITER")
            tokens.append(('DELIM', word))
        elif w_lower in ['plus', 'minus', 'times']:
            print(f"[LEXER] Found '{word}' -> Identified as MATH_OPERATOR")
            tokens.append(('MATH_OP', word))
        elif word.startswith('"') and word.endswith('"'):
            print(f"[LEXER] Found {word} -> Identified as STRING_LITERAL")
            tokens.append(('LITERAL_STR', word))
        elif word.isdigit():
            print(f"[LEXER] Found '{word}' -> Identified as NUMERIC_LITERAL")
            tokens.append(('LITERAL_NUM', word))
        elif word.isalnum():
            if word[0].isdigit():
                return False, {
                    "type": "LEXICAL ERROR",
                    "reason": f"Malformed identifier '{word}'.",
                    "rule": "Variables cannot start with a number.",
                    "fix": "Remove the numbers from the beginning of the variable name.",
                    "suggestion": f"hp {word.lstrip('0123456789')} equip 400 done"
                }
            print(f"[LEXER] Found '{word}' -> Identified as IDENTIFIER")
            tokens.append(('ID', word))
        else:
            return False, {
                "type": "LEXICAL ERROR",
                "reason": f"Illegal character '{word}' detected.",
                "rule": "Symbols not in the language's alphabet are strictly rejected.",
                "fix": "Remove the invalid symbol.",
                "suggestion": "Stick to letters, numbers, and allowed ForgeLang keywords."
            }
            
    print("Lexical Analysis Complete.")
    return True, tokens