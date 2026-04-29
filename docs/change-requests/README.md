## Design Change Requests

This directory holds Design Change Requests (DCRs) — the entry point for any
design update arriving after initial source ingestion. See ADR-0002 for the
governing protocol.

Each DCR file is named `DCR-NNNN-<slug>.md` and carries a metadata table at
the top with: Status, Classification, Submitted, Submitted by, Decided by,
Decided on, Confidence.

Classification is one of: implement-now, defer, spike, reject, needs-adr.

A task context pack derived from a DCR must cite the DCR ID and may only be
created once the DCR is in an implementation-eligible state.
