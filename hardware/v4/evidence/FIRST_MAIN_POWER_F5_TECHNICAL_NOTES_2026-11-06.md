# UPS V4 F5 — první kontrolované napájení J1

**6. 11. 2026 · NÁVRH KE SPOLEČNÉMU POSOUZENÍ, dosud neprovedeno.**
Platí pro vlastníkem potvrzené **IC1 = BQ25798, R5 = 27 kΩ**, tedy výchozí
4S profil / 750 kHz. F5 označuje osazení 5V větve, nikoli počet článků.
Bez baterie, USB, UART, I²C adaptéru a všech externích zátěží.

Vychází z aktuálních uložených schématu/PCB, požadavků, architektury,
aktivního handoveru a konečného osazovacího BOM. Schéma má u R60/R61 stará
metadata 53k/10k; schválené osazení je **16k/3,01k jako pár**. R32/R33 jsou
31,6k/10k. Před testem potvrdit skutečné osazení těchto párů.
Ponechat schválené R12/C26; tento postup nenavrhuje změnu architektury.

## Zapojení a cesta energie

```text
ověřený bezpečný 48V DC zdroj → pouze DC INPUT RK6006
                                  RK OUT+ ─ krátký pár ─ J1.2 (+)
                                  RK OUT− ───────────── J1.1 (PGND)

J1.2 → F1.2 ─ F1 ─ F1.1 → VIN1 ─ Q1.D
                            │       Q1.S ─ Q2.S       [společné sources]
                            │                 Q2.D ─ NT4 ─ VBUS → IC1.2/3
                            ├→ IC1.9 VAC1                         │
                            ├→ TP15                               └→ PMID
                            ├→ C9 → PGND                              │
                            └→ R12 2Ω → C26 2,2µF → PGND        měnič IC1/L1
                                                                       │
                                                                  SYS / TP4
                                                                   ├→ U3 → MAIN_3V3 / TP13
                                                                   │         → U5 → MCU3V3 / TP8
                                                                   └→ U7 → F5_RAW → Q10/U8 → TP17

ZT-703S: vlastní baterie, USB/nabíjení odpojeno, generátor nezapojen
obě zemní svorky sond → tentýž PGND bod TP3
CH1 → TP15; CH2 → TP4 (první start)
multimetr COM → PGND; V vstup → zvolený měřicí bod
```

**J1.1 je mínus; J1.2 plus.** Ověřit kontinuitou na skutečném kabelu:
J1.1–TP3 a J1.2–F1.2. Pohled do protikusu zrcadlí pohled na PCB; nespoléhat
na barvy vodičů nebo odhad vlevo/vpravo. J1.2 není přímo VIN1, mezi nimi je F1.

Q1/Q2 jsou protisměrné N-MOSFETy se společnými sources 1–3, gates 4,
drains 5–9. Gates řídí IC1.11 ACDRV1 přes R1. **VAC1 je přímo na VIN1 před
oběma FETy**, není jimi oddělen od vstupní špičky. R12/C26 je sériová RC
větev do země, nikoli 2Ω odpor v hlavním napájecím přívodu. D1 omezuje VGS,
není vstupní TVS. VAC2 je na VBUS, ACDRV2 na PGND. [1, 3]

**J8 má nyní tři pozice: 1 = PGND, 2 = NC, 3 = F5_5V_OUT.** Starší text
o dvoupinovém J8 je překonaný. V tomto testu zůstává J8 prázdný.

## Příprava, uzemnění a zdroj

1. Deska na nevodivé podložce; všechny konektory kromě J1 prázdné.
   Připravit dosažitelné tlačítko OUTPUT OFF. Nepřipojovat 48 V přímo k UPS.
   Ověřit, že 48V napáječ má bezpečně oddělený nízkonapěťový výstup podle
   svého označení/dokumentace. Samotný RK6006 nepovažovat za izolační bariéru.
2. Se vším vypnutým/odpojeným prověřit multimetrem propojení zemí CH1/CH2,
   COM a případných USB stínění; zvlášť zjistit vazbu RK OUT− na 48V mínus/PE.
   Vodivost prokáže společnou zem; otevřený obvod **neprokáže bezpečnou izolaci**.
   Oba scope kanály proto používat jako společně uzemněné. Zem sond výhradně
   na PGND; nikdy na source/gate Q1/Q2, VIN1, SYS nebo spínací uzel.
   VGS/VDS vysokostranných FETů s těmito sondami v tomto postupu neměřit.
3. RK6006: **Boot Power OFF, Take Out OFF**, automatické sekvence vypnuté.
   Pro všechny kroky rozlišovat nastavený proud CC od samostatného vypínacího
   OCP. Přesné položky ověřit podle firmware přístroje. [5]
4. Nejdřív bez UPS ověřit DMM polaritu a skutečná napětí 1/5/6/9/12 V, která
   budou použita. Scopem zkontrolovat OUTPUT ON/OFF i změny nastavení, zejména
   že se neobjeví nečekaný velký skok. Pak OUTPUT OFF, nastavit 1 V a vyčkat
   na skutečné vybití výstupu pod 0,1 V. Teprve potom připojit J1.
   Tato kontrola naprázdno neprokazuje chování zdroje s UPS.
5. Sondy ×10 i nastavení kanálů ×10, DC coupling, kompenzace zkontrolovaná.
   Začít CH1 1 V/div, CH2 5 V/div a 100 ms/div; umístit nuly tak, aby nebyl
   obraz oříznutý. Pro pomalý rozběh použít Single, trigger CH1 vzestupně
   přibližně 3,5 V; před spouštěním zkontrolovat skutečné vzorkování a délku
   záznamu. DMM slouží pro přesné DC hodnoty, scope pro kolapsy a cyklování.

## Kroky a očekávané hodnoty

Nastavení níže jsou **návrh konzervativního laboratorního postupu**, nikoli
nové produktové specifikace nebo garantovaná ochrana součástek. Při každém
kroku sledovat skutečné napětí a režim CV/CC. Proud naprázdno zatím nemáme
změřený; z předchozích 8 mA při USB nelze odvodit proud na J1.

| Krok | RK6006: napětí / CC limit; OVP / OCP | Doba a očekávání / PASS |
|---|---|---|
| 0 — připojeno, OFF | 1,00 V / 0,020 A; 1,50 V / 0,030 A | Před ON jsou TP15, TP4, TP13 i TP17 pod 0,1 V. |
| 1 — nízkonapěťový předtest | ON: 1,00 V / 0,020 A; 1,50 V / 0,030 A | Nejvýše 5 s: TP15 ≈1 V, REGN/SYS/MAIN/F5 ≈0 V; zdroj v CV. Trvalé CC = STOP. |
| 2 — první funkční start | Při zachovaném propojení nejdřív CC 0,100 A, OCP 0,150 A, OVP 5,50 V; poté jednou změnit U na 5,00 V | Zachytit rozběh. Nedržet mezikroky kolem detekčního prahu 3,4–3,5 V. Při CV dát nejvýše 5 s na ustálení. TP15/VBUS/PMID ≈5 V, SYS typ. 12,2 V; kontrolovat CE. |
| 3 — U3, stále 5 V | 5,00 V / 0,100 A; 5,50 V / 0,150 A | Po PASS SYS/CE měřit TP13 a TP8; ověřit tabulku níže. Sledovat 30 s, žádné cyklování nebo rostoucí odběry. |
| 4 — F5, stále 5 V | Stejné jako krok 3 | Změřit F5_RAW a TP17; sledovat dalších 30 s. Při poruše kterékoli větve OFF celou desku. |
| 5 — volitelné pokračování po PASS předchozích kroků | 6,00 V / 0,100 A; 6,50 V / 0,150 A | U měnit na již připojeném zapnutém zdroji, nikoli přepojováním kabelu. Po ustálení zopakovat DC hodnoty, sledovat 30 s. |
| 6 — volitelné | 9,00 V / 0,100 A; 9,50 V / 0,150 A | Totéž; SYS zůstává kolem 12,2 V, nikoli 9 V. |
| 7 — volitelné, konec tohoto postupu | 12,00 V / 0,100 A; 12,50 V / 0,150 A | Totéž; nejvýše 60 s. Nepokračovat k 15/20/21 V. |
| 8 — ukončení | OUTPUT OFF | J1 i sondy ponechat zapojené do vybití TP15, SYS a F5 pod 0,1 V; případný zbytkový BAT také změřit. Nevybíjet zkratem. |

**První checkpoint může skončit úspěšně již krokem 4 při 5 V.** Vyšší vstup
není potřeba pro samotné ověření základní funkce. CC není důvod automaticky
zvyšovat limit: vypnout, zaznamenat průběh a rozlišit náběhový odběr od závady.
Pokud se BQ po neúspěšném rozběhu zastaví, další pokus až po vybití a analýze;
neřešit to opakovaným připojováním živého J1.

| Uzel / bezpečnější přístup | Předtest 1 V | Po ustálení při J1 = 5/6/9/12 V |
|---|---|---|
| VIN1: TP15 | ≈1 V | ≈napětí J1; podstatný úbytek na F1/kabelu při tomto malém odběru vyšetřit |
| VBUS: C7.1; PMID: C6.1 | ≈0 V | ≈VIN1 po sepnutí Q1/Q2; nejsou to USB napájecí uzly |
| SYS: TP4 | ≈0 V | **12,2 V typ.; 11,9–12,75 V** je datasheetový rozsah VSYSMIN regulace pro 4S [1, §6.5] |
| REGN: C3.1, PGND C3.2 | ≈0 V | Přibližně **4,8–5 V**, orientační screening 4,6–5,2 V; přesné tabulkové podmínky jsou 5/15 V vstup a 20 mA REGN [1, §6.5] |
| CE_N: TP14 | Ještě nehodnotit logiku | HIGH po naběhnutí biasu, obvykle několik voltů; **≥1,3 V**. Nemá padat LOW při startu SYS/MCU [1, §6.5] |
| MAIN_3V3: TP13 | ≈0 V | Výpočet z osazení **3,328 V**; screening 3,135–3,465 V |
| MCU3V3: TP8 | ≈0 V | Téměř MAIN po U5; **3,135–3,465 V** podle požadavku ±5 % |
| F5_RAW: C64.1 nebo C65.1 | ≈0 V | Z osazení **5,0525 V** nominálně |
| F5 výstup: TP17 | ≈0 V | Blízko F5_RAW, **4,75–5,25 V**; trvalý úbytek řádu diody vyžaduje kontrolu U8/Q10 |
| BATTERY: TP16, bez baterie | ≈0 V | Může být přibližně **2,5 V** — není požadavek 0 V [1, §7.3.6] |
| USB3V3 / USB_VBUS, např. C35.1 / C28.1 | ≈0 V | Očekává se bez významného napájení; stabilní vzestup vyšetřit. DMM sám nekvalifikuje závěrný proud. |

Měřit na přístupných pasivech/testpadech, ne volným hrotem mezi piny QFN.
Pokud nelze sondu na C3/C7 apod. bezpečně fixovat, bod za napětí nezkoušet;
před dalším diagnostickým startem doplnit vhodný měřicí kontakt.

## Jak výsledek vyhodnotit

BQ25798 nepotřebuje hosta ani baterii k napájení SYS. CE HIGH zakazuje
nabíjení, nikoli napájení SYS. Na tomto kusu bude už při 5V vstupu pracovat
boost do přibližně 12,2 V. Diagnostický firmware neprogramuje charger a
nevyžaduje USB ke vzniku hlavních napětí. [1, §7.3.2, §7.3.4, §7.3.6]

Nejdřív hodnotit SYS + CE, potom U3/TP13/U5/TP8, nakonec U7/F5_RAW/U8/Q10/TP17.
**U3 a U7 mají oba automatický EN dělič ze SYS** (100k/38,3k), žádný nezávislý
uživatelský vypínač. To jsou oddělené měřicí kontroly, nikoli izolované
napájecí testy. Případnou závadu F5 nelze v tomto read-only postupu obejít.
PASS naprázdno neprokazuje 1A/2A výkon, stabilitu při zátěži, teploty ani
závěrné blokování U5/U8/Q10.

**Ihned OUTPUT OFF:** obrácená polarita; nečekané napětí zdroje; trvající CC
nebo opakované restarty/kolapsy; SYS po ustálení mimo uvedený 4S rozsah nebo
velké pomalé pilovité průběhy; MAIN/MCU/F5 mimo meze; CE po vytvoření biasu
pod 1,3 V nebo jeho pokles při rozběhu měniče; rychlý růst odběru, lokální
zahřívání, zápach/kouř; sklouznutí sondy. Nehledat horkou součástku prstem
na živé desce. Při nereagujícím RK odpojit jeho 48V přívod a počítat se
zbytkovou energií kondenzátorů. Porucha nemusí čekat na reakci obsluhy.

## VAC1 a hranice dostupného měření

F1 5 A ani CC 100 mA nezaručují omezení prvních mikrosekund: energii dodají
výstupní kondenzátory RK a parazitní LC obvodu. RK OVP/OCP nejsou lokální
rychlou svorkou VAC1. **30 V je absolutní maximum VAC1**, nikoli cílová
hodnota testu; interní OVP neodděluje vlastní VAC1 pin od VIN1. [1, 3]

TP15 je vhodný pro DC a hrubý průběh. Pro skutečný lokální VAC1 transient
je vhodnější **C9.1 proti C9.2** u IC1 (0402); vzdálený TP15 ho nemusí věrně
reprezentovat. Dlouhý zemní krokodýlek má indukčnost a sbírá rušení: může
vyrobit zdánlivé překmity i skrýt skutečnou špičku. ZT-703S má jmenovitě
50 MHz a maximum 200/280 MSa/s podle režimu, skutečné vzorkování a pokrytí
záznamu je nutné zkontrolovat. Pomalý záznam startu ani DMM nejsou důkaz
nepřítomnosti rychlé špičky. [6]

**S uvedenými dlouhými zeměmi nekvalifikovat hot-plug, opakované zasouvání
ani provoz na 20/21 V.** Nejjednodušší doplněk je kompatibilní zemní pružinka
k ×10 sondě a bezpečný přístup k C9; pro VGS/VDS vhodná diferenciální sonda.
Při lokálním měření C9 použít jedinou sondu s krátkou místní PGND zemí,
ostatní zemní přívody sond odpojit. Kvalifikace zůstává samostatný úkol
s ověřeným vzorkováním, různými kabely/zdroji a přednostně vstupním přípravkem.
Ani pružinka sama nenahrazuje tuto kvalifikaci.

## Co musí být před společným schválením uzavřeno

- Bezpečné oddělení konkrétního 48V napáječe a zjištěná zemní propojení;
  izolace kanálů ZT-703S není tímto dokumentem potvrzena ani využívána.
- Skutečné chování konkrétního RK6006 při zapnutí, změně setpointu a OFF;
  jeho zbytková energie a chování s kapacitní UPS zatím nejsou změřeny.
- Skutečné R32/R33 a párové R60/R61, identita fyzické revize a populace;
  IC1/R5 již vlastník potvrdil. Stav osazení MLCC zaznamenat, schválenou
  nejistotu Ceff nepovažovat za uzavřenou měřením naprázdno.
- CE startup, skutečný odběr a uvedená napětí budou teprve změřeny.
  S dlouhou zemí lze provést nízkonapěťový funkční screening; nelze předem
  slíbit přežití libovolného přechodu ani zachytit všechny krátké chyby CE.

Pokud nelze ověřit bezpečnost 48V napáječe, polaritu nebo stabilní bezpečné
měřicí připojení, **nezapínat**. Nejjednodušší řešení je ověřený oddělený
napáječ a vhodné měřicí příslušenství, nikoli větší proudový limit.

Do protokolu zaznamenat revizi/IC/R5/populaci, 48V zdroj, RK firmware,
kabely, teplotu okolí, U/I a CV/CC v každém kroku, DC napětí a uložené
průběhy včetně nastavení sond/vzorkování. **Další akce: společné posouzení
tohoto návrhu před jakýmkoli zapnutím J1.**

## Podklady a rozsah ověření

1. [TI BQ25798, SLUSDV2C, červen 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf):
   §5, §6.1/6.5, §7.3.2/4/6/8. Pro BQ25792 ověřeno také veřejné TI E2E
   vydání SLUSDG1D, duben 2026, §8.3.6; postup je ale určen osazenému BQ25798.
2. [TI TPS62933, SLUSEA4D, srpen 2022](https://www.ti.com/lit/ds/symlink/tps62933.pdf):
   reference 0,8 V, EN a soft-start; výstupy vypočteny ze schváleného osazení.
3. [TI SLUAAL8, květen 2023, §2–3](https://www.ti.com/lit/an/sluaal8/sluaal8.pdf),
   [AOS AON7528 Rev. 1.0, říjen 2023](https://aosmd.com/pdfs/datasheet/AON7528.pdf):
   hot-plug LC/RC a meze FETů. [Přijaté rozhodnutí projektu](v4-safety-design-review-2026-10-11.md).
4. [TI LM74700-Q1, Rev. G](https://www.ti.com/lit/gpn/LM74700-Q1):
   ideální dioda F5; funkci závěrného blokování tento test neověřuje.
5. [Manuál výrobce RK6006/RK6012, kopie PDF](https://manuals.plus/m/7a0cbdcb712ec847043dc14197a8743f8035137896d8f31bd629347634b50235.pdf),
   §1.1, §1.4.2.1 a §1.4.2.3; nepoužita specifikace jiného RK6006-C se síťovým vstupem.
6. [Manuál výrobce ZT-703S, kopie, specifikace osciloskopu](https://www.manualslib.com/manual/3351110/Zoyi-Zt-703s.html?page=39).
   Izolační vlastnosti konkrétního kusu z tohoto údaje nevyplývají.

Čerstvý export netlistu a PCB IPC-2581: KiCad CLI **10.0.7**, uložené soubory,
nikoli živý editor. Konnect IPC čtení padů selhalo; exporty nahradily tuto
konkrétní kontrolu. [Cílená parita](first-main-power-review-2026-11-06-parity.json):
30 referencí / 109 padů, **0 neshod** po ověření dvou čistě exportních přejmenování
SW1/SW2 úplnými množinami pinů. Nejde o nový kompletní ERC/DRC ani fyzické měření.
Zdrojové schéma/PCB, BOM a firmware nezměněny; vedlejší změnu sloupců projektu
po exportu obnovil vlastník, poté ověřen čistý diff sledovaných souborů.
