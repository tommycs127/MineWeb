import difflib
import re

def genDiffHTML(a, b):
    pattern = '<(\/|\ )*((del)|(strong)|(i)|(b)|(u)|\ *)*(\/|\ )*>'
    a = re.sub(pattern, '', a)
    b = re.sub(pattern, '', b)
    d = list(difflib.ndiff(a, b))
    html = ''
    for i in d:
        status, char = i[:2], i[2]
        print(status, char)
        if char in ['~', '*']:
            char = '{{{' + char + '}}}'
        elif char in ['', '\n']:
            pass
        else:
            if status == '- ':
                html += f'~~{char}~~'
            elif status == '+ ':
                html += f'**{char}**'
            else:
                html += char
            
    return html