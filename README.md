# TenderPilot + ZeroWaste · Source-grounded prototypes

Two read-only workflows in one repository. Both have a local web dashboard and FastMCP tools.

### TenderPilot
Find EU procurement notices via the official, anonymous [TED Search API](https://docs.ted.europa.eu/api/latest/search.html). Normalizes notice titles, buyer and publication ID. Eligibility, contracting rules and deadlines **must be checked by a human**.

```bash
python core.py TenderPilot "software"
```

### ZeroWaste
Locate potential outreach leads (mapped community centers or food-bank facilities) near a coordinate using crowdsourced [OpenStreetMap / Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API).

```bash
python core.py ZeroWaste "6.9271,79.8612"
```

A mapped location **is not a confirmed food recipient or consenting partner**. This prototype cannot arrange, verify, or coordinate donations.

### Demo and tests
```bash
python dashboard.py --port 8765
python -m unittest discover -s tests -v
pip install -r requirements.txt
python server.py
```
FastMCP is optional; stdio by default, or `fastmcp run server.py:mcp --transport http --port 8000`. Production HTTP transport requires access control. All source APIs may impose usage limits.

The pipeline is discovery → normalization → provenance checks → source-linked report → human decision. No autonomous business decision or LLM orchestrator is claimed.
