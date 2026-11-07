"""Public, read-only HTTPS refresh. Records failures without inventing stock."""
import concurrent.futures
import csv
import datetime
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import requests

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / 'hardware/v4/evidence/phase5-5-sourcing'
EXTRA = {
    'L2-Coilank': 'https://www.lcsc.com/product-detail/C49261457.html',
    'L3-Bourns': 'https://www.lcsc.com/product-detail/C3223092.html',
    'R32-Viking': 'https://www.lcsc.com/product-detail/C2681601.html',
    'R33-RESI': 'https://www.lcsc.com/product-detail/C52677569.html',
    'R60-16k': 'https://www.lcsc.com/product-detail/C326732.html',
    'C39-exact': 'https://www.lcsc.com/product-detail/C415530.html',
    'C63-exact': 'https://www.lcsc.com/product-detail/C106856.html',
    'D1-exact': 'https://www.lcsc.com/product-detail/C668891.html',
    'U1-H4X': 'https://www.lcsc.com/product-detail/C41349510.html',
    'J2-exact': 'https://www.lcsc.com/product-detail/C561764.html',
    'J3-exact': 'https://www.lcsc.com/product-detail/C17189968.html',
    'H03-exact': 'https://www.lcsc.com/product-detail/C17689101.html',
    'R5-27k': 'https://www.lcsc.com/product-detail/C114533.html',
    'R5-13k7': 'https://www.lcsc.com/product-detail/C274361.html',
    'R5-8k2': 'https://www.lcsc.com/product-detail/C114545.html',
    'R6-exact': 'https://www.lcsc.com/product-detail/C114538.html',
    'R23-exact': 'https://www.lcsc.com/product-detail/C137929.html',
    'J1-TME': 'https://www.tme.eu/en/details/mx-105313-1102/raster-signal-connectors-2-50mm/molex/105313-1102/',
    'L1-TME': 'https://www.tme.eu/en/details/dr125-2r2-r/inductors/eaton-electronics/',
    'R12-TME-HP': 'https://www.tme.eu/en/details/crcw12062r00fkeahp/smd-resistors/vishay/',
    'C32-TDK': 'https://www.tme.eu/en/details/c2012x7r1h225kac/mlcc-smd-capacitors/tdk/c2012x7r1h225k125ac/',
    'coilank-drawing': 'https://datasheet.lcsc.com/lcsc/2505091635_Coilank-AAPS252010M1R0F_C48783469.pdf',
    'coilank-drawing-legacy': 'https://datasheet.lcsc.com/datasheet/pdf/db0306ba92d8c07b239ddfd67f0cd388.pdf',
    'RESI-drawing': 'https://atta.szlcsc.com/upload/public/pdf/source/20231218/EBECA0901342DCBDB0ABFC8C8F9AFCF5.pdf',
}

def main():
    dest = EV / 'live-http'
    dest.mkdir(exist_ok=False)
    rows = list(csv.DictReader((EV / 'entry-sourcing/SHOPPING_LIST_BY_SUPPLIER.csv').open(encoding='utf-8-sig')))
    urls = {r['group_id']: r['direct_url'] for r in rows if r['supplier'] in ('LCSC', 'TME')}
    urls.update(EXTRA)
    def fetch(item):
        key, url = item
        assert urlparse(url).hostname in ('www.lcsc.com', 'www.tme.eu', 'datasheet.lcsc.com', 'atta.szlcsc.com')
        result = dict(id=key, url=url, observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), stock_confirmed=False)
        try:
            response = requests.get(url, timeout=18)
            result.update(http_status=response.status_code, final_url=response.url, headers=dict(response.headers))
            suffix = '.pdf' if response.content.startswith(b'%PDF') else '.html'
            (dest / (key + suffix)).write_bytes(response.content)
            result.update(bytes=len(response.content), content_file=key+suffix)
            if response.status_code != 200:
                result['status'] = 'HTTP_FAILURE_NO_STOCK_VERIFICATION'
            elif suffix == '.pdf':
                result['status'] = 'MANUFACTURER_PDF_RETRIEVED'
            else:
                result['status'] = 'HTTP200_REQUIRES_CONTENT_REVIEW_NOT_STOCK_CONFIRMATION'
        except requests.RequestException as exc:
            result.update(status='NETWORK_FAILURE_NO_STOCK_VERIFICATION', error=str(exc))
        print(key, result['status'], flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(fetch, urls.items()))
    (dest / 'ledger.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Completed', len(result), 'public GET requests')

if __name__ == '__main__':
    main()
