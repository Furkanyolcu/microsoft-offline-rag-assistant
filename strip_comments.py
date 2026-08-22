import os
import tokenize
import io

def remove_comments(source):
    result = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    last_lineno = -1
    last_col = 0
    
    for tok in tokens:
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            result.append(" " * (start_col - last_col))
            
        if token_type == tokenize.COMMENT:
            pass # ignore comment
        elif token_type == tokenize.STRING and token_string.startswith(('"""', "'''")):
            pass # ignore docstrings
        else:
            result.append(token_string)
            
        last_lineno = end_line
        last_col = end_col
        
    return "".join(result)

def main():
    directory = "."
    for root, dirs, files in os.walk(directory):
        if "venv" in root or ".venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "strip_comments.py":
                filepath = os.path.join(root, file)
                print(f"Stripping {filepath}")
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    new_content = remove_comments(content)
                    
                    # Remove empty lines
                    new_lines = [line for line in new_content.split('\n') if line.strip() != '']
                    final_content = '\n'.join(new_lines) + '\n'
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(final_content)
                except Exception as e:
                    print(f"Failed to strip {filepath}: {e}")

if __name__ == "__main__":
    main()
