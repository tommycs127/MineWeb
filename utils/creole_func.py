from creole import creole2html as c2h
from creole.shared.example_macros import code
import re

creole_ = ''

def table_of_contents(text):
    global creole_
    text = creole_.split('\n')
    toc = []
    for i in range(len(text)):
        result = re.search('={1,6}\ (\w|\ |\?)+', text[i])
        if result:
            intent, header = result.group(0).split(' ', 1)
            intent = intent.replace('=', '#')
            link = f'[[#{header.replace(" ", "_")}|{header}]]'
            toc.append(f'{intent} {link}')
    return '<table><tr><td>' + c2h('\n'.join(toc)) + '</td></tr></table>'
    
def toRead(s, indent=0):
    for r in re.finditer("\[{2}.[^\[\]\|]*\]{2}", s):
        title = r.group(0)[2:-2]
        s = s.replace(r.group(0), f'[[{"../"*indent}read/{title}|{title}]]')
    return s

def creole2html(creole, to_read=0):
    global creole_
    if to_read:
        creole = toRead(creole, to_read)
    creole_ = creole
    return c2h(creole, macros={"code": code})
    
if __name__ == '__main__':
    print(creole2html('**PCCU** is an //university// in __Taiwan__.'))