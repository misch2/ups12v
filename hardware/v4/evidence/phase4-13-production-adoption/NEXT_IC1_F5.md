# Návrh dalšího checkpointu po Phase4.13

**Pouze návrh pro vlastníka; žádný z níže uvedených spojů nebyl nyní routován.**
Výchozí stav: přijatá produkce Phase4.13,44opens,0physical DRC/0parity/ERC0.
USB je přijaté pro prototyp a zůstává beze změny.

## Nejprve tři zbývající IC1 F0 escapes

| Síť | IC1 pad / poloha mm | Existující cílová síť |
|---|---|---|
| I2C_SCL |14 / (60.600,67.900) | Již routovaný kmen k R21.2, U6.2 a J4.4 |
| ~INT |21 / (61.900,65.600) | Již routovaný kmen k R28.2, R29.1 a J4.6 |
| STAT |1 / (58.100,64.400) | Již routovaná síť D2.1 |

Navržený malý rozsah: připojit pouze tyto tři fyzické pady k jejich existujícím
ostrovům. Konkrétní vrstvy, připojovací body, šířky a případné prokovy se mají
zvolit až po čerstvém nativním snapshotu a lokální clearance/drill kontrole;
souřadnice v tabulce nejsou hotový route plan. Zachovat IC1/L1 silové cesty,
switching/BTST/REGN/BATP/feedback/bypass okolí, skutečnou In1 referenci, USB,
NT izolaci, RF keepout a všechny rezervace F5.
Osm existujících nativních oblouků zachovat beze změny. Starší straight-only
helpery je odmítají; případná příprava routingu musí využít jejich skutečné
exportované měděné polygony, bez nahrazení oblouků přibližnými úsečkami.

Před produkčním zápisem vytvořit izolovaný úplný kandidát; potom nativní
save/reload/refill, ERC/DRC/parity a všechny473 padové ostrovy. Očekávaný výsledek
je **41 opens, výhradně dosavadní F5**, bez nového spojení či rozštěpení mimo
tři zamýšlená uzavření. Po úspěchu aktualizovat manifest a STOP pro review.
Žádný nový obvod, komponenta, pravidlo nebo historický cleanup není součástí
tohoto návrhu.

## Potom samostatný F5 power-stage milestone

F5 řešit až po přijetí IC1 checkpointu a samostatném schválení jeho rozsahu.
Nejprve navrhnout související silové/switching, bootstrap, feedback a lokální
bypass/return trasy jako celek v již schválené architektuře a BOM variantě.
Současných41 F5 opens není oprávnění routovat je v IC1 milestone.
Vyžadovat vlastní izolovaný kandidát, kontrolu skutečné mědi/drillů a PGND,
ERC/DRC/parity, úplnou konektivitu a další owner checkpoint. Výrobní a HW
power-up kvalifikační brány zůstávají samostatné.

Pro oba budoucí milníky použít
[Phase4.13 accepted-installed-baseline.json](accepted-installed-baseline.json).
Původní owner scratch ani starší add-only plány nereplayovat.
