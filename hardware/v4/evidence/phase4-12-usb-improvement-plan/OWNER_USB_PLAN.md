# UPS V4 — Phase 4.12: plán lokálních USB úprav

2026-10-17. **Návrh pro kontrolu vlastníkem; žádná CAD úprava nebyla provedena ani tímto dokumentem schválena.** Phase 4.11 zůstává přijatý CONDITIONAL PASS. Nezačínat USB znovu.

## Úplně jednoduchý postup pro začátečníky

1. Prohlédnout [návrh U2](02-U2-primary.png): doporučený střed **X115.000 / Y81.400 mm, rotace 90°**. Cesta od kontaktů A k ochraně klesne z 15.03/15.25 na 2.10/2.16 mm; zemní přívod zůstane 0.591 mm.
2. Prohlédnout [VBUS](08-VBUS-proposal.png): horní stopa šířky 0.60 mm umožňuje odstranit prokov (109.220,80.518), bez přesunu C28 nebo U4.
3. [Mezeru u R48/R49](10-gap-proposal.png) lze otevřít na přibližně 0.20 mm bez meandrů. Jde o zlepšení geometrie, současných 0.10 mm neporušuje přijatou clearance.
4. [Převážně horní trasu MCU](05-MCU-proposed-F.png) posoudit jako samostatnou volbu: má kratší spodní most, ale vyžaduje přesun čtyř signálových prokovů a kontrolu nového vyplnění PGND. Jednodušší záloha ponechává dnešní B.Cu a zlepšuje návraty.
5. **Zde STOP pro review vlastníkem.** Níže uvedené editační kroky jsou připravené pro následně schválenou ruční práci v KiCad 10. Potom následuje nezávislá validace; migrace do produkce potřebuje vlastní schválení.

## Priority a měřitelné změny

| Priorita | Dnes | Konkrétní návrh | Podstatný kompromis |
|---|---|---|---|
| 1 — U2 | (110.744,91.440),90°; nechráněné A cesty 15.028/15.248 mm | (115.000,81.400),90°; 2.100/2.162 mm; PGND via (113.984,81.400) | Zachování dolní owner trasy prodlouží celou J7.A→R48/R49 cestu asi o 2 mm. Ochrana však zasahuje mnohem dříve. |
| 2 — VBUS | 1.00/0.50 mm sériový prokov; přívod 0.60 mm | Souvislá 0.60 mm F.Cu stopa, bez tohoto prokovu; C28 odbočka 0.30 mm dlouhá 0.897 mm | Ampacita není změřena; šířka hlavního přívodu se nezmenšuje. |
| 3 — mezery | Dvě úzké oblasti s mezerou 0.10 mm u R48/R49 | 0.20 mm šířka / přibližně 0.20 mm mezera; žádná nová serpentýna | Malá lokální změna vývodů; zachovává oba rezistory i názvy sítí. |
| 4 — MCU, varianta F/B | B.Cu 15.063 mm na každém signálu; 4× via 1.00/0.50 mm | D+ F/B 15.817/6.031 mm; D− F/B 13.236/7.780 mm; 4× signál +4× PGND via 0.60/0.30 mm | Zůstává spodní most bez sousední souvislé PGND vrstvy. Staggered výstup zhorší rovnost délek; nelze tvrdit ověřenou impedanci. |

## Podklad a hranice ověření

Přesný projekt: `C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-10-owner-editable-scratch/ups12v_v4.kicad_pro`.

Owner PCB SHA256: `d05be24dd0f3cb857a806fb94fde87da811f1fb1ee3f2feda89d8278bac003de`.

Produkční PCB SHA256: `6d692e893773a28c690c359ca7e7583b54a7b8effe03ffa9844131a36a6c0f80`.

Použity jsou nativní exporty přesně tohoto owner stavu z Phase 4.11: snapshot, skutečné vyplněné polygony In1, padové polygony, courtyard, všechny otvory, měď ve čtyřech vrstvách, skutečné RF rule areas a F5 rezervace. Vazbu na soubory obsahuje [source-binding.json](source-binding.json); závěrečné porovnání hashů je ve [focused-evidence.json](focused-evidence.json).

Kontroly v této fázi jsou pouze matematické nad exportovanou geometrií. Společný návrh kontroluje 32 nových úseků a 9 prokovů proti 2766 ponechaným měděným tvarům a 337 otvorům a vzájemně mezi novými objekty. Zahrnuje clearance 0.10 mm, měď–vrtání 0.25 mm, vrtání–vrtání 0.25 mm, prstenec a hranu desky; nejde o nový nativní DRC. U2 je navíc kontrolován skutečnými transformovanými pady a courtyard. Plánovací rezervace označené „USB …“ byly pro vlastní USB plán odfiltrovány z pomocného checkeru; žádné pravidlo CAD, RF omezení ani F5 rezervace nebylo změněno nebo prominuto.

V Phase 4.12 nebyl načten, uložen ani přepočítán žádný CAD pomocí KiCadu. Přijatá Phase 4.11 má 44 opens, 0 physical, 0 parity; ERC 0 errors. Tyto výsledky nejsou výsledky dosud neprovedených úprav. Offline toolkit má 81 úspěšných regresních testů. Není k dispozici měření USB signálu, ESD, EMI, impedanční výpočet ani tepelná kvalifikace.

## 1. U2 blíže ke konektoru

J7 je (117.390,83.975),90°. A6 D+ je (117.390,81.425), A7 D− (117.390,80.575); B6 D+ (118.740,80.575), B7 D− (118.740,81.425). Zachovat původní spojení duplicit: D+ přes B.Cu mezi PTH kontakty, D− přes F.Cu. U2.1 je D+, U2.2 D−, U2.3 PGND.

| Varianta | Střed U2 / rotace | Via PGND 0.60/0.30 | U2.3→via, 0.50 mm stopa | Courtyard mezera k J7 / U4 |
|---|---|---|---|---|
| Dnešní | (110.744,91.440),90° | (109.728,91.440) | 0.591 mm | Přijatý owner stav |
| **A — doporučená** | **(115.000,81.400),90°** | **(113.984,81.400)** | **0.591 mm** | **0.640 / 0.910 mm** |
| B — alternativa | (114.700,82.500),90° | (113.684,82.500) | 0.591 mm | 0.940 / 0.610 mm |

Délky od J7 po první ochranný pad U2, nikoli vzdušná vzdálenost:

| Kontakt | Dnes, planární | A, planární | B, planární |
|---|---:|---:|---:|
| A6 D+ | 15.028 mm | 2.100 mm | 2.855 mm |
| A7 D− | 15.248 mm | 2.162 mm | 2.917 mm |
| B6 D+ | 16.730 mm | 3.802 mm | 4.557 mm |
| B7 D− | 16.950 mm | 3.864 mm | 4.619 mm |

Při referenci na F.Cu středy kontaktů má cesta B6 navíc dvě PTH traversály, nominálně celkem 3.090 mm při dnešním stackupu. Například A návrh má B6→U2 přibližně 6.892 mm v modelu stopa+barrel; B7 zůstává 3.864 mm. To není elektrická doba šíření ani model vnitřku konektoru. Obě orientace USB-C zůstávají funkčně zapojené a jejich geometrická asymetrie nezmizí pouhým posunem U2.

![U2 návrh A](C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-12-usb-improvement-plan/02-U2-primary.png)

[Původní stav](01-U2-before.png) · [Alternativa B, tenké čáry přes původní měď](03-U2-alternative.png)

Obě polohy leží v ověřené mezeře mezi skutečnými courtyard U4 a J7. Nepřekrývají C28, montážní otvory ani J7 shield sloty; checker zahrnuje jejich skutečné vrtání. Datové stopy zůstávají F.Cu, bez nového signálového prokovu nebo odbočeného ochranného stubu. U2 leží přímo na cestě. Oba výstupy míří dolů do zachovaných kotev (116.840,85.464239) a (116.440020,85.629917) a dále původními cestami k R48/R49. USB_VBUS ani USB3V3 se kvůli U2 neposouvají.

Volba zemního prokovu je podstatná: zdánlivě lákavá poloha U2 (115.300,82.000) s via (114.284,82.000) **neprošla**. Prokov zasahuje B.Cu USB_VBUS na X114.808; měděná mezera −0.076 mm a vrtání–měď jen 0.074 mm. Kontrola samotné F.Cu by tuto chybu skryla. Tento odmítnutý kandidát není součástí doporučení.

Via doporučené A leží uvnitř skutečného In1 PGND polygonu. U nových datových F úseků je v dnešním vyplnění kryto 803/871 vzorků středu a hran, chybějící jsou zejména u PTH kontaktů a přechodových oblastí. Krátký PGND přívod je zachován; žádná souvislá reference přes každý antipad není tímto číslem prohlášena za ověřenou. Po osazení nového prokovu je nutné nové vyplnění a kontrola návratu. Umístění blíže ke konektoru vychází z TI TPD2EUSB30A SLVSAC2G, rev. G, §10.1–10.2 ([datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf)); nepřidáváme libovolný maximální počet milimetrů.

### Přesné editace U2 — až po schválení návrhu

Všechny souřadnice jsou absolutní X,Y v mm v horním pohledu KiCadu. Neměnit pomocný počátek a neobracet pohled podle obrázku.

1. Otevřít uvedený scratch projekt v KiCad 10. V PCB Editoru zkontrolovat název souboru. Zapnout F.Cu, B.Cu, In1 a courtyard. V router settings zvolit **Walk Around**, ponechat vynucení clearance a vypnout **Remove redundant tracks**, aby router automaticky neodstranil některou duplicitní větev J7. Význam těchto voleb ověřen v [KiCad 10 manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html).
2. Jednotlivě odstranit pouze následující čtyři úseky USB_DP a čtyři USB_DN. Nevolit Delete whole net / celý připojený spoj. Přesná UUID jsou v `focused-evidence.json`, sekce `removals.U2`.

| Síť | Řetězec k odstranění; obsahuje 4 úseky |
|---|---|
| USB_DP | (117.390,81.425) → (117.390,81.725) → (117.162182,81.725) → (116.840,82.047182) → (116.840,85.464239) |
| USB_DN | (117.390,80.575) → (116.990,80.975) → (116.990,81.047182) → (116.440020,81.597162) → (116.440020,85.629917) |

3. **Přesunout pouze footprint U2 pomocí Properties (`E`)**, X115.000, Y81.400, angle90°. Nepoužít drag připojených spojů. R48/R49, U4, J7, C28 a dolní datové trasy ponechat. Původní měď u starého místa U2 je součástí průchozích datových cest a zůstává spojitá. Původní PGND via a jeho krátké PGND stopy mohou zůstat; nejsou novou cestou U2. Nepřipojovat nový U2.3 dlouhou stopou zpět ke starému via.
4. Nové středy padů musí být U2.1=(115.425,81.750), U2.2=(115.425,81.050), U2.3=(114.575,81.400). Vložit nový **PGND via (113.984,81.400), diameter0.60, drill0.30**, průchozí F↔B; z pad3 vést přímou F.Cu stopu 0.50 mm.
5. Vést níže uvedené F.Cu cesty šířky 0.20 mm, ideálně společnou část jako pár. Route Differential Pair je standardně `6`; pro asymetrické krátké vývody lze použít jednotlivé stopy. Existující páry jsou rozpoznané, žádné přejmenování sítí není potřeba. Každý bod tabulky je skutečný roh nebo ukončení, nikoli pokyn vést vzduchem přímo přes překážku.

| Úsek A | Body v pořadí |
|---|---|
| J7.A6→U2.1 | (117.390,81.425) → (115.750,81.425) → (115.425,81.750) |
| J7.A7→U2.2 | (117.390,80.575) → (115.900,80.575) → (115.425,81.050) |
| U2.1→původní DP kotva | (115.425,81.750) → (115.425,83.000) → (116.840,84.415) → (116.840,85.464239) |
| U2.2→původní DN kotva | (115.425,81.050) → (115.025,81.450) → (115.025,83.165686) → (116.440020,84.580706) → (116.440020,85.629917) |

6. Pokud vlastník vybere alternativu B, použít **namísto A** střed (114.700,82.500),90°, zemní via (113.684,82.500) a přesné cesty z `U2-alternative.json` (`incoming`, `outgoing`). Pady jsou .1=(115.125,82.850), .2=(115.125,82.150), .3=(114.275,82.500); zemní přívod opět 0.50 mm. Ostatní kroky a kotvy jsou stejné.
7. Po tomto uceleném kroku vyplnit zóny a provést DRC a kontrolu všech kontaktů J7, U2.1/.2/.3 a R48.2/R49.2. Nepokračovat s novým fyzickým problémem. Změna footprintu nesmí přejmenovat sítě ani poškodit původní cesty.

## 2. MCU reference: praktická F/B volba a záloha

Současná délka od R48.1 k U1.27 je 20.374 mm, R49.1→U1.26 20.518 mm. Z toho je na B.Cu **15.063 mm na každé síti**. Přední vývody mají 5.311/5.455 mm. Čtyři signálové průchozí via jsou 1.00/0.50 mm. Nejbližší PGND via jsou od levého DP 2.595 mm, levého DN 2.711 mm, pravého DP 2.105 mm a pravého DN 3.303 mm. Středy PGND jsou (80.025,92.600), (75.500,88.650), respektive pro oba pravé (92.600,93.500).

Stackup má dielektrika 0.10/1.24/0.10 mm. F.Cu sousedí s In1 PGND, B.Cu s In2, která obsahuje signály a napájení. Vzdálenější In1 se nemůže automaticky vydávat za ideální sousední B referenci. Dnešní skutečné In1 antipady kolem dvojic velkých signálových via splývají. Stopy na B tedy nelze označit za ověřených 90 Ω jen podle šířky a mezery.

Přímý F pár mezi dnešními konci byl geometricky odmítnut: koliduje s MCU_EN, MCU3V3/C30, BOOT_STRAP2 a padovou oblastí U1. Přijatý napájecí layout ani tyto signály kvůli USB nepřesouváme. **Nejde o důkaz nemožnosti všech myslitelných F tras**, ale o konkrétní odmítnutí přímého koridoru. Funkční kompromis vede většinu délky F.Cu a překročí překážky krátkým B mostem. Zůstávají právě dva přechody vrstev na každý signál; čtyři původní signálové prokovy se odstraní a čtyři nové je nahradí.

![Volitelná přední trasa](C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-12-usb-improvement-plan/05-MCU-proposed-F.png)

[Současná B.Cu](04-MCU-before-B.png) · [Nový B most](06-MCU-proposed-B.png) · [Skutečná dnešní In1 pod navrženými F stopami](07-MCU-current-In1-projection.png)

Plánované celkové délky MCU jsou 21.849/21.015 mm, D+−D− = **+0.833 mm** proti dnešním −0.144 mm. D+ má 72.4 % délky na F, D−63.0 %. V nominálním modelu celé cesty J7→U1 s primárním U2 vychází rozdíl A přibližně +0.795 mm, B +3.885 mm (dnes A−0.1365, B+2.9535 mm). Levý DN přechází dříve než DP, aby obešel skutečný BOOT_STRAP2 diagonální spoj. Tato část je rozpojenější než pravidelný pár; je to otevřeně uvedený kompromis reference proti rovnosti cest, nikoli prohlášení o lepší impedanci. Nepřidávat vyrovnávací serpentýny.

Projekce nových F cest do **dnešních skutečných** In1 polygonů kryje 1432/1842 vzorků středu a obou hran po nejvýše 0.05 mm. Mezery se soustředí hlavně kolem odstraněných starých via na X77–78 a X92–93 a nových přechodů. Čtyři navržené PGND via leží uvnitř dnešní In1 PGND. Nová signálová via však vytvoří vlastní antipady. Staré antipady mohou po odstranění via zmizet; bez nového nativního fillu nelze určit konečné krytí ani prohlásit návrat za souvislý. U každého přechodu je připraven konkrétní blízký PGND prokov, nikoli pouze vzdálené obecné propojení zemí.

### Přesné editace volby MCU F/B

1. Vybrat pouze sítě `/USB_MCU_DP` a `/USB_MCU_DN` (prefix `/` je hierarchický název). Odstranit jejich **10 B.Cu úseků** a právě čtyři signálové prokovy: DP (77.724,91.400), (92.456,91.400); DN (77.724,90.200), (92.456,90.200). Přesná UUID jsou v `focused-evidence.json`, `removals.MCU`. Zachovat všech 15 současných F.Cu vývodových úseků, včetně bodů po odstraněných via. Pokud segment patří tuning group, vybírat její jednotlivé příslušné úseky; nesmazat celou síť/skupinu s dalším obsahem.
2. Vložit čtyři **signálové via 0.60/0.30 mm**: DP (85.300,91.800), (91.000,91.800); DN (83.800,90.000), (91.000,90.600). Net musí odpovídat tabulce. Každý je průchozí, i když signál používá jen F/B. Vložit je jednotlivě na přesné pozice; automatická dvojice via po `V` nemusí vytvořit potřebné odstupňování.
3. Spojit následující úseky stopami 0.20 mm. Uprostřed B mostu jsou středy Y91.400 /91.000, tedy mezera mědi 0.20 mm. Širší rozevření na koncích je záměrný vývod, nikoli nutnost tuningů.

| Síť / vrstva | Body v pořadí |
|---|---|
| DP F levá | (77.724,91.400) → (78.524,90.600) → (84.920,90.600) → (84.920,91.420) → (85.300,91.800) |
| DN F levá | (77.724,90.200) → (83.600,90.200) → (83.800,90.000) |
| DP B most | (85.300,91.800) → (85.700,91.400) → (90.600,91.400) → (91.000,91.800) |
| DN B most | (83.800,90.000) → (84.800,91.000) → (90.600,91.000) → (91.000,90.600) |
| DP F pravá | (91.000,91.800) → (91.400,91.400) → (92.456,91.400) |
| DN F pravá | (91.000,90.600) → (91.400,90.200) → (92.456,90.200) |

4. Vložit tyto **PGND via 0.60/0.30 mm**, nesplést se signálovými:

| Příslušný signálový přechod | PGND via | Vzdálenost středů |
|---|---|---:|
| DP levý (85.300,91.800) | (85.300,92.600) | 0.800 mm |
| DN levý (83.800,90.000) | (83.000,91.200) | 1.442 mm |
| DP pravý (91.000,91.800) | (91.000,92.600) | 0.800 mm |
| DN pravý (91.000,90.600) | (91.000,89.800) | 0.800 mm |

Via (83.000,91.200) má vrtání v mezeře mezi skutečnými zemními SMD ploškami U1, nikoli vrtání skrz SMD pad. Ponechat tuto kontrolovanou polohu; nevkládat libovolně zemní via mezi oba signály. Testované mezilehlé polohy kolidovaly s F vývody a/nebo B párem.

5. Vyplnit PGND, zkontrolovat skutečné In1 antipady a všechny čtyři návraty. Potom DRC a parity/connectivity kontrola R48.1→U1.27 a R49.1→U1.26. Při nutnosti přesunout chráněnou napájecí měď zastavit tuto variantu a vrátit se k níže uvedené záloze; nevynucovat cestu změnou clearance.

### Menší záložní úprava: zachovat B.Cu

Pokud vlastník nechce F/B přetrasování, ponechat oba dnešní 15.063 mm B úseky a všechny F vývody. Geometricky prošlo zmenšení čtyř stávajících signálových via na **0.60/0.30 mm na původních souřadnicích** a přidání PGND via stejných rozměrů v (77.724,92.200), (92.456,89.400), (92.456,92.200). Tři odpovídající návraty jsou 0.800 mm od signálových via. Levý DN zatím spoléhá na existující PGND via (75.500,88.650), vzdálené 2.711 mm; v omezeném screeningu 24 pozic do ±1.2 mm v osách nebyla nalezena nová vyhovující poloha bez vrtání v SMD padu. Není to důkaz nemožnosti vzdálenějšího nebo jinak upraveného návratu.

Menší signálová via dávají nominálně prostor asi 0.40 mm mezi kruhovými In1 antipady při clearance0.10 a rozteči1.20 mm; dnešní 1.00 mm via tento prostor nemají. Toto je geometrická předpověď pro refill. Záloha **nevytváří sousední PGND v In2**, nemění B impedanci na ověřenou a je pouze lepší strategií přechodových návratů v rámci zachované trasy. Přesný schválení čekající návrh: `MCU-B-fallback.json`. Také jeho společná kombinace s U2 A, VBUS a úpravou mezer prošla geometrickou kontrolou: [B-fallback-with-gap.json](B-fallback-with-gap.json).

## 3. USB_VBUS bez sériového prokovu

![VBUS návrh](C:/Users/Michal/Git/my/ups12v/hardware/v4/evidence/phase4-12-usb-improvement-plan/08-VBUS-proposal.png)

Prokov (109.220,80.518),1.00/0.50 mm je možné obejít po F.Cu bez přesunu U4, C28, U2 nebo chráněné napájecí mědi. C28 zůstává ve vlastnické poloze (114.074,77.978), jeho PGND spoj i via zůstávají. Vstup U4.1 je (105.850,80.700); krátký stávající 0.60 mm úsek z (106.032,80.518) do padu ponechat. Celá nová hlavní cesta od J7.A9 k U4.1 má asi 13.258 mm, bez tohoto sériového barrel přechodu. Původní B.Cu napájecí propojení kontaktů J7 a všechny čtyři VBUS kontakty zůstávají.

### Přesné editace VBUS

1. Odstranit jen těchto pět úseků USB_VBUS a via `a3b8a2f5-dcb0-48c8-be4b-75eb3930c432` (109.220,80.518):

| Vrstva / šířka | Začátek → konec |
|---|---|
| F /0.30 | (113.594,77.978) → (113.340,78.232) |
| F /0.30 | (113.340,78.232) → (111.506,78.232) |
| F /0.30 | (111.506,78.232) → (109.220,80.518) |
| F /0.60 | (109.220,80.518) → (106.032,80.518) |
| B /0.60 | (109.220,80.518) → (114.808,80.518) |

2. Nová **F.Cu 0.60 mm**: J7.A9 (117.390,78.875) → odbočka (113.594,78.875) → (106.032,78.875) → (106.032,80.518), napojit na ponechaný vstupní úsek U4.1. Dva vodorovné úseky u odbočky jsou jedna přímá trasa.
3. Nová **F.Cu 0.30 mm**: C28.1 (113.594,77.978) → (113.594,78.875), délka0.897 mm. Zachovat zem C28.2.
4. Ponechat svislý B.Cu spoj na X114.808 i konektorový napájecí okruh. Není důvod odstraňovat více mědi. Refill + DRC a ověřit J7.A4/A9/B4/B9→U4.1 i C28.1. Zachovaná šířka0.60 mm je srovnání geometrie, nikoli nové proudové nebo tepelné potvrzení.

## 4. Mezery a asymetrie bez zbytečného tuningu

USB řadič ESP32-C3 používá Full-Speed 12 Mbit/s (Espressif MINI-1 datasheet v2.2, §5.2.1.5; [zdroj](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf)). Nominální geometrický rozdíl kompletních B-kontaktních cest **D+ delší o2.9535 mm** je pozorování z Phase4.11, nikoli selhání neexistujícího skew pravidla. Nevyrovnávat jej automatickou serpentýnou. Zachovat A/B kontakty, oba rezistory i oba názvy MCU sítí.

Projekt má clearance0.10 mm a routerový default pair width/gap0.20/0.20 mm. Nemá vynucenou USB `diff_pair_gap` min/max, skew ani impedanční constraint. Rozdíl mezi optimální routerovou mezerou a kontrolovanou clearance vysvětluje [KiCad 10 DRC manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html). Dnešní mezera0.10 mm je legální; při ruční úpravě lze rozumně využít volný prostor na0.20 mm bez změny pravidel.

[Před úpravou](09-gap-before.png) · [Ověřená lokální alternativa](10-gap-proposal.png)

### Přesné editace lokálních mezer

Nezávisí na výběru F/B versus zachovaný B most; mění pouze F vývody u R48/R49 a dlouhou konektorovou DN rovinku. Výsledný návrh byl společně screenován s variantou U2 A, VBUS a MCU F/B, bez kolizí. Dosud nejde o native DRC.

1. U MCU strany nahradit tři DP úseky mezi (92.456,91.400) a R48.1 následujícím řetězcem, šířka0.20 mm: **(92.456,91.400) → (92.874,90.982) → (95.032,90.982) → (95.490,91.440)**.
2. Nahradit tři DN úseky mezi (92.456,90.200) a (95.490,90.184): **(92.456,90.200) → (92.838,90.582) → (95.092,90.582) → (95.490,90.184)**. Ponechat krátký svislý úsek do R49.1 (95.490,90.000).
3. Na konektorové straně nahradit pět DN úseků od (96.990001,90.000) přes dnešní Y90.520 až do (111.068980,91.083335): **(96.990001,90.000) → (97.410001,90.420) → (110.405645,90.420) → (111.068980,91.083335)**. Ponechat R49.2→(96.990001,90.000) i navazující malý úsek do Y91.090. DP dlouhá stopa na Y90.820 se nehýbe.
4. Referenční seznam11 odstraněných UUID je `focused-evidence.json:removals.gap`; nové úseky `pair-gap-option.json:paths`. Nejmenší vypočtená mezera stop v celém F konektorovém páru je0.199980 mm (zaokrouhlená původní geometrie), v MCU páru0.200000 mm. Není potřeba zmenšovat clearance nebo přidat custom rule. DRC po úpravě rozhodne podle skutečné KiCad geometrie.

## Dokončení pozdějšího owner editačního checkpointu

Po každém schváleném uceleném kroku provést refill, DRC, kontrolu dotčené connectivity/parity a lokální diff. Před předáním zavřít editory a uložit aktuální soubory; nezávislá kontrola provede nové ERC/DRC, kontrolu všech devíti uzavřených USB/ESD spojů, duplicit J7, obou sériových rezistorů, ploch PGND, zachování ostatních owner zlepšení a hashů produkce. Neočekávaný native assertion/IPC failure znamená STOP podle AGENTS; neautomaticky obnovovat KiCad.

**Žádné přepsání produkce ani migrace celého scratch souboru.** Nedotýkat se IC1 SCL/INT/STAT, 41 F5 opens, RF zóny, napájecích/switching/bootstrap/feedback/REGN/BATP tras ani odložených R35v2, R12–C26v3 a SYS cleanup návrhů. VBUS změny jsou výslovně vyjmenovaná USB závislost. BOM, schéma, net names, pravidla, manifest i ostatní owner zlepšení zůstávají v této plánovací fázi beze změny.

## Evidence a reprodukce pouze nad exporty

- [Společný návrh a měření](combined-proposal.json): primární U2 + VBUS + volitelný MCU F/B včetně návratů; before/after délky, nominální 3D délky a skutečná dnešní In1 projekce.
- [Lokální mezery](pair-gap-option.json): doplněk nad společným návrhem, vlastní geometrická kontrola a výsledné délky.
- [Dvě polohy U2](U2-primary.json), [alternativa](U2-alternative.json), [VBUS](VBUS-all-F.json), [MCU B záloha](MCU-B-fallback.json).
- [Přesné původní objekty a zachování zdrojů](focused-evidence.json). Průběžné `U2-A`, `MCU-direct-F`, `MCU-B-return*`, první `MCU-short-B-bridge` jsou odmítnuté nebo překonané pokusy, nikoli nabídka ke kopírování. Pro finální MCU použít `combined-proposal.json` nebo `MCU-short-B-bridge-v2.json` + tabulku PGND.
- Implementace screeningu: `hardware/v4/tools/v4kicad/usb_improvement_plan.py`. Bez pcbnew, CAD zápisů, vyhledávání USB tras nebo A*; výslovně zadané polylinie. Import nic nespouští ani nezapisuje. Obrázky ukazují exportovanou měď/pady a označené plánované geometrie; nejsou screenshoty již upraveného KiCadu.

**Phase4.12 hotova jako plán. STOP pro review vlastníkem.**
