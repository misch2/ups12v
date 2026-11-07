# Phase5.2 evidence method and limitations

2026-10-19, Europe/Prague. Entry branch codex/v4-phase5-component-sourcing.
Entry sourcing directory and active BOM/handover copied before edits.196protected
CAD/library/manufacturing hashes matched the accepted Phase5.1 manifest at entry.
No CAD/nativeKiCad process launched, source export regenerated or editor changed.

Manufacturer and supplier pages were read with the web tool. Complete returned
responses, including provider cache ages and failures, are saved as TXT files.
refresh_phase5_2.py parses these saved observations offline; it is not a live API.
phase5_2_reviewed_overrides.json makes reviewed exceptions explicit. Re-running
the parser changes documentary JSON/CSVs only and cannot reserve stock/order.
No stock count in this evidence is described as guaranteed current inventory.

Konnect catalog availability was checked. Its JLCPCB search reported no local
database. No database download or assembly-library-only selection was made;
exact manufacturer/distributor pages were used instead. Native CAD APIs were
unnecessary for procurement-only analysis.

TDK direct characteristic-PDF web access failed; a direct requests download first
failed sandbox DNS, then the approved network execution returned HTTP403. The
official product page was opened in a temporary hidden browser. Its DC Bias
Characteristic → Download data as CSV control yielded tdk_graph.csv in Downloads,
copied unchanged to TDK-C3216X5R1V226M160AC-dcbias.csv in this evidence folder.
The file identifies the exact160ACpart,DC/V,Capacitance(Nom.)/F and creation date
19October2026GMT. Source:
https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X5R1V226M160AC
The visible page explicitly labels characteristic graphs non-guaranteed reference
data. FullTJ00E manufacturer query failed502; alternativeC32TDKquery timed out.
No equivalence or betterC32effective capacitance was inferred from those failures.

Existing AOSRev3.1PDF and Murata12/2020ECsheet were rendered locally only for table/
curve inspection. New raster copies are evidence, not edited manufacturer sources.
The AOS55°Cleakage condition and µA units were visually verified; Murata's typical
data disclaimer,ACmeasurement conditions and dimensions were read. No electrical
measurement or simulation was performed. Calculation assumptions are explicit in
PHASE5_2_COMPATIBILITY_REVIEW.md. TDK3.3Vcapacitance uses linear interpolation of
3.15/4Vexported points, not an independently measured point.

Read-only pad/net constraints reuse Phase4.21snapshot/layout and Phase4.17netlist;
the Phase5.1accepted-export-pad-fit.json carries the targeted land dimensions.
Later accepted source changes were paste-only; current196filemanifest preserved.
Euclidean pad distances are not routed-loop inductance. No new sourceCADparsing,
mutation, nativeassertion/IPCoperation, ERC/DRC or firmware build was involved.

write-like-me retrieval returned no suitable prose references; existing project
report conventions and explicit owner instructions were used. No writing samples
were saved or used as factual engineering evidence.

Independent documentary verification checks authoritativeF0/F5coverage,670fitted,
one reference/group,all6five-board splits,R5options,IC1exact5,DNP/feature exclusions,
spare/MOQ/costmath,harnesscapacity,only3newapprovedreferencesfor2identities,
originalMPNtraceability,unapprovedcandidate exclusion,groupedchecklist and196hashes.
Its PASS means purchasing-data consistency/preservation, not electrical approval,
complete qualification, current inventory, delivered cost or purchase release.
No supplier message, cart, checkout, order, assembly, power-up, commit or push.
