#!/usr/bin/env python3
"""Tests for the agent-based contact importer."""

import json
import os
import unittest
from unittest.mock import Mock, patch
from agent_approach import ContactStorage, AgentContactImporter


class TestContactStorage(unittest.TestCase):
    """Test the business logic storage tool."""
    
    def setUp(self):
        self.storage = ContactStorage()
    
    def test_file_contact_with_full_name_and_email(self):
        """Test filing a contact with full name and email."""
        result = self.storage.file_contact("John Doe", email="john@example.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Filed contact: John Doe")
        self.assertEqual(result["contact"]["first_name"], "John")
        self.assertEqual(result["contact"]["last_name"], "Doe")
        self.assertEqual(result["contact"]["email"], "john@example.com")
        
        # Check it was stored
        contacts = self.storage.get_contacts()
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["first_name"], "John")
    
    def test_file_contact_with_single_name_and_phone(self):
        """Test filing a contact with single name and phone."""
        result = self.storage.file_contact("Jane", phone="555-123-4567")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["contact"]["first_name"], "Jane")
        self.assertIsNone(result["contact"]["last_name"])
        self.assertEqual(result["contact"]["phone"], "555-123-4567")
    
    def test_file_contact_with_both_email_and_phone(self):
        """Test filing a contact with both email and phone."""
        result = self.storage.file_contact(
            "Jane Smith", 
            email="jane@test.org", 
            phone="555-987-6543"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["contact"]["email"], "jane@test.org")
        self.assertEqual(result["contact"]["phone"], "555-987-6543")
    
    def test_file_contact_requires_name(self):
        """Test that name is required."""
        result = self.storage.file_contact("", email="test@example.com")
        
        self.assertFalse(result["success"])
        self.assertIn("Name is required", result["error"])
    
    def test_file_contact_requires_email_or_phone(self):
        """Test that either email or phone is required."""
        result = self.storage.file_contact("John Doe")
        
        self.assertFalse(result["success"])
        self.assertIn("Either email or phone is required", result["error"])
    
    def test_clear_contacts(self):
        """Test clearing all contacts."""
        self.storage.file_contact("John Doe", email="john@example.com")
        self.assertEqual(len(self.storage.get_contacts()), 1)
        
        self.storage.clear_contacts()
        self.assertEqual(len(self.storage.get_contacts()), 0)


class TestAgentContactImporter(unittest.TestCase):
    """Integration tests for the agent-based contact importer using real OpenAI API."""
    
    def setUp(self):
        # Check if we have an API key for integration tests
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.skipTest("OPENAI_API_KEY not found - skipping integration tests")
        
        self.importer = AgentContactImporter()
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                AgentContactImporter()
    
    def test_import_standard_csv_integration(self):
        """Integration test: Import standard CSV with real OpenAI API."""
        csv_data = """First Name,Last Name,Email,Phone
John,Doe,john@example.com,555-123-4567
Jane,Smith,jane@test.org,555-987-6543"""
        
        result = self.importer.import_contacts(csv_data, "Import standard contact list")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that contacts were actually filed
        contacts = self.importer.get_contacts()
        self.assertEqual(len(contacts), 2)
        
        # Verify contact data
        names = [f"{c['first_name']} {c['last_name']}" for c in contacts]
        self.assertIn("John Doe", names)
        self.assertIn("Jane Smith", names)
    
    def test_import_international_csv_integration(self):
        """Integration test: Import international CSV format."""
        csv_data = """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567
María,López,maria@test.es,+34 93 987 6543"""
        
        result = self.importer.import_contacts(csv_data, "Import Spanish contact list")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that contacts were filed
        contacts = self.importer.get_contacts()
        self.assertEqual(len(contacts), 2)
        
        # Should handle Spanish names
        names = [f"{c['first_name']} {c['last_name']}" for c in contacts]
        self.assertIn("Luis García", names)
        self.assertIn("María López", names)
    
    def test_import_pipe_delimited_integration(self):
        """Integration test: Import pipe-delimited CSV without headers."""
        csv_data = """John Doe|john@example.com|555-123-4567
Jane Smith|jane@test.org|555-987-6543"""
        
        result = self.importer.import_contacts(csv_data, "Import pipe-delimited data without headers")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that contacts were filed
        contacts = self.importer.get_contacts()
        self.assertEqual(len(contacts), 2)
        
        # Should extract names and emails correctly
        emails = [c['email'] for c in contacts if c['email']]
        self.assertIn("john@example.com", emails)
        self.assertIn("jane@test.org", emails)
    
    def test_import_mixed_format_integration(self):
        """Integration test: Import CSV with mixed data in fields."""
        csv_data = """Contact,Primary Info,Notes
John Doe,john@example.com,Phone: 555-123-4567 Company: Acme
Jane Smith,Call 555-987-6543,Email: jane@test.org"""
        
        result = self.importer.import_contacts(csv_data, "Import contacts with mixed data in notes")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that contacts were filed
        contacts = self.importer.get_contacts()
        self.assertEqual(len(contacts), 2)
        
        # Should extract data from mixed fields
        names = [f"{c['first_name']} {c['last_name']}" for c in contacts]
        self.assertIn("John Doe", names)
        self.assertIn("Jane Smith", names)
    
    def test_unexpected_format_integration(self):
        """Integration test: Agent handles completely unexpected CSV format."""
        # Test handling of completely unexpected CSV format
        csv_data = """"Contact Info","Details","Extra"
"Smith, Jane (Manager)","jane.smith@company.com | Mobile: +1-555-0123","Dept: Sales, Start: 2020"
"Rodriguez, Carlos","carlos.r@email.com Phone: 555.987.6543","Engineering Team Lead\""""
        
        result = self.importer.import_contacts(csv_data, "Import contacts from messy legacy system export")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that contacts were filed despite the unexpected format
        contacts = self.importer.get_contacts()
        self.assertEqual(len(contacts), 2)
        
        # Should handle names with titles and extract emails from mixed fields
        names = [f"{c['first_name']} {c['last_name']}" for c in contacts]
        emails = [c['email'] for c in contacts if c['email']]
        
        # Should extract Jane Smith and Carlos Rodriguez
        self.assertTrue(any("Jane" in name for name in names))
        self.assertTrue(any("Carlos" in name for name in names))
        
        # Should extract emails from mixed delimiter fields
        self.assertTrue(any("jane.smith@company.com" in email for email in emails))
        self.assertTrue(any("carlos.r@email.com" in email for email in emails))
    
    def test_agent_uses_file_contact_tool(self):
        """Integration test: Verify agent actually uses the file_contact tool."""
        csv_data = """Name,Email
Test User,test@example.com"""
        
        # Track tool usage by monitoring the storage
        initial_count = len(self.importer.get_contacts())
        
        result = self.importer.import_contacts(csv_data, "Import simple contact")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Verify the file_contact tool was actually called
        final_count = len(self.importer.get_contacts())
        self.assertGreater(final_count, initial_count, "Agent should have filed contacts using the tool")
        
        # Verify the contact was filed correctly
        contacts = self.importer.get_contacts()
        self.assertTrue(any("Test User" in f"{c['first_name']} {c['last_name']}" for c in contacts))


if __name__ == "__main__":
    unittest.main()