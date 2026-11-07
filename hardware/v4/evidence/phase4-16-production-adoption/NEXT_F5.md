# Návrh Phase4.17 — F5 routing

**Pouze návrh; STOP pro owner review před implementací F5.**

Výchozí stav: přijatá produkce Phase4.16, PCB SHA256
`bce08349485b0f8d53060fcc9ef1a3911eaabf0408de16b288d0655e30754899`;
[přijatý manifest](accepted-installed-baseline.json). Zbývá41nepropojení F5,
F0=0; žádné fyzické DRC/parity/ERC chyby.

Po samostatném schválení navrhuji nejprve izolovaný kompletní kandidát F5:

1. Z aktuálního schématu, schválené architektury/BOM variant a čerstvého nativního
   snapshotu vymezit F5 silové, switching, bootstrap, feedback, řízení a lokální
   bypass/PGND návratové cesty. Před routováním porovnat s již přijatými požadavky
   a příslušným existujícím doporučeným layoutem výrobce.
2. Routovat související F5 cesty jako celek v nové izolované kopii. Zachovat
   přijaté IC1/BATTERY/USB, síťové oddělení, skutečnou PGND měď a ostatní produkční
   geometrii. Nutný přesun komponent nebo změnu mimo F5 nejprve předložit vlastníkovi.
3. Kandidát ověřit nativním refill/save/reload, ERC/DRC/paritou a kompletní
   konektivitou všech473padů; zkontrolovat skutečné měděné/drill clearances,
   silové smyčky a PGND návraty. Cílem je uzavřít všech41F5nepropojení bez ztráty
   předchozích spojení a bez nových fyzických chyb.

Poté předložit kandidát a jeho konkrétní geometrické/elektrické kvalifikace
pro owner review; produkční instalace F5 je další samostatně schvalovaný krok.
Tento návrh neopravňuje měnit CAD, BOM/pravidla, provádět legacy cleanup,
vyrábět, nakupovat, zapínat hardware ani měnit firmware.
