# V4 — přehled parametrů UPS, 2S / 4S

Obnoveno 9. 11. 2026 podle přehledu vytvořeného 8. 11. 2026.

Výpočetní přehled pro V4 s BQ25798 a volitelnou F5 větví. **Externí USB-C PD trigger je společný předpoklad.** Limit článků 1C je horní mez, nikoli požadavek dosáhnout 1C v každé situaci. Uvedené odhady nejsou měření ani garantované parametry prototypu.

## Předpoklady

- Pack 2S1P nebo 4S1P, Li-ion 18650, 3000 mAh, nominálně 3,6 V/článek, nabíjení na 4,2 V/článek. Kapacita obou sériových packů zůstává 3 Ah.
- Zadaný limit článků: 1C = 3 A při nabíjení i vybíjení. Konkrétní článek a BMS nejsou vybrány.
- Plánované napětí packu pod zátěží: 2S 6,4–8,4 V; 4S 12,8–16,8 V. Nejde o nové nastavení vypínacího prahu BMS.
- Pro výdrž se počítá s využitím 85 % jmenovité energie a účinností výstupního měniče 90 %. Jde o plánovací předpoklady bez vybíjecí křivky konkrétního článku.
- Vlastní spotřeba na SYS: 0,3 W jako ilustrační úspornější scénář, 1,5 W jako konzervativní projektová rezerva. Ani jedna hodnota není změřený typický odběr.
- Při běžném bateriovém provozu napájí baterie SYS přes vodivou cestu; další 90% BQ převod se do výdrže nepřičítá. Úbytky této cesty jsou přibližně zahrnuty v plánovacím rozpočtu.

## Základní parametry

| Parametr | 2S1P | 4S1P |
| --- | ---: | ---: |
| Počet článků / kapacita | 2 / 3 Ah | 4 / 3 Ah |
| Jmenovitá energie | 21,6 Wh | 43,2 Wh |
| Energie použitá ve výpočtu výdrže | 18,36 Wh | 36,72 Wh |
| Nominální napětí packu | 7,2 V | 14,4 V |
| Plánovaný rozsah packu pod zátěží | 6,4–8,4 V | 12,8–16,8 V |
| VSYS z baterie | Přibližně napětí packu minus úbytek cesty | Přibližně napětí packu minus úbytek cesty |
| VSYS ze zdroje, výchozí profil BQ25798 | Od cca 7,2 V; sleduje pack | Od cca 12,2 V; sleduje pack |
| VSYS u plného packu, nabíjení vypnuté | Typ. 8,6 V PWM / 9,0 V PFM | Typ. 17,0 V PWM / 17,4 V PFM |
| 5V výstup F5: trvalý projektový cíl | **2 A / 10 W** | **2 A / 10 W** |
| Limit článků při 1C | 3 A nabíjení i vybíjení | 3 A nabíjení i vybíjení |
| Bateriový výkon při 3 A na spodní hranici packu | 19,2 W | 38,4 W |
| Z toho pro externí regulovanou zátěž při η=90 % a režii 1,5 W | 15,9 W | 33,2 W |
| Současný plán nabíjení V4 | Nejvýše nominálně 0,5 A | Nejvýše nominálně 0,5 A |
| Praktický vstup pro plán 0,5 A se zátěží | **9 V / 3 A** do 10 W | **20 V / 2 A** do 15 W externě |

VSYS není pevně stabilizovaných 12 V ani přímo napětí PD zdroje. Hodnoty VSYS v tabulce jsou typické body BQ25798, nikoli garantované krajní meze. Datasheet například uvádí pro plný 4S pack při vypnutém nabíjení v PWM 16,82–17,25 V a pro výchozí minimální regulaci 11,9–12,75 V. PFM, tolerance a přechody vyžadují odpovídající rezervu připojeného spotřebiče. Jiný osazený IC vyžaduje samostatné posouzení výchozího profilu.

3A třída samotného TPS62933 nezaručuje 3 A na celém F5 výstupu. Platí projektový cíl 2 A. F5 označuje osazení 5V větve, nikoli počet článků.

Výkon 15,9 / 33,2 W je pouze energetický rozpočet zadaného 1C packu, nikoli kvalifikace desky, BMS, kabeláže nebo externího měniče. 36W instalace vyžaduje na spodní hranici 4S packu přibližně `(36/0,9 + 1,5)/12,8 = 3,24 A` ještě před dalšími ztrátami, a tedy přesahuje zadaný 1C limit.

## Doba běhu

Zátěž znamená užitečný výkon za jedním výstupním měničem.

| Zátěž | 2S, režie 0,3 W | 2S, rezerva 1,5 W | 4S, režie 0,3 W | 4S, rezerva 1,5 W |
| --- | ---: | ---: | ---: | ---: |
| 1 W | 13,0 h | 7,0 h | 26,0 h | 14,1 h |
| 5 W | 3,14 h | 2,60 h | 6,27 h | 5,20 h |
| 15 W, externí měnič | 1,08 h | 1,01 h | 2,16 h | 2,02 h |

**15 W vyžaduje externí měnič z VSYS**, protože přesahuje 10W cíl F5. U 2S je navíc mimo současný 10W kvalifikační cíl. Dva sloupce vlastní spotřeby představují dva scénáře, nikoli garantovaný interval výdrže. Teplota, stárnutí, BMS a špičky mohou výsledek zhoršit.

## Nabíjení podle současného plánu 0,5 A

| Pack a vstup | Bez externí zátěže | Se zátěží |
| --- | --- | --- |
| 2S, 9 V / 3 A | Cca 6,5–8 h | Podobně při 1 W, 5 W i 10 W |
| 4S, 20 V / 2 A | Cca 6,5–8 h | Podobně při 1 W, 5 W, 10 W i 15 W externě |

Stejný proud v ampérech znamená přibližně stejnou dobu pro oba 3Ah sériové packy; 4S potřebuje dvojnásobný nabíjecí výkon.

Časy používají hrubý model `3 Ah / I_charge + 0,5 až 2 h` na konec CC/CV. Konkrétní článek, počáteční SOC, ukončovací proud a teplota jsou pro přesný výsledek nezbytné. Hluboké vybití a přednabíjení model nepokrývá.

## Pack × vstupní profil × zátěž

Každá buňka uvádí **modelový nabíjecí proud · orientační dobu nabíjení**, pokud by byl proud nastaven na tuto hodnotu. Přehled zkoumá dostupný rozpočet až do 1C. S ponechaným limitem V4 0,5 A se všechny vyšší hodnoty omezí na 0,5 A a čas bude přibližně 6,5–8 h. Nižší proudy se nezvýší.

Použité předpoklady: vlastní spotřeba **1,5 W**, účinnost BQ i výstupního měniče **90 %**, využití **90 % jmenovitého vstupního proudu**. Proud je omezen výkonem u plného packu, 3A limitem článků a orientačním součtem SYS + nabíjení nejvýše 5 A na spodní hranici packu.

Jde o výpočetní strop před tolerancemi, nikoli přesné doporučení registru nebo tepelnou kvalifikaci. Při tvrdém limitu článku 3 A musí nominální nastavení zohlednit kladnou toleranci regulace. Režim 1C není změnou schváleného 0,5A plánu.

Časy jsou scénář při konstantním uvedeném proudu, nikoli simulace adaptivního proudu celým cyklem. Adaptivní řízení může část cyklu urychlit, teplotní regulace a lineární režim BATFET jej mohou prodloužit. Pro velmi malé proudy musí odpovídat také ukončovací proud a nabíjecí časovač; výpočet 50 h není příslib autonomního cyklu s výchozí konfigurací IC.

### 2S1P — 3000 mAh

| Vstup přes PD trigger | Bez zátěže | Zátěž 1 W | Zátěž 5 W | Zátěž 15 W¹ |
| --- | --- | --- | --- | --- |
| 5 V / 0,5 A | 0,06 A · 48,5–50,0 h | Vybíjení: 0,59 W | Vybíjení: 5,03 W | Vybíjení: 16,14 W |
| 5 V / 3 A | 1,27 A · 2,9–4,4 h | 1,14 A · 3,1–4,6 h | 0,61 A · 5,4–6,9 h | Vybíjení: 6,02 W |
| 9 V / 3 A | 2,42 A · 1,7–3,2 h | 2,29 A · 1,8–3,3 h | 1,76 A · 2,2–3,7 h | 0,44 A · 7,3–8,8 h |
| 15 V / 3 A | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 2,16 A · 1,9–3,4 h |
| 20 V / 2 A | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 1,69 A · 2,3–3,8 h |
| 20 V / 3 A | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 3,00 A · 1,5–3,0 h | 2,16 A · 1,9–3,4 h |

### 4S1P — 3000 mAh

| Vstup přes PD trigger | Bez zátěže | Zátěž 1 W | Zátěž 5 W | Zátěž 15 W¹ |
| --- | --- | --- | --- | --- |
| 5 V / 0,5 A | <0,05 A² | Vybíjení: 0,59 W | Vybíjení: 5,03 W | Vybíjení: 16,14 W |
| 5 V / 3 A | 0,63 A · 5,2–6,7 h | 0,57 A · 5,8–7,3 h | 0,30 A · 10,4–11,9 h | Vybíjení: 6,02 W |
| 9 V / 3 A | 1,21 A · 3,0–4,5 h | 1,15 A · 3,1–4,6 h | 0,88 A · 3,9–5,4 h | 0,22 A · 14,1–15,6 h |
| 15 V / 3 A | 2,08 A · 1,9–3,4 h | 2,01 A · 2,0–3,5 h | 1,75 A · 2,2–3,7 h | 1,09 A · 3,3–4,8 h |
| 20 V / 2 A | 1,84 A · 2,1–3,6 h | 1,77 A · 2,2–3,7 h | 1,51 A · 2,5–4,0 h | 0,85 A · 4,0–5,5 h |
| 20 V / 3 A | 2,80 A · 1,6–3,1 h | 2,74 A · 1,6–3,1 h | 2,47 A · 1,7–3,2 h | 1,81 A · 2,2–3,7 h |

¹ Externí měnič z VSYS; přesahuje F5 cíl 10 W. U 2S je mimo současný 10W kvalifikační cíl. U 2S/15 W omezuje rychlé nabíjení také společný 5A rozpočet.

² Pro 4S / 5 V / 0,5 A zbývá u plného packu jen cca 31 mA, tedy pod minimální programovatelnou hodnotou ICHG 50 mA. V tomto konzervativním scénáři nelze počítat se souvislým nabíjením až do plna; nižší skutečná režie může výsledek změnit.

**Vybíjení: X W** je chybějící výkon na SYS, který musí dodat baterie, navíc se ztrátami bateriové cesty. Nejde o stav s neměnným SOC.

## Vstupní zdroje a doporučení

| Vstup | Modelový výkon po BQ | Praktické použití |
| --- | ---: | --- |
| 5 V / 0,5 A | 2,03 W | Pouze velmi pomalé nabíjení při dostatečně malé režii |
| 5 V / 3 A | 12,15 W | Malé zátěže; při 10W F5 zátěži konzervativní model zdroj mírně překračuje |
| 9 V / 3 A | 21,87 W | 2S, 10W výstup a nabíjení 0,5 A |
| 15 V / 3 A | 36,45 W | Větší rezerva pro rychlejší nabíjení |
| 20 V / 2 A | 32,40 W | 4S i 15W externí zátěž při nabíjení 0,5 A |
| 20 V / 3 A | 48,60 W | Vyšší výkon a rychlejší nabíjení; 4S 1C se zátěží není zaručeno |

PD trigger přivádí vyjednané napětí do hlavního vstupu J1. Projektový limit zůstává 20 V nominálně / 21 V včetně tolerance. Zdroj i trigger musí zvolený profil skutečně podporovat. 5 V / 500 mA je nízkovýkonový vstupní scénář, nikoli vysokonapěťový PD profil.

## Účinnost a ztráty

Bateriový provoz s jedním výstupním měničem:

| Užitečná zátěž | Ztráta 90% měniče | Celkové ztráty, režie 0,3 / 1,5 W | Účinnost celé UPS, režie 0,3 / 1,5 W |
| --- | ---: | ---: | ---: |
| 1 W | 0,11 W | 0,41 / 1,61 W | 71 / 38 % |
| 5 W | 0,56 W | 0,86 / 2,06 W | 85 / 71 % |
| 15 W | 1,67 W | 1,97 / 3,17 W | 88 / 83 % |

Při provozu ze vstupního zdroje jsou dva konverzní stupně: před vlastní spotřebou přibližně `0,9 × 0,9 = 81 %`. Nabíjení přidává další ztráty. Energie uložená do baterie není tepelná ztráta. Datasheetová účinnost BQ25798 96,5 % při vstupu 20 V / baterii 16 V / nabíjení 3 A platí pouze pro tento konkrétní bod, nikoli pro celou UPS.

## Výpočty a podklady

```text
E_nominal_Wh = N_series × 3,6 V × 3 Ah
E_usable_Wh  = 0,85 × E_nominal_Wh
P_SYS_W     = P_load_W / 0,90 + P_aux_W
t_runtime_h = E_usable_Wh / P_SYS_W
P_source_W  = V_source × (0,90 × I_source_rated) × 0,90
I_charge_A  = min(3 A,
                  max(0, P_source_W − P_SYS_W) / V_pack_full,
                  5 A − P_SYS_W / V_pack_low)
t_charge_h  = 3 Ah / I_charge_A + 0,5 až 2 h
P_loss_W    = P_SYS_W − P_load_W
eta_total   = P_load_W / P_SYS_W
```

Výpočet proudu není platný jako souvislé nabíjení pro hodnoty pod minimálním ICHG. Při záporném výkonovém zůstatku se uvádí deficit krytý baterií.

- [V4_REQUIREMENTS.md](V4_REQUIREMENTS.md), R03–R06: packy, proudy, cíle, 0,5A plán, režie a účinnosti; při obnově znovu ověřeny relevantní požadavky.
- [V4_ARCHITECTURE.md](V4_ARCHITECTURE.md), A08: projektový cíl F5 2 A.
- [První napájení — technické poznámky](evidence/FIRST_MAIN_POWER_F5_TECHNICAL_NOTES_2026-11-06.md): BQ25798 / R5 27 kΩ = 4S, F5 nominálně 5,0525 V podle osazení.
- [TI BQ25798, SLUSDV2C, rev. C, červen 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf), §6.3, §6.5, §7.3.8: limity IC, SYS, NVDC a sdílení výkonu.
- [TI TPS62933, SLUSEA4D, rev. D, srpen 2022](https://www.ti.com/lit/ds/symlink/tps62933.pdf), §8–9: proudová třída IC a účinnost.

Dokumentační obnova bez změn CAD, firmware nebo hardwaru. K určení skutečných typických a garantovaných parametrů chybí konkrétní článek/BMS, vlastní odběr, účinnostní křivky, teplotní/zátěžová měření a externí měnič pro 15 W.
