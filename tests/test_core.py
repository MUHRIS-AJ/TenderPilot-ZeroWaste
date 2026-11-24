import unittest
from unittest.mock import patch
import core
class WorkflowTests(unittest.TestCase):
    @patch("core.request_json")
    def test_ted(self, request):
        request.return_value={"notices":[{"publication-number":"123456-2026","notice-title":{"eng":"Computer services"},"buyer-name":"Local Council"}]}
        result=core.run("software","TenderPilot")
        self.assertEqual(result["count"],1)
        self.assertIn("ted.europa.eu",result["opportunities"][0]["source_url"])
        self.assertIn("FT~",request.call_args.kwargs["payload"]["query"])
    @patch("core.request_json")
    def test_osm(self, request):
        request.return_value={"elements":[{"type":"node","id":123,"lat":6.9,"lon":79.8,"tags":{"name":"Community A","amenity":"community_centre"}}]}
        result=core.run("6.9,79.8","ZeroWaste")
        self.assertEqual(result["count"],1)
        self.assertFalse(result["candidate_facilities"][0]["partner_verified"])
    def test_reject_query_injection(self):
        with self.assertRaises(ValueError):core.tenders('software") OR ("x')
        with self.assertRaises(ValueError):core.partner_leads("999,999")
if __name__=="__main__":unittest.main()
