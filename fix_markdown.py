import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the Baseline Card rendering issue caused by Markdown interpreting 4+ spaces as a code block.
def fix_indent(match):
    lines = match.group(0).split('\n')
    fixed_lines = []
    for line in lines:
        fixed_lines.append(line.lstrip())
    return '\n'.join(fixed_lines)

text = re.sub(r'<div class="baseline-card">.*?</div>\s*</div>\s*</div>\s*</div>', fix_indent, text, flags=re.DOTALL)
text = re.sub(r'<div class="swipe-container">.*?</div>', fix_indent, text, flags=re.DOTALL)
text = re.sub(r'<div class="asset-card">.*?</div>', fix_indent, text, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
