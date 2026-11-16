"""Apply recorded owner decisions and reviewed documentary observations, offline only.

No CAD imports, network, carts, supplier messages or Git mutations.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
EV = OUT.parent / 'evidence/phase5-3-sourcing'


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def main():
    s = json.loads((OUT/'selections.json').read_text(encoding='utf-8'))
    for ref in ('Q3', 'Q8', 'Q9'):
        s[ref].update(manufacturer='Alpha & Omega Semiconductor', mpn='AO3400A',
            ratings='30V N-MOSFET; SOT-23; pins1=G2=S3=D; VGS+/-12V',
            status='OWNER_APPROVED', original_procurement_mpn='PMV16UN,215',
            basis='Explicit Phase5.3 owner approval: AO3400A LCSC C20917; purchase20; purchasing-only replacement',
            notes='Existing SOT-23 geometry unchanged. Retain Phase5.2 leakage/rail-ramp/CE and I2C OFF-state prototype checks; no whole-temperature hardware qualification claimed')
    for ref in ('C35', 'C36'):
        s[ref].update(status='OWNER_APPROVED_PROTOTYPE',
            basis='Explicit Phase5.3 owner approval for prototype: Murata GRM21BR61E226ME44L',
            notes='Owner accepts documented effective-capacitance uncertainty for prototype evaluation. Typical12-14uF at3.3V and illustrative4.7124uF screen are not guaranteed minima. C35 retained2.2uF minimum; C36 has no newly imposed minimum. Hardware qualification pending')
    for ref in ('TP1', 'TP3', 'TP4'):
        s[ref].update(mpn='NOT_PURCHASED', manufacturer='N/A', status='EXCLUDED_OWNER_NO_HARDWARE',
            ratings='Existing PCB pad and plated hole sufficient for probing',
            basis='Explicit Phase5.3 owner decision: no purchase or obligatory fitting; optional loops already owned',
            notes='No wire-loop fabrication, purchase, spare or fit requirement. Preserve existing PCB geometry')
    for ref in ('C33', 'C45', 'C64', 'C65'):
        s[ref].update(mpn='C3216X5R1V226MTJ00E', original_procurement_mpn='C3216X5R1V226M160AC',
            status='VERIFIED_IDENTITY_PROTOTYPE_REVIEW',
            basis='TDK Ceramic Capacitor Supply Status Update Jan12,2023 p12: explicit catalogPN160AC to TDKPNTJ00E mapping; same retained device, purchasing identity only',
            notes='Exact naming mapping closed; not a new dielectric/footprint. LCSC C342620 order30 for20fit+1spare+9MOQ excess. Prototype Ceff risk acceptance remains for owner review; retained25uF bank design basis not guaranteed by typical curves and not silently relaxed')
    s['C32']['notes'] = ('PROTOTYPE_REVIEW: recommend retained Yageo CC0805KKX7R9BB225, LCSC C125847 order10 for5fit+3spares+2MOQ excess. Known typical0.5-0.6uF at18V gives calculated0.50-0.60Vpp at1A/500kHz from C32 alone. Not measured; remote capacitors not counted ideally. See Phase5.3 bounded prototype acceptance proposal; no guaranteed Cmin invented')
    s['D3']['notes'] = s['D4']['notes'] = 'Exact BAS116H,115 supply found at LCSC C74210;20pieces for10fit+1spare+9MOQ excess; no diode substitution'
    s['L3']['notes'] = 'Exact MEC retained; Coilcraft dynamic stock unresolved, Farnell EU backorder26Feb2027 cached. No MRC or XGL substitution approved; see unsent exact5-piece request in Phase5.3 commercial review'
    s['C63'].update(manufacturer='YAGEO',mpn='CC0603KRX7R9BB333',
        original_procurement_mpn='GRM188R71H333KA61D',status='PROPOSED',
        ratings='33nF +/-10%; 50V X7R; 0603',
        basis='Phase5.3 same-value/grade/0603 purchasing proposal; Yageo exact specification generated17Oct2026 p1; no CAD change',
        notes='Original Murata obsolete/out of stock. Proposed Yageo body1.6+/-0.1x0.8+/-0.1x0.8+/-0.1mm; Sn terminations; retained SS function and footprint. Owner exact-MPN review pending; verify startup with other prototype tests')
    save(OUT/'selections.json', s)

    def obs(supplier, sku, url, stock, moq, multiple, price, evidence, cache, notes=''):
        return dict(supplier=supplier, sku=sku, url=url, stock=stock, moq=moq, multiple=multiple,
            unit_price_usd=price, price_break_qty=moq,
            availability='PAGE_IN_STOCK', date='2026-10-19',
            freshness=f'Retrieved2026-10-19; provider cache {cache}; page observation only, not reserved inventory',
            evidence='../evidence/phase5-3-sourcing/'+evidence,
            packaging='Plain cut tape / loose pieces; no paid reeling',
            price_basis='Dated USD page observation excluding tax/freight; reconfirm Czech offer before purchase',
            refresh_status='PHASE5_3_REVIEWED_PAGE_OBSERVATION', notes=notes)
    old = {}
    for name in ('supplier_observations.json','phase5_1_observations.json','phase5_2_observations.json'):
        old.update(json.loads((OUT/name).read_text(encoding='utf-8')))
    q = dict(old['AO3400A'])
    q['notes'] = 'Owner approved exact AO3400A/C20917 purchase20; Phase5.2 dated observation reused; no new stock refresh claimed'
    o = {'AO3400A': q}
    o['BAS116H,115'] = obs('LCSC','C74210','https://www.lcsc.com/de/product-detail/C74210.html',55050,10,10,.0669,'research-15.json','today','Exact retained diode. Older TME3-piece shortage bypassed without substitution')
    o['C3216X5R1V226MTJ00E'] = obs('LCSC','C342620','https://www.lcsc.com/product-detail/C342620.html',92160,10,10,.3642,'research-11.json','today','TDK2023p12 mapping verified; Ceff prototype review still pending; not owner-approved by source discovery')
    o['GCM1555C1H102JA16D'] = obs('LCSC','C437434','https://www.lcsc.com/pl/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_Murata-Electronics-GCM1555C1H102JA16D_C437434.html',8450,50,50,.0133,'research-13.json','last month')
    o['DR125-2R2-R'] = obs('DigiKey','513-1662-1-ND','https://www.digikey.com/en/products/detail/eaton-electronics-division/DR125-2R2-R/667148',57,1,1,.83,'research-19.json','2 weeks ago','Exact original. LCSC regional pages conflict; do not treat old reference-only price as available supply')
    o['RC0805FR-075K6L'] = obs('DigiKey','311-5.60KCRCT-ND','https://www.digikey.com/en/products/detail/yageo/RC0805FR-075K6L/728002',134765,1,1,.10,'research-13.json','2 weeks ago','8-piece request; quote10 instead if tier10 atUSD0.034 remains available: USD0.34 total versus8 atUSD0.10=USD0.80. Not automatically overbuying')
    o['RC0402FR-078K2L'] = obs('DigiKey','311-8.20KLRCT-ND','https://www.digikey.com/en/products/detail/yageo/RC0402FR-078K2L/726662',342368,1,1,.10,'research-18.json','yesterday','8-piece request; quote10 atUSD0.021: USD0.21 total versus8 atUSD0.10=USD0.80. Tier optimization requires explicit planning override')
    o['CC0805KKX7R9BB225'] = obs('LCSC','C125847','https://www.lcsc.com/product-detail/C125847.html',81765,5,5,.139,'research-20.json','last week','C32 prototype proposal pending owner review, not guaranteed input capacitance')
    o['CRCW12062R00JNEAHP'] = obs('DigiKey','541-2.0UACT-ND','https://www.digikey.com/en/products/detail/vishay-dale/CRCW12062R00JNEAHP/2228087',14909,1,1,.35,'research-25.json','5 months ago','Exact HP part,6pieces=USD2.10. Older cached USD quote; refresh before order; preceding CZK quote not added to USD cost')
    o['CC0603KRX7R9BB333'] = obs('DigiKey','311-1429-1-ND','https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB333/2833735',48255,1,1,.12,'research-24.json; ../evidence/phase5-3-sourcing/research-27.json','yesterday','C63 owner selection pending. Quote10 atUSD0.065=USD0.65 versus8 atUSD0.12=USD0.96; LCSC MOQ100 not necessary')
    o['RN73C1E31K6BTD'] = dict(old['RN73C1E31K6BTD'])
    o['RN73C1E31K6BTD'].update(supplier='Mouser',sku='279-RN73C1E31K6BTD',
        url='https://au.mouser.com/en/ProductDetail/TE-Connectivity-AMP/RN73C1E31K6BTD?qs=sGAEpiMZZMvdGkrng054t3JR9pTAeVpLheHvv27vnVmmmus07uyG1g%3D%3D',
        availability='PAGE_IN_STOCK',stock=3207,moq=1,multiple=1,unit_price_usd=None,
        date='2026-10-19',freshness='Retrieved2026-10-19; Australia page cache last month; Czech allocation/price not established',
        evidence='../evidence/phase5-3-sourcing/research-16.json; ../evidence/phase5-3-sourcing/research-27.json',
        notes='Exact0402/31.6k/0.1%/10ppm source identified; cut tape MOQ/multiple1. Request8pieces or compare10-tier with both precision resistors on existing supplier; USD/Czech delivered quote missing, no invented FX')
    # Remove unsupported costs/quantities instead of counting an unquoted L3 as supplied.
    o['XAL5050-682MEC'] = dict(old['XAL5050-682MEC'])
    o['XAL5050-682MEC'].update(availability='UNCONFIRMED_CONFIGURATION', stock='',
        unit_price_usd=None, moq=1, multiple=1,
        evidence='../evidence/phase5-3-sourcing/research-04.json; ../evidence/phase5-3-sourcing/research-06.json',
        notes='USD3.02 manufacturer indication only; excluded from priced supplied subtotal. Exact5 supported in principle; stock/dispatch and Czech delivered quote unresolved. Farnell DE cached26Feb2027,42weeks; Czech lookup unavailable')
    o['GRM188R71H333KA61D'] = dict(old['GRM188R71H333KA61D'])
    o['GRM188R71H333KA61D'].update(availability='NOT_AVAILABLE',stock=0,unit_price_usd=None,
        evidence='../evidence/phase5-3-sourcing/research-17.json',
        notes='Exact Murata obsolete and no longer manufactured on DigiKey; cannot use substitute stock as original supply')
    save(OUT/'phase5_3_observations.json',o)
    candidates = json.loads((OUT/'replacement_candidates.json').read_text(encoding='utf-8'))
    candidates = [r for r in candidates if r['candidate_mpn'] not in ('AO3400A','C3216X5R1V226MTJ00E')]
    for r in candidates:
        r.update(approval_status='NOT_SELECTED_AFTER_OWNER_AO3400A_APPROVAL',conditional_order_qty=0,
            conditional_extended_usd=0,remaining_review='Historical fallback only; no second MOSFET purchase')
    save(OUT/'replacement_candidates.json',candidates)
    print('Owner decisions applied; TP hardware excluded; exact TDK alias and reviewed commercial observations recorded')


if __name__ == '__main__':
    main()
