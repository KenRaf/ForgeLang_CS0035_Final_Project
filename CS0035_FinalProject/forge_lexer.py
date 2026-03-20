import re

def run_lexer(source_code):
    print("\n--- STARTING LEXICAL ANALYSIS ---")
    source_code = source_code.lower()
    token_pattern = r'".*?"|\w+'
    raw_tokens = re.findall(token_pattern, source_code)
    
    tokens = []
    for word in raw_tokens:
        if word in ['hp', 'lore', 'xp', 'status']:
            print(f"[LEXER] Found '{word}' -> Identified as DATATYPE")
            tokens.append(('DATATYPE', word))
        elif word == 'begin':
            print(f"[LEXER] Found '{word}' -> Identified as SCOPE_IN")
            tokens.append(('SCOPE_IN', word))
        elif word == 'close':  # <--- UPDATED KEYWORD
            print(f"[LEXER] Found '{word}' -> Identified as SCOPE_OUT")
            tokens.append(('SCOPE_OUT', word))
        elif word == 'spawn':
            print(f"[LEXER] Found '{word}' -> Identified as OUTPUT_KEYWORD")
            tokens.append(('OUTPUT', word))
        elif word == 'equip':
            print(f"[LEXER] Found '{word}' -> Identified as ASSIGN_OPERATOR")
            tokens.append(('ASSIGN', word))
        elif word == 'done':
            print(f"[LEXER] Found '{word}' -> Identified as DELIMITER")
            tokens.append(('DELIM', word))
        elif word in ['plus', 'minus', 'times']:
            print(f"[LEXER] Found '{word}' -> Identified as MATH_OPERATOR")
            tokens.append(('MATH_OP', word))
        elif word.startswith('"') and word.endswith('"'):
            print(f"[LEXER] Found {word} -> Identified as STRING_LITERAL")
            tokens.append(('LITERAL_STR', word))
        elif word.isdigit():
            print(f"[LEXER] Found '{word}' -> Identified as NUMERIC_LITERAL")
            tokens.append(('LITERAL_NUM', word))
        elif word.isalnum(): 
            print(f"[LEXER] Found '{word}' -> Identified as IDENTIFIER")
            tokens.append(('ID', word))
        else:
            print(f"[LEXER] Found '{word}' -> UNKNOWN TOKEN!")
            tokens.append(('UNKNOWN', word))
            
    print("Lexical Analysis Complete.")
    return tokens