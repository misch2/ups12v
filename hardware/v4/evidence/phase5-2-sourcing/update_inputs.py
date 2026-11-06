"""Idempotent Phase5.2 purchasing-document changes; never touches CAD."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'hardware/v4/sourcing'


def main():
    p=OUT/'selections.json'
    s=json.loads(p.read_text(encoding='utf-8'))
    for refs, manufacturer, original, replacement in [
        (['U8'],'Texas Instruments','LM74700QDBVRQ1','LM74700QDBVTQ1'),
        (['C70','C71'],'TDK','GRM188R71C105KA12D','C1608X7R1C105K080AC')]:
        for ref in refs:
            s[ref].update(manufacturer=manufacturer,mpn=replacement,status='OWNER_APPROVED',
                          original_procurement_mpn=original,
                          basis='Explicit owner Phase5.2 approval 2026-10-19; procurement identity only; Phase5.1 compatibility evidence retained',
                          notes=f'Owner-approved purchasing replacement for {original}; source CAD intentionally retains original identity. No CAD modification authorized')
    for ref in ['Q3','Q8','Q9']:
        s[ref]['notes']='Original PMV16UN EOL; AO3400A is preferred procurement candidate, PMV16XNR C110920 is now a sourced alternative. Neither owner approved; hot leakage and sequencing qualification limits in PHASE5_2_COMPATIBILITY_REVIEW.md'
    s['C32']['notes']='HOLD: proposed Yageo has only about0.5-0.6uF typical at18V. Ideal1A/500kHz/18V duty-based calculation gives0.50-0.60Vpp C32-only ripple, before ESR/ESL; not measured or an acceptance threshold. Remote C21 is not qualified local capacitance. No minimum Ceff invented'
    for ref in ['C33','C45','C64','C65']:
        s[ref]['notes']='HOLD: exact TJ00E mapping and DC bias remain unconfirmed by manufacturer. Retained25uF pair basis preserved. TPS62933 table10-2 minimum15uF normal3.3V/500kHz,10uF F5/500kHz does not authorize relaxing25uF. See Phase5.2 compatibility'
    for ref in ['C35','C36']:
        s[ref]['notes']='Murata typical12-14uF at3.3V; calculated illustrative4.7124uF screen uses assumed aging/small-AC factors, not guaranteed joint lower bound. C35 retained2.2uF minimum; C36 no invented floor. Exact procurement proposal remains unapproved'
    for ref in ['TP1','TP3','TP4']:
        s[ref]['notes']='Preferred proposal: hand-formed tinned copper loop, two0.30mm wire tails in existing1.00mm hole; ODloop2.00mm max, height3.5mm max. Full fabrication/jig/envelope proposal in Phase5.2 compatibility; not owner approved or assembled'
    p.write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
    p=OUT/'replacement_candidates.json'
    c=json.loads(p.read_text(encoding='utf-8'))
    c=[r for r in c if r['references'] not in ['U8','C70 C71']]
    for r in c:
        r['evidence']='../evidence/phase5-2-sourcing/replacements-commercial.txt; PHASE5_2_COMPATIBILITY_REVIEW.md'
        if r['candidate_mpn']=='AO3400A':
            r.update(approval_status='PREFERRED_PROPOSAL_OWNER_APPROVAL_REQUIRED',
                     remaining_review='Static logic and package fit supported; lower capacitance than both Nexperia types. IDSS5uA max at55C, no85C maximum. No measured switching/whole-temperature guarantee. Owner selection and prototype qualification remain',
                     nominal_grade='30V N-FET; VGS+/-12V; Rds48mohm max2.5V; Ciss630pF typical; G1S2D3; CE/I2C slow controls only')
        if r['candidate_mpn']=='PMV16XN,215':
            r.update(candidate_mpn='PMV16XNR',supplier='LCSC',sku='C110920',
                     url='https://www.lcsc.com/product-detail/C110920.html',page_stock=65625,
                     unit_price_usd=0.1494,MOQ=5,multiple=5,conditional_order_qty=20,
                     conditional_MOQ_excess=4,conditional_extended_usd=2.988,
                     approval_status='SOURCED_ALTERNATIVE_OWNER_APPROVAL_REQUIRED',
                     remaining_review='Manufacturer12NC934068844215 maps exact PMV16XNR to PMV16XN. IDSS1uA25C only; no hot maximum. About2x Ciss and slower weak-pull-up release than AO3400A; not preferred',
                     evidence='../evidence/phase5-2-sourcing/research-03.txt; ../evidence/phase5-2-sourcing/research-01.txt; PHASE5_2_COMPATIBILITY_REVIEW.md')
    p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    print('Promoted exactly U8/C70/C71 procurement identities; retained originals; other candidates remain holds')


if __name__=='__main__':
    main()
