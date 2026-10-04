import unittest
import json
from tools import dispatch_tool, AVAILABILITY

class TestAssignmentTools(unittest.TestCase):
    
    def setUp(self):
        # Reset Monday's rooms to a known state for reliable assertions
        AVAILABILITY["Monday"] = ["214", "216", "220"]

    def test_nonexistent_tool_rejection(self):
        """CRITICAL: Verifies a tool name is checked against allowed list before lookups."""
        result = dispatch_tool("wipe_all_data", '{"confirm": true}')
        self.assertIn("Error:", result)
        self.assertIn("not an authorized or existing tool", result)

    def test_malformed_json_arguments(self):
        """Ensures that malformed/broken JSON syntax does not crash your agent workflow."""
        result = dispatch_tool("check_availability", '{"day": "Monday"') # Missing closing brace
        self.assertIn("Error:", result)
        self.assertIn("were not valid JSON", result)

    def test_type_error_parameter_drift(self):
        """Ensures that parameter signature mismatches are handled gracefully."""
        result = dispatch_tool("check_availability", '{"invalid_key": "Monday"}')
        self.assertIn("Error:", result)
        self.assertIn("argument mismatch or invalid structure", result)

    def test_successful_read_path(self):
        """Validates functional happy path for read-only lookups."""
        result = dispatch_tool("check_availability", '{"day": "Monday"}')
        self.assertIn("Available rooms on Monday:", result)

if __name__ == "__main__":
    unittest.main()
