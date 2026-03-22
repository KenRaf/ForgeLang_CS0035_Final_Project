import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    source_code = source_code.lower()
    
    # NEW: The regex now catches illegal symbols so we can flag them
    token_pattern = r'".*?"|\w+|[^\w\s]'
    raw_tokens = re.findall(token_pattern, source_code)
    
    tokens = []
    for word in raw_tokens:
        if word in ['hp', 'lore', 'xp', 'status']:
            tokens.append(('DATATYPE', word))
        elif word == 'begin':
            tokens.append(('SCOPE_IN', word))
        elif word == 'close':
            tokens.append(('SCOPE_OUT', word))
        elif word == 'spawn':
            tokens.append(('OUTPUT', word))
        elif word == 'equip':
            tokens.append(('ASSIGN', word))
        elif word == 'done':
            tokens.append(('DELIM', word))
        elif word in ['plus', 'minus', 'times']:
            tokens.append(('MATH_OP', word))
        elif word.startswith('"') and word.endswith('"'):
            tokens.append(('LITERAL_STR', word))
        elif word.isdigit():
            tokens.append(('LITERAL_NUM', word))
        elif word.isalnum():
            # NEW: Lexical Error check for Malformed Identifiers!
            if word[0].isdigit():
                return False, {
                    "type": "LEXICAL ERROR",
                    "reason": f"Malformed identifier '{word}'.",
                    "rule": "Identifiers cannot start with a number or invalid character.",
                    "fix": "Remove the numbers from the beginning of the variable name.",
                    "suggestion": f"hp {word.lstrip('0123456789')} equip 400 done"
                }
            tokens.append(('ID', word))
        else:
            # NEW: Lexical Error check for Illegal Characters!
            return False, {
                "type": "LEXICAL ERROR",
                "reason": f"Illegal character '{word}' detected.",
                "rule": "Symbols not in the language's alphabet are strictly rejected.",
                "fix": "Remove the invalid symbol.",
                "suggestion": "Stick to letters, numbers, and allowed ForgeLang keywords."
            }
            
    print("Lexical Analysis Complete.")
    return True, tokens