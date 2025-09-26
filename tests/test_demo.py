#!/usr/bin/env python3
"""Integration tests for the demo script."""

import unittest
import os
from unittest.mock import patch
from demo import run_demo


class TestDemoIntegration(unittest.TestCase):
    """Integration tests for the demo functionality."""
    
    def test_demo_runs_without_api_key(self):
        """Test that demo runs gracefully without OpenAI API key."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise an exception
            try:
                run_demo()
            except Exception as e:
                self.fail(f"Demo should run without API key, but raised: {e}")
    
    def test_demo_runs_with_real_api_key(self):
        """Integration test: Demo runs with real OpenAI API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.skipTest("OPENAI_API_KEY not found - skipping integration test")
        
        # Should not raise an exception and should make real API calls
        try:
            run_demo()
        except Exception as e:
            self.fail(f"Demo should run with real API key, but raised: {e}")
    
    def test_traditional_approach_works_independently(self):
        """Test that traditional approach works without any API dependencies."""
        from traditional_approach import TraditionalContactImporter
        
        importer = TraditionalContactImporter()
        csv_data = """First Name,Last Name,Email
John,Doe,john@example.com
Jane,Smith,jane@test.org"""
        
        contacts = importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["first_name"], "John")
        self.assertEqual(contacts[0]["email"], "john@example.com")
    
    def test_agent_approach_works_with_api_key(self):
        """Test that agent approach works with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.skipTest("OPENAI_API_KEY not found - skipping agent test")
        
        from agent_approach import AgentContactImporter
        
        importer = AgentContactImporter()
        csv_data = """Name,Email
Test User,test@example.com"""
        
        result = importer.import_contacts(csv_data, "Test import")
        
        # Should get a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Should have filed the contact
        contacts = importer.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertTrue("Test User" in f"{contacts[0]['first_name']} {contacts[0]['last_name']}")


if __name__ == "__main__":
    unittest.main()