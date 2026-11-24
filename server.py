from fastmcp import FastMCP
from core import tenders,partner_leads
mcp=FastMCP("MUHRIS TenderPilot and ZeroWaste")
@mcp.tool
def find_eu_tenders(keyword: str)->dict:
    """Discover publicly published EU TED notices without claiming business eligibility."""
    return tenders(keyword)
@mcp.tool
def find_food_bank_leads(latitude: float, longitude: float)->dict:
    """Find mapped nearby social facilities. Consent and food acceptance NOT verified."""
    return partner_leads(str(latitude)+","+str(longitude))
if __name__=="__main__":mcp.run()
