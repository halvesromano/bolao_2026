
import os

file_path = r'c:\Users\m753051\code\bolao_2026\core\templates\core\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic string
bad_syntax = '{% if r==current_round %}'
good_syntax = '{% if r == current_round %}'

if bad_syntax in content:
    new_content = content.replace(bad_syntax, good_syntax)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Fixed syntax error in {file_path}")
else:
    print(f"Syntax error not found. Searching for variations...")
    # debug what is there
    start = content.find('{% if r')
    if start != -1:
        end = content.find('%}', start) + 2
        print(f"Found nearby tag: {content[start:end]}")
