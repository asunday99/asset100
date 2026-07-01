import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I will find all instances of st.markdown(f''' or st.markdown(''' that contain HTML tags
# and strip leading whitespace from every line inside them.
def fix_markdown_indentation(match):
    prefix = match.group(1)
    content = match.group(2)
    suffix = match.group(3)
    
    lines = content.split('\n')
    stripped_lines = [line.lstrip() for line in lines]
    new_content = '\n'.join(stripped_lines)
    
    return prefix + new_content + suffix

# Match st.markdown(..., unsafe_allow_html=True) blocks
# The regex looks for st.markdown( followed by f''' or ''' or f\"\"\" or \"\"\"
# Then non-greedy content
# Then the closing quotes and , unsafe_allow_html=True)
pattern = r"(st\.markdown\([f]?[']{3}|\"{3})(.*?)((?:[']{3}|\"{3})\s*,\s*unsafe_allow_html\s*=\s*True\))"
text = re.sub(pattern, fix_markdown_indentation, text, flags=re.DOTALL)

# Also fix the cards_html += f''' blocks
pattern2 = r"(cards_html \+= [f]?[']{3}|\"{3})(.*?)((?:[']{3}|\"{3}))"
text = re.sub(pattern2, fix_markdown_indentation, text, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
