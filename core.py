"""Two source-grounded pipelines: EU tender discovery and OSM community leads."""
from __future__ import annotations
import re
from transport import request_json, SourceError

SERVICES = ["TenderPilot","ZeroWaste"]
TED="https://api.ted.europa.eu/v3/notices/search"
OSM="https://overpass-api.de/api/interpreter"

def _text(value):
    if isinstance(value, dict):
        return next(iter(value.values()), "")
    if isinstance(value, list):
        return ", ".join(map(_text, value[:3]))
    return str(value or "")

def tenders(keyword: str):
    """Official TED expert full-text search. No eligibility claims."""
    if not 2 <= len(keyword.strip()) <= 100 or not re.fullmatch(r"[\w ,.-]+", keyword, re.UNICODE):
        raise ValueError("Tender keyword must be 2–100 letters, numbers, spaces or punctuation.")
    # Source Agent: bounded expert query, with user input sanitized to prevent query injection.
    phrase=keyword.strip().replace('"',"")
    payload={"query":'FT~("'+phrase+'")',"fields":["publication-number","notice-title","buyer-name","publication-date"],
             "limit":10,"page":1}
    data=request_json(TED,payload=payload)
    hits=data.get("notices", data.get("results", []))
    if not isinstance(hits,list):
        raise SourceError("TED search returned an unexpected JSON format.")
    rows=[]
    for item in hits[:10]:
        if not isinstance(item, dict):
            continue
        number=_text(item.get("publication-number") or item.get("publicationNumber"))
        if not number:
            continue
        rows.append({"number":number,"title":_text(item.get("notice-title") or item.get("title")),
                     "buyer":_text(item.get("buyer-name")),
                     "published":_text(item.get("publication-date")),
                     "source_url":"https://ted.europa.eu/en/notice/"+number})
    return {"project":"TenderPilot","keyword":keyword,"count":len(rows),"opportunities":rows,
        "source":TED,"stages":["Discovery: TED search","Analysis: normalize buyer/title","Verification: publication identifier","Report: candidate shortlist"],
        "limitations":["Not checked for eligibility, deadline or procurement compliance.","Read the complete official notice before bidding.","Coverage: EU TED only, not Sri Lankan procurement."]}

def partner_leads(location: str):
    """Query OpenStreetMap for nearby food banks/community facilities: NOT confirmed partners."""
    match=re.fullmatch(r"\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\s*", location)
    if not match:
        raise ValueError("Enter latitude,longitude (e.g. 6.9271,79.8612).")
    lat,lon=map(float,match.groups())
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("Latitude/longitude out of range.")
    # Restrict to a modest 3 km radius and capped output to respect public Overpass.
    q=f'[out:json][timeout:15];(nwr(around:3000,{lat:.5f},{lon:.5f})["social_facility"="food_bank"];nwr(around:3000,{lat:.5f},{lon:.5f})["amenity"="community_centre"];);out center 30;'
    # Overpass supports GET query string data; caller cannot supply arbitrary QL.
    data=request_json(OSM,params={"data":q})
    rows=[]
    for e in data.get("elements",[])[:30]:
        tag=e.get("tags") or {}
        if not e.get("id"):
            continue
        rows.append({"name":tag.get("name","Unnamed mapped facility"),
                     "type":tag.get("social_facility") or tag.get("amenity","other"),
                     "lat":e.get("lat") or (e.get("center") or {}).get("lat"),
                     "lon":e.get("lon") or (e.get("center") or {}).get("lon"),
                     "source_url":f'https://www.openstreetmap.org/{e.get("type","node")}/{e["id"]}',
                     "partner_verified":False})
    return {"project":"ZeroWaste","query":location,"candidate_facilities":rows,
        "count":len(rows),"source":"OpenStreetMap / Overpass","stages":["Discovery: mapped facilities","Analysis: nearby locations","Verification: mapping source","Report: outreach shortlist"],
        "limitations":["These are mapped places, NOT verified willing food recipients.","Never arrange food transfer without partner consent and safe handling checks.","No live surplus supply, logistics or routing integration yet."]}

def run(query: str, service: str="TenderPilot"):
    if service=="TenderPilot": return tenders(query)
    if service=="ZeroWaste": return partner_leads(query)
    raise ValueError("Unknown service.")

if __name__=="__main__":
    import argparse,json
    ap=argparse.ArgumentParser()
    ap.add_argument("service",choices=SERVICES)
    ap.add_argument("query")
    a=ap.parse_args()
    try: print(json.dumps(run(a.query,a.service),indent=2))
    except (ValueError,SourceError) as exc: ap.exit(2,str(exc)+"\n")
