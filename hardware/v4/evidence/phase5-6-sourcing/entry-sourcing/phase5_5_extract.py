"""Summarize public-cache research for manual review, never infer absent stock."""
import json
from pathlib import Path
import re
import sys

EV = Path(__file__).resolve().parents[1] / 'evidence/phase5-5-sourcing'

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    records = []
    for path in sorted(EV.glob('research-*.json')):
        raw = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(raw, str):
            continue
        for block in raw.split('--------------------------------------------------------------------------------'):
            head = re.search(r'^([^\n]+) \((https://[^\n]+)\)', block.strip())
            if not head:
                continue
            title, url = head.groups()
            if not any(h in url for h in ['lcsc.com', 'tme.eu', 'tme.com']):
                continue
            text = re.sub(r'(?m)^L\d+(?:@P\d+(?:-\d+)?)?: ?', '', block)
            text = re.sub(r'\ue200cite\ue202.*?\ue201', '', text)
            age = re.search(r'Crawled: ([^;\n]+)', text)
            stock = re.search(r'(?:In-Stock:|En stock:|Vorrätig:|En stock :|Em estoque:)\s*([\d,]+)', text, re.I)
            tme = re.search(r'([\d, ]+) in TME stock', text)
            absent = bool(re.search(r'Out of Stock|Agotado|Brak w magazynie|Nicht auf Lager', text, re.I))
            terms = re.search(r'(?:Minimum:|Mínimo:)\s*(\d+)\s*(?:Multiple:|Múltiplo:|Vielfaches:)\s*(\d+)', text)
            prices = re.findall(r'(?m)^(\d[\d,]*)\+\s*\|\s*\$\s*([\d.]+)', text)
            prices += re.findall(r'Net price for quantities from (\d+) pcs - ([\d.]+) USD', text)
            if not (stock or tme or absent or terms or prices):
                continue
            records.append(dict(title=title, url=url, evidence=path.name,
                                cache_age=age.group(1) if age else 'unspecified',
                                stock=int(re.sub(r'\D','',(stock or tme).group(1))) if stock or tme else (0 if absent else None),
                                terms=list(map(int,terms.groups())) if terms else None,
                                prices=prices, out_of_stock=absent,
                                direct=bool(re.search('Source: (?:find|open|click)', block)),
                                reference_only='Reference Only' in text or 'Tylko do wglądu' in text))
    (EV / 'cache-observations.json').write_text(json.dumps(records, indent=2)+'\n')
    for r in records:
        if any(x in r['title'] for x in ['AAPS0530','SRP5050FA-6R8','PTFR0402Q','ARG02BTC3162','BZT52C12-TP','C2012X7R1H225','RT0603BRD0716','GRM155R71H333','105313','105307','RC0805FR-0713','RC0805FR-0727','RC0402FR-078K2']):
            print(r['evidence'],r['title'].split('|')[0][:35],r['stock'],r['terms'],r['prices'][:2],r['cache_age'])

if __name__ == '__main__':
    main()
