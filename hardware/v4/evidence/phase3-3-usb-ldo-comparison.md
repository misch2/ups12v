# Bounded service-USB regulator comparison — 2026-10-10

> HISTORICAL / SUPERSEDED: the owner subsequently selected a normal buck and service USB LDO. AP7361C-33E-13 selection is recorded in phase3-4-usb-ldo-selection.md. The old retain-buck decision below is not current authority.

Decision: retain existing U4 TPS62933. No CAD replacement or new assembly variant. USB-only programming has no measured current trace yet; Wi-Fi is excluded. A 3 A buck rating does not establish USB allowance or successful ROM flashing.

Manufacturer source checked 2026-10-10: [Diodes AP2112 DS39724 Rev. 2-2, June 2017](https://www.diodes.com/datasheet/download/AP2112.pdf), pp.3/8: 600 mA rating, SOT25 thermal resistance 184 C/W without heatsink; 3.3 V dropout maximum 400 mV at 600 mA; recommended input 2.5–6 V. AP2112K-3.3 is a comparison candidate, not a selected/order-qualified part.

Calculated screen at 5.25 V input, 3.3 V output (USB high-voltage planning assumption, not a measured source):

| Output current | LDO loss `(5.25−3.3) I` | Temperature rise at 184 C/W |
| --- | ---: | ---: |
| 100 mA | 0.195 W | 35.9 C |
| 300 mA | 0.585 W | 107.6 C |
| 500 mA | 0.975 W | 179.4 C |

These are first-order steady-state estimates; PCB copper/enclosure/ambient change them. The 500 mA requirement cannot be inferred safe from the small-package current rating. At an assumed 50 C ambient and the 150 C absolute junction limit, this model allows only about 279 mA, with no reliability margin. A larger thermal package could work but has no demonstrated advantage for this checkpoint.

USB current also matters: with a 100 mA input allowance at 4.75 V, an assumed 90%-efficient buck has an upper bound about 130 mA at 3.3 V; an LDO about 100 mA, before interface consumption/quiescent current. Neither calculation proves ROM load fits. A 500 mA output draws approximately 386 mA at 4.75 V with that buck-efficiency assumption, versus approximately 500 mA for an LDO. Respect the actual port/configuration allowance and measure cold-start/inrush and ROM peaks later. No efficiency or current measurement is claimed.

Keep the reverse-blocking mux with either regulator. The smaller LDO part count alone does not justify changing a retained circuit before current/thermal benefit is established.
