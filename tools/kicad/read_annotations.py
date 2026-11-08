"""Read-only extraction of field geometry absent from the Konnect read API."""
import json
import re
import sys
from pathlib import Path

TOKEN = re.compile(r'\s+|[()]|"(?:\\.|[^"\\])*"|[^()\s]+')

def read_tree(path):
    stack = []
    root = None
    for m in TOKEN.finditer(Path(path).read_text(encoding='utf-8-sig')):
        t = m.group()
        if t.isspace():
            continue
        if t == '(':
            a = []
            if stack:
                stack[-1].append(a)
            else:
                if root is not None:
                    raise ValueError('multiple roots')
                root = a
            stack.append(a)
        elif t == ')':
            stack.pop()
        else:
            if t.startswith('"'):
                t = re.sub(r'\\(.)', lambda m: {'n':'\n','t':'\t','r':'\r'}.get(m[1],m[1]), t[1:-1])
            stack[-1].append(t)
    if stack:
        raise ValueError('unbalanced tree')
    return root

def child(node, key, default=None):
    return next((n for n in node if isinstance(n,list) and n and n[0] == key), default)

def extract(path):
    result = {}
    for symbol in read_tree(path)[1:]:
        if not isinstance(symbol,list) or symbol[0] != 'symbol':
            continue
        fields = {}
        for p in symbol:
            if not isinstance(p,list) or p[0] != 'property':
                continue
            at = child(p,'at'); effects = child(p,'effects',[]); font = child(effects,'font',[])
            hide = child(p,'hide',child(effects,'hide'))
            fields[p[1]] = {'value':p[2], 'x':float(at[1]), 'y':float(at[2]), 'rotation':float(at[3]),
                            'size':child(font,'size',[None,'1.27','1.27'])[1:],
                            'justify':child(effects,'justify',[])[1:],
                            'visible':not ('hide' in p or 'hide' in effects or (hide and (len(hide)==1 or hide[1]=='yes')))}
        ref = fields['Reference']['value']; at = child(symbol,'at'); uid = child(symbol,'uuid')[1]
        result[ref] = {'uuid':uid,'x':float(at[1]),'y':float(at[2]),'rotation':float(at[3]),'fields':fields}
    return result

if __name__ == '__main__':
    data = extract(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'symbols':len(data),'visible_value_sizes':sorted({str(c['fields']['Value']['size']) for c in data.values() if c['fields'].get('Value',{}).get('visible')})}))
