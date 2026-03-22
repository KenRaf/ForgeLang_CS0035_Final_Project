import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    
    # We use a pattern to catch words, strings, or stray illegal symbols
    token_pattern = r'".*?"|\w+|[^\w\s]'
    raw_tokens = re.findall(token_pattern, source_code)
    
    tokens = []
    for word in raw_tokens:
        w_lower = word.lower() # We check logic in lowercase, but keep the original 'word' for the UI
        
        if w_lower in ['hp', 'lore', 'xp', 'status']:
            tokens.append(('DATATYPE', word))
        elif w_lower == 'begin':
            tokens.append(('SCOPE_IN', word))
        elif w_lower == 'close':
            tokens.append(('SCOPE_OUT', word))
        elif w_lower == 'spawn':
            tokens.append(('OUTPUT', word))
        elif w_lower == 'equip':
            tokens.append(('ASSIGN', word))
        elif w_lower == 'done':
            tokens.append(('DELIM', word))
        elif w_lower in ['plus', 'minus', 'times']:
            tokens.append(('MATH_OP', word))
        elif word.startswith('"') and word.endswith('"'):
            tokens.append(('LITERAL_STR', word))
        elif word.isdigit():
            tokens.append(('LITERAL_NUM', word))
        elif word.isalnum():
            # STRICT RULE: Variables CANNOT start with a number!
            if word[0].isdigit():
                return False, {
                    "type": "LEXICAL ERROR",
                    "reason": f"Malformed identifier '{word}'.",
                    "rule": "Variables cannot start with a number.",
                    "fix": "Remove the numbers from the beginning of the variable name.",
                    "suggestion": f"hp {word.lstrip('0123456789')} equip 400 done"
                }
            tokens.append(('ID', word))
        else:
            # STRICT RULE: No illegal characters (!, @, #, etc.)
            return False, {
                "type": "LEXICAL ERROR",
                "reason": f"Illegal character '{word}' detected.",
                "rule": "Symbols not in the language's alphabet are strictly rejected.",
                "fix": "Remove the invalid symbol.",
                "suggestion": "Stick to letters, numbers, and allowed ForgeLang keywords."
            }
            
    print("Lexical Analysis Complete.")
    return True, tokens