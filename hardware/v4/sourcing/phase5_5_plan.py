"""Phase 5.5 proposal identities. All replacements await owner approval."""
import csv
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
EV=BASE.parent/'evidence/phase5-5-sourcing'
# id: proposed MPN, manufacturer, exact LCSC SKU, compatibility rationale
OVERRIDES={
 'P012':('CC0402KRX7R9BB333','Yageo','C106862','33nF +/-10% 50V X7R 0402; same soft-start function'),
 'P014':('CC0603KRX7R9BB333','Yageo','C106856','Owner-approved identity; supplier-only transfer'),
 'P016':('BZT52C12-TP','MCC','C668891','Exact SOD-123 zener retained'),
 'P021':('1053131102','Molex','C564339','Exact black/key-A, 2-position, tin, right-angle header'),
 'P022':('1053131103','Molex','C561764','Exact black/key-A, 3-position, tin, right-angle header'),
 'P023':('1053132102','Molex','C17189968','Exact natural/key-B, 2-position, tin, right-angle header'),
 'P027':('1053132103','Molex','C17412426','Exact natural/key-B, 3-position, tin, right-angle header'),
 'P028':('DR125-2R2-R','Eaton','C5337632','Exact L1; compare live LCSC with cached TME route'),
 'P029':('AAPS0530M4R7F','Coilank','C49261457','4.7uH +/-20%; bounded ordered-pad fit and current screen'),
 'P030':('SRP5050FA-6R8M','Bourns','C3223092','6.8uH +/-20%; bounded ordered-pad fit and current screen'),
 'P037':('0805W8F2702T5E','Uni-Royal','C17593','27k 1% 100ppm 125mW 0805; R5 4S profile'),
 'P038':('RC0805FR-075K6L','Yageo','C114538','Exact 5.6k 1% 0805 retained'),
 'P043':('CRCW12062R00JNEAHP','Vishay','C2078479','Exact 2ohm 5% 750mW pulse-proof HP resistor retained'),
 'P047':('0402WGF8201TCE','Uni-Royal','C25924','8.2k 1% 100ppm 62.5mW 50V 0402; same MAIN priority divider'),
 'P049':('ARG02BTC3162','Viking','C2681601','31.6k 0.1% 25ppm 0402; paired budget with R33 10ppm'),
 'P050':('PTFR0402Q10K0N9','Resistor Today (RESI)','C52677569','10k 0.02% 10ppm 0402; stronger tolerance than original'),
 'P053':('RT0603BRD0716KL','Yageo','C326732','16k 0.1% 25ppm 0603; only as reviewed pair with R61 3.01k'),
 'P054':('RT0603BRD073K01L','Yageo','C705772','3.01k 0.1% 25ppm 0603; only as reviewed pair with R60 16k'),
 'P056':('0603WAF3832T5E','Uni-Royal','C23034','38.3k 1% 100ppm 100mW 0603; same F5 enable divider'),
 'P058':('ESP32-C3-MINI-1-H4X','Espressif','C41349510','Same PCB antenna/module pinout, flash 4MB, chip v1.1; -40..105C grade'),
 'R5-2S':('0805W8F8201T5E','Uni-Royal','C17828','8.2k 1% 100ppm 125mW 0805; separate alternative profile stock'),
 'R5-3S':('0805W8F1372T5E','Uni-Royal','C17448','13.7k 1% 100ppm 125mW 0805; separate alternative profile stock'),
 'H02':('1053071203','Molex','C505113','Exact black/key-A three-cavity TPA-capable housing'),
 'H03':('1053072202','Molex','C17689101','Exact natural/key-B two-cavity TPA-capable housing'),
 'H04':('1053072203','Molex','C17399592','Exact natural/key-B three-cavity TPA-capable housing'),
}

def main():
    rows=list(csv.DictReader((EV/'entry-sourcing/SHOPPING_LIST_BY_SUPPLIER.csv').open(encoding='utf-8-sig')))
    for r in rows:
        r['original_supplier']=r['supplier']
        r['original_mpn']=r['manufacturer_mpn']
        r['phase5_5_approval']='PENDING_FINAL_BASKET_OWNER_REVIEW'
        if r['group_id'] in OVERRIDES:
            mpn,manufacturer,sku,reason=OVERRIDES[r['group_id']]
            r.update(manufacturer_mpn=mpn,manufacturer=manufacturer,distributor_sku=sku,
                     supplier='LCSC',direct_url=f'https://www.lcsc.com/product-detail/{sku}.html',proposal_reason=reason)
            if mpn!=r['original_mpn']:
                r['phase5_5_approval']='PROPOSED_REPLACEMENT_OWNER_APPROVAL_REQUIRED'
        else:r['proposal_reason']='Retain Phase5.4 identity and supplier; refresh stock/terms'
    (BASE/'phase5_5_plan.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    targets=[dict(id=r['group_id'],mpn=r['manufacturer_mpn'],sku=r['distributor_sku'],url=r['direct_url']) for r in rows if r['supplier']=='LCSC']
    (EV/'browser-targets.json').write_text(json.dumps(targets,indent=2)+'\n',encoding='utf-8')
    print('Planned',len(rows),'rows;',len(targets),'LCSC live targets; all proposed only')

if __name__=='__main__':main()
