import json
import os
import sys

# Mocking parts of the LinkedInSimulationRunner to test logic
class MockLinkedInSimulationRunner:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
    def test_logic(self):
        enabled = self.config.get("enable_linkedin_connections", False)
        if enabled:
            return "LOGIC ACTIVE: Establishing professional network connections..."
        else:
            return "LOGIC INACTIVE: LinkedIn professional connection logic is disabled."

print("Testing with ON config:")
runner_on = MockLinkedInSimulationRunner(r"C:\Users\HP\Downloads\MiroFish\tmp\test_config_on.json")
print(runner_on.test_logic())

print("\nTesting with OFF config:")
runner_off = MockLinkedInSimulationRunner(r"C:\Users\HP\Downloads\MiroFish\tmp\test_config_off.json")
print(runner_off.test_logic())
