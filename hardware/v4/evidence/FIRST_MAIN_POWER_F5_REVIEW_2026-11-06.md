# UPS V4 F5 — první zapnutí hlavního vstupu

**6. 11. 2026 · Návrh ke společnému posouzení. Dosud neprovedeno.**
Pro vlastníkem potvrzené **BQ25798 + R5 = 27 kΩ**, tedy výchozí 4S / 750 kHz.
Bez baterie, USB, UART, I²C adaptéru a externí zátěže.

## Zapojení

```text
ověřený bezpečně oddělený 48V zdroj → DC INPUT RK6006
RK OUT+ ─ krátký párový přívod ─ J1.2 (+)
RK OUT− ─────────────────────── J1.1 (PGND)

J1.2 → F1.2 ─ F1 ─ F1.1 → VIN1 → D[Q1]S ─ S[Q2]D → NT4 → VBUS → IC1 → SYS/TP4
                            ├→ IC1.9 VAC1
                            ├→ TP15
                            └→ R12 2Ω → C26 2,2µF → PGND
SYS/TP4 → U3 → MAIN_3V3/TP13 → U5 → MCU3V3/TP8
SYS/TP4 → U7 → RAW → U8/Q10 → TP17

ZT-703S na vlastní baterii, bez USB/nabíjení; generátor nezapojen.
Obě země sond → stejný PGND bod TP3; CH1 → TP15, CH2 → TP4.
Samostatný multimetr: COM → PGND, vstup V → měřený uzel.
```

**J1.1 = mínus, J1.2 = plus.** Na skutečném kabelu ověřit kontinuitu
J1.1–TP3 a J1.2–F1.2; nezaměnit pohled na PCB a do protikusu.
Q1/Q2 jsou N-MOSFETy se společnými sources; řídí je ACDRV1 přes R1.
VAC1 je přímo na VIN1 **před FETy**, takže vstupní špičku vidí i při jejich
vypnutí. R12 není v hlavním přívodu, tvoří s C26 odbočku do země.
D1 je svorka VGS, nikoli vstupní TVS. VAC2 je na VBUS, ACDRV2 na PGND.
Aktuální **J8: 1 = PGND, 2 = NC, 3 = 5V výstup**; ponechat prázdný.

## Před připojením desky

- Ověřit bezpečné oddělení konkrétního 48V napáječe podle dokumentace.
  RK6006 nepovažovat za izolační bariéru. Nikdy nepřipojit 48 V přímo k J1.
- Při vypnutém/odpojeném vybavení zjistit kontinuitu zemí CH1/CH2, COM,
  USB stínění a vazbu RK OUT− na 48V mínus/PE. Otevřený obvod neprokazuje
  bezpečnou izolaci. Kanály používat jako společně uzemněné; **všechny země
  sond pouze PGND**, nikdy na VIN1, SYS, gate/source ani spínací uzly.
- RK: **Boot Power OFF, Take Out OFF**, žádná automatická sekvence.
  Ověřit funkci OUTPUT OFF. Proudový limit CC a vypínací OCP jsou odlišné. [2]
- Bez UPS ověřit DMM polaritu a plánované setpointy; scopem OUTPUT ON/OFF
  a změny napětí. Nečekané velké skoky = nepřipojovat UPS. Potom OUTPUT OFF,
  nastavit 1 V, skutečný výstup nechat vybít pod **0,1 V**, teprve pak připojit J1.
- Izolační podložka, bezpečně fixované sondy ×10, oba kanály ×10/DC;
  zkontrolovat kompenzaci. Začít CH1 1 V/div, CH2 5 V/div, 100 ms/div,
  Single / vzestupný trigger CH1 kolem 3,5 V. Zkontrolovat pokrytí rozběhu,
  neoseknutý obraz a skutečnou vzorkovací frekvenci.

## Postup a nastavení RK6006

Jde o **navržené laboratorní meze k odsouhlasení**, nikoli garantovanou
ochranu nebo nové produktové požadavky. Mezi kroky nepřepojovat živý kabel.
Před zvýšením U nejdřív nastavit příslušné OVP/OCP.

| Krok | U / proudový limit CC | OVP / OCP | Kontrola |
|---|---|---|---|
| 0: připojeno, OUTPUT OFF | 1,00 V / 0,020 A | 1,50 V / 0,030 A | TP15, SYS, MAIN a F5 před ON <0,1 V. |
| 1: předtest, OUTPUT ON | 1,00 V / 0,020 A | 1,50 V / 0,030 A | Nejvýše 5 s; TP15 ≈1 V, ostatní větve ≈0 V, CV. |
| 2: první funkční start | Nejprve limit 0,100 A; potom jednou změnit U na **5,00 V** | 5,50 V / 0,150 A | Nepobývat kolem detekčního prahu 3,4–3,5 V. Při CV dát nejvýše 5 s na ustálení SYS/CE. |
| 3: U3 a MCU | 5,00 V / 0,100 A | 5,50 V / 0,150 A | Po PASS SYS/CE měřit TP13 a TP8; sledovat 30 s. |
| 4: F5 | 5,00 V / 0,100 A | 5,50 V / 0,150 A | RAW a TP17, dalších 30 s. **Zde lze první checkpoint úspěšně ukončit.** |
| 5: volitelné pokračování po PASS | 6,00 V / 0,100 A | 6,50 V / 0,150 A | Zopakovat napětí, 30 s. |
| 6: volitelné | 9,00 V / 0,100 A | 9,50 V / 0,150 A | Totéž, 30 s. |
| 7: volitelné, konec rozsahu | 12,00 V / 0,100 A | 12,50 V / 0,150 A | Totéž, nejvýše 60 s. Žádných 15/20/21 V. |
| 8: ukončení | OUTPUT OFF | — | Ponechat připojeno do vybití TP15/SYS/F5 pod 0,1 V; zkontrolovat také BAT. Nevybíjet zkratem. |

## Očekávaná napětí a PASS/FAIL

Vše vůči PGND. V předtestu 1 V očekávat kromě TP15 všechny uvedené napájecí
větve přibližně nulové. Následující hodnoty platí po ustálení při 5–12V vstupu:

| Měřicí bod | Očekávání / kritérium |
|---|---|
| **TP15 = VIN1** | Přibližně J1; podstatný úbytek na kabelu/F1 při malém odběru vyšetřit. |
| VBUS: C7.1; PMID: C6.1 | Přibližně VIN1 po sepnutí Q1/Q2. |
| **TP4 = SYS** | **12,2 V typ., 11,9–12,75 V** podle 4S VSYSMIN specifikace. [1, §6.5] |
| REGN: C3.1 | Typicky 4,8–5 V; orientační screening 4,6–5,2 V. Tabulkové podmínky jsou 5/15 V vstup, 20 mA REGN. [1] |
| TP14 = CE_N | Po vytvoření biasu HIGH, **≥1,3 V**; nemá padat LOW při startu SYS/MCU. [1] |
| **TP13 = MAIN_3V3** | Z R32/R33 = 31,6k/10k vychází **3,328 V**; screening 3,135–3,465 V. |
| TP8 = MCU3V3 | Téměř MAIN po U5, **3,135–3,465 V**. |
| F5_RAW: C64.1/C65.1 | S osazením R60/R61 = **16k/3,01k jako pár** nominálně **5,0525 V**. Schéma má stará metadata. |
| TP17 = F5 výstup | Blízko RAW, **4,75–5,25 V**; trvalý úbytek řádu diody vyšetřit na U8/Q10. |
| TP16 = BATTERY, bez baterie | Může být přibližně **2,5 V**; není požadavek 0 V. [1, §7.3.6] |
| USB3V3 / USB_VBUS: C35.1 / C28.1 | Bez významného napájení; stabilní vzestup vyšetřit. DMM nekvalifikuje závěrný proud. |

BQ25798 má napájet SYS autonomně bez baterie; **CE HIGH zakazuje nabíjení,
nikoli SYS**. S R5 = 27k se již z 5 V vytváří přibližně 12,2 V. [1]
U3 i U7 mají automatické EN ze SYS: lze je **měřit postupně**, bez zásahu
je nelze napájet odděleně. Nejdřív SYS/CE, pak U3/MCU, nakonec F5.
Na drobných součástkách měřit jen s bezpečně fixovaným hrotem; jinak OFF
a připravit vhodný kontakt. Nepíchat mezi piny QFN.

**Ihned OUTPUT OFF:** chybná polarita/napětí, přetrvávající CC, opakované
kolapsy, neustálení do 5 s při CV, uvedená napětí mimo meze, velké pomalé
pily na SYS/BAT, CE pod 1,3 V po vytvoření biasu, rostoucí odběr, podezření
na rychlé lokální zahřívání, zápach/kouř nebo sklouznutí sondy.
Při nereagujícím RK odpojit jeho 48V přívod; kondenzátory zůstávají zdrojem
energie. **Nezvyšovat automaticky limit a neopakovat start bez analýzy.**
Proud naprázdno zatím není znám; USB odběr ho neurčuje. PASS vyžaduje stabilní CV.

## VAC1, vybavení a otevřené předpoklady

**F1 ani CC 100 mA nezaručují omezení první špičky**: zdrojové kondenzátory
a parazitní LC ji mohou vytvořit před reakcí regulace. VAC1 má absolutní
maximum **30 V**; interní OVP ani RK OVP ho lokálně nesvorkují. [1, 3]

TP15 je vhodný pro DC/hrubý průběh. Lokální VAC1 transient měřit u IC1 na
**C9.1 proti C9.2**. Dlouhá zem sondy může vytvořit falešné zvonění i skrýt
špičku. ZT-703S 50 MHz / max. 200–280 MSa/s ani pomalý záznam startu
neprokazují nepřítomnost rychlého překmitu. [4]
**S dostupnými dlouhými zeměmi nekvalifikovat hot-plug ani 20/21V vstup.**
Nejjednodušší doplněk: kompatibilní zemní pružinka a bezpečný kontakt u C9;
pro vysokostranné VGS/VDS diferenciální sonda. Při lokálním měření použít
jedinou sondu s místní PGND zemí, ostatní země sond odpojit. Samostatná
hot-plug kvalifikace vyžaduje také ověřené vzorkování, přípravek a reprezentativní kabely/zdroje.

Před schválením zbývá potvrdit bezpečnost 48V napáječe, zemní vazby,
chování konkrétního RK, skutečné osazení odporových párů a identitu revize.
Izolace kanálů není potvrzena ani využívána. CE start, odběr a napětí se
teprve změří; zachycení všech krátkých chyb CE není s dlouhou zemí prokázané.
PASS naprázdno neprokazuje zatížitelnost, teploty, Ceff/stabilitu ani reverse blocking.
Není-li ověřen zdroj, polarita či bezpečné měření, **nezapínat**.

Zapsat revizi/populaci, zdroj/RK firmware/kabely, okolní teplotu, U/I a CV/CC,
DC napětí a průběhy včetně nastavení. **Následuje společné posouzení před zapnutím J1.**

Podklady: [1 — TI BQ25798 SLUSDV2C, červen 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf),
[2 — manuál výrobce RK6006, §1.4.2](https://manuals.plus/m/7a0cbdcb712ec847043dc14197a8743f8035137896d8f31bd629347634b50235.pdf),
[3 — TI SLUAAL8, květen 2023](https://www.ti.com/lit/an/sluaal8/sluaal8.pdf),
[4 — manuál výrobce ZT-703S](https://www.manualslib.com/manual/3351110/Zoyi-Zt-703s.html?page=39).
[Podrobné zdůvodnění a ostatní datasheety](FIRST_MAIN_POWER_F5_TECHNICAL_NOTES_2026-11-06.md).
Čerstvá [cílená parita](first-main-power-review-2026-11-06-parity.json) z exportů KiCad 10.0.7:
30 referencí / 109 padů, 0 neshod. Živé IPC nebylo dostupné; nový kompletní
ERC/DRC ani fyzická měření neproběhla. Sledované soubory návrhu zůstaly po obnově nastavení projektu beze změn.
