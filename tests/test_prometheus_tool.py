import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.prometheus import PrometheusClient
from core.tools import extract_service_name, get_service_health, run_tools


class TestPrometheusIntegration(unittest.TestCase):

    def test_extract_service_name(self):
        self.assertEqual(extract_service_name("why is checkout slow"), "checkout")
        self.assertEqual(extract_service_name("AUTH service error rate"), "auth")
        self.assertEqual(extract_service_name("payments processing delay"), "payments")
        self.assertEqual(extract_service_name("something completely unknown"), "unknown")

    def test_get_service_health_structure(self):
        res = get_service_health("checkout")
        self.assertIn("service", res)
        self.assertIn("status", res)
        self.assertIn("latency", res)
        self.assertIn("error_rate", res)
        self.assertIn("source", res)
        self.assertEqual(res["service"], "checkout")
        self.assertEqual(res["source"], "prometheus")

    @patch("requests.get")
    def test_prometheus_unreachable_fallback(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        client = PrometheusClient(base_url="http://invalid-host:9090")
        res = client.fetch_service_health("checkout")

        self.assertEqual(res["service"], "checkout")
        self.assertEqual(res["status"], "error")
        self.assertIn("Failed to connect", res["error"])

    @patch.object(PrometheusClient, "query")
    def test_prometheus_healthy_response(self, mock_query):
        def mock_prom_query(promql):
            if "up" == promql:
                return {"result": [{"metric": {"job": "checkout"}, "value": [1600000000, "1"]}]}
            if "duration" in promql:
                return {"result": [{"value": [1600000000, "0.12"]}]}
            if "requests_total" in promql:
                return {"result": [{"value": [1600000000, "0.5"]}]}
            return None

        mock_query.side_effect = mock_prom_query
        client = PrometheusClient()
        res = client.fetch_service_health("checkout")

        self.assertEqual(res["service"], "checkout")
        self.assertEqual(res["latency"], "120ms")
        self.assertEqual(res["error_rate"], "0.5%")
        self.assertEqual(res["status"], "healthy")

    def test_run_tools_langgraph_node(self):
        state = {"question": "why is checkout failing?"}
        output = run_tools(state)
        self.assertIn("tool_results", output)
        self.assertEqual(output["tool_results"]["service"], "checkout")


if __name__ == "__main__":
    unittest.main()
