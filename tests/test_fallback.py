import unittest
from unittest.mock import patch
from transport import SourceError
import core

class FallbackTest(unittest.TestCase):
    @patch("core.request_json")
    def test_switches_overpass_endpoint(self, fetch):
        fetch.side_effect=[SourceError("timed out"),{"elements":[]}]
        result=core.partner_leads("6.9271,79.8612")
        self.assertEqual(fetch.call_count,2)
        self.assertEqual(result["count"],0)
        self.assertEqual(result["overpass_endpoint"],core.OSM_FALLBACK)
if __name__=="__main__":unittest.main()
