# UPS V4 — potvrzení owner oprav po USB review

2026-10-17. **Obě nalezená přerušení jsou opravena — PASS tohoto opravného checkpointu.** Dříve popsané kompromisy USB reference zůstávají podmínkami širšího layout review. Nejde o schválení výroby nebo migrace do produkce.

## Výsledek nezávislé kontroly

| Kontrola | Před opravou | Nyní |
|---|---:|---:|
| DRC otevřené spoje | 46 | **44** |
| DRC fyzické chyby | 0 | **0** |
| DRC parity | 0 | **0** |
| DRC warnings | 24 | **20** |
| ERC errors / warnings | 0 /11 | **0 /11** |
| Nativní padové ostrovy | 162 | **160** |

Obnovené průchozí prokovy **MCU_EN(86.740,89.500)** a **MCU_BOOT_STRAP2(84.540,89.500)** mají oba měď0.50 mm / vrtání0.30 mm. Nativní konektivita potvrzuje obnovení U1.8↔R16/C29/SW2 a U1.5↔R17.1. Čtyři přidané dangling-track warnings zmizely. Původní warning identity a ignored checks odpovídají přijaté Phase4.11.

Kontrola všech473 padů proti přijaté Phase4.11 potvrzuje **žádný rozštěpený původní ostrov a zachování všech dosavadních padových spojení**. Proti předchozímu chybnému stavu byly sloučeny právě dva ostrovy: po jednom na MCU_EN a MCU_BOOT_STRAP2. Zbylých44 opens tvoří původních41 odložených F5 a3 IC1 SCL/INT/STAT; žádný nový open nezůstal.

**Všech devět USB/ESD propojení je nativně uzavřených:** obě J7 A/B duplicity, oba vstupy a výstupy U2 k R48/R49, obě MCU strany rezistorů k U1.27/26 a U2 PGND. Zachována polarita a oba sériové rezistory. Všechny čtyři VBUS kontakty J7, U4.1, C28.1 a C27.1 jsou rovněž jeden ostrov. Schéma, projekt a pravidla jsou hashově shodné s Phase4.11.

## Rozsah aktuální owner změny

Proti předchozímu nevyhovujícímu owner stavu bylo nahrazeno33 a přidáno29 track/arc objektů, pouze na `/USB_MCU_DP` a `/USB_MCU_DN`. Přibyly dva opravené prokovy; dva levé signálové USB vias se změnily na0.50/0.30 mm. Levý DP via se současně přesunul z(85.598,92.2528) na(85.598,91.4400); DN zůstal v(82.804,89.8652). Pravá signálová via zůstávají1.00/0.50 mm.

Footprinty a pady se proti předchozímu review nezměnily. Všechny ostatní stávající stopy jsou přesně zachované. Nativní audit včetně zón, RF omezení, board drawings a footprint graphics je shodný. Aktuální owner inventář má1027 track/arc objektů,287 vias,154 footprints a473 pads.

| MCU síť | F.Cu | B.Cu | Celkem |
|---|---:|---:|---:|
| /USB_MCU_DP | 13.847 mm | 7.815 mm | 21.661 mm |
| /USB_MCU_DN | 10.478 mm | 11.187 mm | 21.665 mm |

MCU planární DP−DN je nyní−0.003808 mm, se skutečnými délkami oblouků. Není třeba automaticky přidávat další tuning. Tento výsledek neustanovuje nový skew limit ani90Ω impedanci.

Konektorový F pár má minimum0.200 mm, MCU F přibližně0.199980 mm. Na přepracované MCU B trase je minimum nyní0.100 mm oproti předchozím0.200 mm. Splňuje současnou enforced clearance podle nativního DRC;0.20 mm netclass pair gap je doporučená geometrie routeru, nikoli vynucený min/max constraint. Tento kompromis je zaznamenán a nevyhodnocuje se jako nové porušení neexistujícího USB pravidla.

## Zachované limity předchozího USB review

U2 zůstává v(115.000,81.400),90°, nechráněné A6/A7 cesty2.100/2.286 mm. Jeho PGND stále vede1.824 mm k existujícímu via U4(113.000,82.000); navržený samostatný0.591 mm návrat nebyl přidán. VBUS přívod bez původního sériového prokovu a jeho šířky zůstaly zachované.

DN má nadále větší část délky na B.Cu; v sousední In2 není souvislá PGND plane. Nové PGND stitching vias nebyly přidány. Nejbližší návratové PGND via jsou od levého DP1.995 mm, levého DN2.515 mm, pravého DP2.105 mm a pravého DN3.303 mm. Menší levá signálová via omezují jejich antipady; toto samo není potvrzením výsledné impedance.

Skutečná In1 projekce F stop pokrývá797/877 vzorků DP a581/662 DN (střed a obě hrany, podélný krok nejvýše0.05 mm, aproximace oblouků do0.0001 mm). Přechodové oblasti mají zbývající výpadky reference; procento krytí není SI akceptační limit. Posouzení těchto již zdokumentovaných kompromisů zůstává samostatné od potvrzení dvou opravených přerušení.

## Provedení a zachování originálů

Owner potvrdil: „Opraveno, editor zavřen, DRC OK“. Kontrola použila novou izolovanou kopii a monitorované KiCad10.0.7 workers. DRC refill/save proběhl pouze v kopii; následný nativní readback potvrdil přesné zachování všech routed/placed objektů. Ownerem uložené fill polygony se přesně rovnají čerstvému refillu. In1 grids po0.1 mm v12×12 mm regionech kolem IC1/L1/U3 mají proti předchozímu review0 změněných vzorků. Jde o konečné vzorkování, nikoli field solution.

Ověřený owner PCB SHA256: **`55fe96f32e8e440996924239dd1409f84cb0ffc27cb30c7ea48c7e6c02f610f5`**.

Přijatý produkční PCB nadále: **`6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`**. Všechny čtyři owner source soubory, tři přijaté produkční soubory a přijatý manifest zůstaly během kontroly beze změny. Žádná native assertion/IPC recovery, agent CAD oprava, produkční migrace, změna BOM/pravidel, fabrication, nákup, HW power-up, firmware, commit nebo push.

Evidence: [correction-confirmation.json](correction-confirmation.json), [drc.json](drc.json), [erc.json](erc.json), [post-refill-preservation.json](post-refill-preservation.json), [source-authority-and-preservation.json](source-authority-and-preservation.json).

**Opravný checkpoint dokončen. STOP před další samostatně schvalovanou fází.** Zachovat F5 hranice a odložené R35v2, R12–C26v3 a SYS cleanup návrhy. Nezaměňovat ověřený owner scratch za schválenou produkční baseline.
