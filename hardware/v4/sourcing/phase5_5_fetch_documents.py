"""Fetch public manufacturer drawings into evidence; no CAD imports or writes."""
from pathlib import Path
import requests

EV = Path(__file__).resolve().parents[1] / 'evidence/phase5-5-sourcing'
URLS = {
    'bourns-srp5050fa.pdf': 'https://www.bourns.com/docs/product-datasheets/srp5050fa.pdf',
    'coilank-aaps-f.pdf': 'https://datasheet.lcsc.com/datasheet/pdf/db0306ba92d8c07b239ddfd67f0cd388.pdf?productCode=C48783469',
}

def main():
    for name, url in URLS.items():
        dest = EV / name
        if dest.exists():
            continue
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        assert response.content.startswith(b'%PDF'), (name, response.headers.get('Content-Type'))
        dest.write_bytes(response.content)
        print(name, len(response.content))

if __name__ == '__main__':
    main()
