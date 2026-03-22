def run_parser(tokens):
    print("\n--- STARTING SYNTAX ANALYSIS ---")
    i = 0
    while i < len(tokens):
        if tokens[i][0] in ['SCOPE_IN', 'SCOPE_OUT']:
            i += 1
            continue
            
        if tokens[i][0] == 'DATATYPE':
            has_math = False
            if i + 4 < len(tokens) and tokens[i+4][0] == 'MATH_OP':
                has_math = True
            
            if has_math:
                if i + 7 < len(tokens) and tokens[i+6][0] == 'SCOPE_OUT' and tokens[i+7][0] == 'DELIM':
                    i += 8
                elif i + 6 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+6][0] == 'DELIM':
                    i += 7
                else:
                    return False, {
                        "type": "SYNTAX ERROR",
                        "reason": "Malformed control structure in math operation.",
                        "rule": "Math structures require: [DataType] [ID] [equip] [Value] [MathOp] [Value] [done]",
                        "fix": "Ensure you have all required operators and a 'done' delimiter.",
                        "suggestion": "hp bossHealth equip 100 plus 50 done"
                    }
            else:
                if i + 5 < len(tokens) and tokens[i+4][0] == 'SCOPE_OUT' and tokens[i+5][0] == 'DELIM':
                    i += 6
                elif i + 4 < len(tokens) and tokens[i+1][0] == 'ID' and tokens[i+4][0] == 'DELIM':
                    i += 5
                else:
                    # Specific Syntax Error check for missing delimiters
                    if i + 4 >= len(tokens) or tokens[i+4][0] != 'DELIM':
                        return False, {
                            "type": "SYNTAX ERROR",
                            "reason": "Missing delimiter or punctuation.",
                            "rule": "Every statement must end with the 'done' keyword.",
                            "fix": "Add 'done' at the end of your command.",
                            "suggestion": f"{tokens[i][1]} myVar equip 100 done"
                        }
                    return False, {
                        "type": "SYNTAX ERROR",
                        "reason": "Invalid structure or misplaced operator.",
                        "rule": "Standard assignments require: [DataType] [ID] [equip] [Value] [done]",
                        "fix": "Check the sequence of your words.",
                        "suggestion": "hp bossHealth equip 5000 done"
                    }
        else:
            # Specific Syntax Error check for incorrect keyword usage
            return False, {
                "type": "SYNTAX ERROR",
                "reason": f"Incorrect keyword usage: '{tokens[i][1]}'.",
                "rule": "Statements must begin with a valid DataType (hp, xp, lore) or Scope modifier (begin).",
                "fix": "Start the line with a valid declaration keyword.",
                "suggestion": "hp playerHealth equip 100 done"
            }
            
    print("Syntax Analysis Complete. No structural errors.")
    return True, {}