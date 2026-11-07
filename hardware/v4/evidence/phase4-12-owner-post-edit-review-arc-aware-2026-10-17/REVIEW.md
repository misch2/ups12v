# UPS V4 — kontrola uložených owner USB úprav

2026-10-17. **NEEDS_FIX: dvě nová přerušení mimo USB.** USB je připojené a jeho geometrie se zlepšila, ale nelze potvrdit zachování dosavadního zapojení. Do žádného zdrojového CAD ani produkce nebylo zasaženo.

## Nejkratší postup pro opravu vlastníkem

1. Opravit níže uvedený krátký B.Cu úsek `/USB_MCU_DN`, aby uvolnil místo dvěma původním prokovům.
2. Obnovit průchozí prokov **MCU_EN (86.740,89.500)** a **MCU_BOOT_STRAP2 (84.540,89.500)**, oba **0.50/0.30 mm**. Každý musí mít svoji původní síť, nikoli USB D−.
3. Vyplnit zóny, spustit DRC, uložit a zavřít editory. Následně znovu nezávisle ověřit návrat ze46 na44 opens a obnovení obou původních padových spojení. Toto číslo je očekávání po opravě, nikoli výsledek již provedené opravy.

**Prokovy nelze pouze vrátit na dnešní trasu.** Aktuální D− má od jejich původní mědi jen0.0152 mm místo požadovaných0.10 mm a od vrtání0.1152 mm místo0.25 mm. Připravená lokální odbočka prošla společnou geometrickou kontrolou s oběma obnovenými prokovy; nebyla aplikována do CAD ani nativně DRC validována jako oprava.

## Potvrzené nálezy

| Priorita | Nález | Přímý důkaz |
|---|---|---|
| **P1** | Odstraněn prokov MCU_EN, (86.740,89.500), původní UUID `ca4c8fa5-2a57-4d82-9225-39740126934b` | U1.8 je nyní samostatný padový ostrov; R16.1/C29.1/SW2.1 zůstávají na druhé straně. Nativní DRC hlásí přerušení F↔B a dva dangling track ends. Původní reset/EN propojení bylo přerušeno. |
| **P1** | Odstraněn prokov MCU_BOOT_STRAP2, (84.540,89.500), UUID `5e4c4867-b18e-4f3d-b6c1-dee845e26125` | U1.5 a R17.1 jsou nyní dva samostatné ostrovy. Nativní DRC hlásí další přerušení F↔B a dva dangling track ends. |

Obě sítě měly v přijaté Phase4.11 správnou kontinuitu. Jejich původní stopy zůstaly geometricky shodné; chybí právě uvedené prokovy. Nativní pokrytí všech473 padů ukazuje160→162 ostrovů a právě tyto dva rozštěpené dříve spojené ostrovy. Nejde o pouhou změnu reprezentativního ratsnest endpointu.

![Aktuální chybějící prokovy](C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-12-owner-post-edit-review-arc-aware-2026-10-17/missing-vias-B.png)

### Přesná minimální lokální odbočka D−

V KiCad 10, po výběru správného scratch projektu, ponechat router **Walk Around** a pravidla beze změny. Nemazat celou síť ani tuning group. Všechny body jsou absolutní X,Y v mm, pohled shora.

Odstranit jediný přímý B.Cu úsek `/USB_MCU_DN`, šířka0.20 mm, UUID **`076ac8bc-c659-4f53-9948-b66a2e74e165`**, mezi (82.810499,89.865200) a (87.409614,89.865200). Zachovat sousední 0.006499 mm spoj k via (82.804,89.865200), navazující úsek k meandru i všechny ostatní owner úpravy.

Nahradit jej B.Cu stopou **0.20 mm**, třemi úseky:

| Pořadí | Bod |
|---|---|
| Začátek | (82.810499,89.865200) |
| Roh 1 | (83.145299,90.200000) |
| Roh 2 | (87.074814,90.200000) |
| Konec | (87.409614,89.865200) |

Potom vložit dva původní průchozí prokovy0.50/0.30 mm uvedené výše a zkontrolovat síť každého. Tato kombinace prošla kontrolou mědi a vrtání ve všech vrstvách včetně skutečných exportovaných měděných polygonů oblouků. Přidá D− přibližně0.277 mm; nevyžaduje nový signálový přechod vrstev. Nevyrovnávat automaticky tento rozdíl další serpentýnou. Jde o plán lokální opravy, žádná oprava nebyla provedena.

![Pouze návrh lokální opravy](C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-12-owner-post-edit-review-arc-aware-2026-10-17/proposed-minimal-repair-B.png)

Podrobnosti: [minimal-repair-proposal.json](minimal-repair-proposal.json). Nevyhovující prosté vrácení prokovů je zaznamenáno v [restore-two-vias-geometric-check.json](restore-two-vias-geometric-check.json).

## Co je po USB úpravě správně a co zůstává kompromisem

**Konektivita USB:** všech osm datových spojení a U2 PGND zůstává uzavřených. R48/R49 nejsou obejity, polarita a `/USB_MCU_DP`/`/USB_MCU_DN` zůstávají správné. Duplicity J7 A/B zůstaly zachované. Všechny čtyři J7 VBUS kontakty, U4.1, C28.1 a C27.1 jsou jeden nativně potvrzený ostrov. Schéma je přesně totožné s přijatou Phase4.11.

**U2:** skutečně je v (115.000,81.400),90°. Nechráněné planární A6→U2.1 je **2.100 mm**, A7→U2.2 **2.286 mm**, proti dřívějším15.028/15.248 mm. B6 má v nominálním modelu včetně původního B crossoveru a obou PTH traversál6.892 mm, B7 po F3.988 mm. Je to podstatné přiblížení ESD ke konektoru; žádný libovolný maximální limit vzdálenosti nebyl zaveden.

**Zem U2:** nová0.50 mm F stopa vede (114.575,81.400)→(113.600,81.400)→existující PGND via(113.000,82.000), které je v GND mědi U4. Její délka je **1.824 mm**. Původní návrh0.591 mm s novým via(113.984,81.400) nebyl realizován. Současný návrat je funkčně připojený, ale není pravda, že zachoval navrženou délku0.591 mm. Pokud vlastník chce návrat zkrátit podle plánu, přidání PGND via0.60/0.30 v(113.984,81.400) na již existující PGND stopu geometricky prošlo; nic nebylo přidáno. Jde o volbu ke zlepšení, nikoli zde zavedený nový vzdálenostní limit.

**USB_VBUS:** sériový prokov(109.220,80.518) byl odstraněn. Nový přívod vede F.Cu se šířkou0.60 mm; C28 má0.30 mm odbočku. Poloha C28 a U4 se nezměnila. Konektorový B.Cu okruh zůstává. Nová geometrie nemá fyzický DRC problém; není tím potvrzena ampacita nebo teplota na skutečném HW.

**Mezery:** konektorový F pár má vypočtené minimum0.200 mm; MCU F přibližně0.199980 mm, MCU B0.200 mm. Všechny datové stopy jsou0.20 mm. Obloukové analytické odhady mají uvedenou aproximační mez; primární kontrola clearance je nativní DRC. Projektové routing defaults0.20/0.20 a enforced clearance0.10 zůstaly beze změny. Žádné nové skew/impedance pravidlo nebylo doplněno.

**MCU reference:** délky nejsou totožné s navrženým krátkým F/B mostem:

| Síť | Dnes F.Cu | Dnes B.Cu | Celkem |
|---|---:|---:|---:|
| /USB_MCU_DP | 14.659 mm | 8.151 mm | 22.811 mm |
| /USB_MCU_DN | 10.478 mm | 12.347 mm | 22.825 mm |

D+ má přibližně64.3 % délky na F, D−45.9 %. D− tedy stále vede převážně B.Cu. Dvě levá signálová via se přesunula do(85.598,92.2528) a(82.804,89.8652); pravá zůstala v(92.456,91.4)/(92.456,90.2). Všechna čtyři mají nadále1.00/0.50 mm. Nebyla přidána plánovaná blízká PGND via. Nejbližší stávající PGND via jsou od levého DP1.660 mm, levého DN2.515 mm, pravého DP2.105 mm a pravého DN3.303 mm.

Skutečná In1 polygonová projekce současných F stop, včetně otvorů a antipadů, kryje835/928 vzorků DP a562/662 vzorků DN; krok podél stopy nejvýše0.05 mm, střed a obě hrany, aproximace oblouků do0.0001 mm odchylky. Přerušení reference u velkých signálových via zůstávají. Samotné procento pokrytí není SI kritérium. In2 se nestala souvislou PGND vrstvou. Lze potvrdit částečné zkrácení B cest proti15.063 mm na každé síti; **nelze potvrdit plnou realizaci navržené reference ani90Ω impedanci**.

MCU planární skew je nyní DP−DN=−0.014326 mm. Přidané zaoblené meandry D− byly zahrnuty skutečnými délkami oblouků, nikoli jejich tětivami. Při použití předchozího nominálního stackupu vychází kompletní A cesta přibližně−0.006 mm a B cesta+3.084 mm; současné tloušťky vrstev zde nebyly nezávisle znovu exportovány, proto jde pouze o uvedený nominální model. Původní B-contact asymetrie nebyla a není neúspěšný skew test. USB Full-Speed12Mbit/s nepřináší důvod automaticky přidávat další serpentýny bez konkrétního SI požadavku.

## Výsledky kontrol a zachování

| Kontrola | Přijatá Phase4.11 | Aktuální uložený owner stav |
|---|---:|---:|
| DRC otevřené spoje | 44 | **46** |
| DRC fyzické chyby | 0 | 0 |
| DRC parity | 0 | 0 |
| DRC warnings | 20 | 24 |
| ERC errors / warnings | 0 /11 | 0 /11 |
| Nativní padové ostrovy | 160 | **162** |

Čtyři nové DRC warnings jsou dangling ends na MCU_EN/MCU_BOOT_STRAP2. Původní library warnings zůstávají; pouze souřadnice hlášení U2 následují jeho přesun. Ignored checks jsou shodné s přijatou kontrolou. Z46 opens jsou41 dříve odložených F5,3 dříve odložené IC1 SCL/INT/STAT a2 nová přerušení uvedená nahoře.

Owner má1031 track/arc objektů (z toho12 oblouků),285 vias,154 footprints a473 pads. Proti Phase4.11 přibylo85 a ubylo72 track/arc objektů, žádný stávající track nebyl změněn pod stejným UUID. Ubylo6 a přibyly2 vias; žádný via se stejným UUID nezměnil rozměry. Pohnul se pouze U2 a jeho tři pady. U1/U4 mají obnovená UUID polí reference/value, jejich sémantický obsah, poloha a grafika se nezměnily. Zone definitions/RF omezení a board drawings zůstaly shodné.

Všechny změny stop jsou USB nebo výslovně související lokální PGND/VBUS. Žádná jiná původní stopa se nezměnila. Dvě chybějící ne-USB vias však znamenají selhání zachování konektivity. Ponechané switching/bootstrap/feedback/REGN/BATP trasy jsou shodné a skutečné In1 fill grids po0.1 mm v12×12 mm regionech kolem IC1/L1/U3 nemají změněný vzorek. Jde o konečné vzorkování, nikoli plošný důkaz mezi vzorky. Ownerem uložené vyplnění mědi se přesně rovná novému nativnímu refill výsledku kontrolní kopie.

## Identita zdrojů a provedení

Zdrojový projekt: `hardware/v4/evidence/phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro`. Vlastník potvrdil: „Ano, oba jsou zavřené a vše uložené.“

Kontrolovaný owner PCB SHA256: **`bf66ce440b3e265c3cdf12a10e53c4b65723a476c0b185b0dbad6405a3e8a153`**. Tento stav je zkontrolovaný s nálezy, nikoli nová přijatá baseline.

Přijatý produkční PCB zůstává **`6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`**. Všechny čtyři aktuální owner soubory a tři produkční soubory zůstaly během kontroly hashově nedotčené; schéma/projekt/pravidla jsou shodné s Phase4.11. Přijatý manifest se nezměnil.

Nativní KiCad10.0.7 běžel pouze v monitorovaných izolovaných workerech s explicitním zdrojem a přijatým produkčním manifestem. DRC vyplnil a uložil pouze novou kontrolní kopii. Následný nativní readback potvrdil přesné zachování všech stop, vias, padů a footprints při refillu.

První kontrola v sousedním adresáři `phase4-12-owner-post-edit-review-2026-10-17` skončila běžným odmítnutím nepodporovaného arc objektu. Nedocházelo k native assertion ani pokusu obnovovat editor. Sdílený toolkit byl rozšířen o čtení skutečného start/mid/end oblouků, nativní délky a nativní outside copper polygony s chybou do100nm. Délka se kontroluje proti geometrii oblouku. Dosavadní straight-only proximity/strip analýzy, legacy cleanup planning a raster router mají explicitní guard proti záměně oblouku za tětivu. Po85 offline regresních testech prošla nová nativní kontrola v tomto čerstvém adresáři. Nebyl použit A* ani generovány nové USB trasy do CAD.

Plné exporty: [focused-review.json](focused-review.json), [drc.json](drc.json), [erc.json](erc.json), [post-refill-preservation.json](post-refill-preservation.json), [previous-review-pad-connectivity.json](previous-review-pad-connectivity.json), [source-authority.json](source-authority.json). Tyto soubory jsou důkaz, nikoli produkční migrační plán.

**STOP pro owner opravu a review.** Žádná produkční migrace, změna schématu/BOM/pravidel, fabrication, nákup, napájení HW, firmware, commit nebo push. Odložené R35v2, R12–C26v3, SYS cleanup a veškeré F5 hranice zůstávají zachované.
