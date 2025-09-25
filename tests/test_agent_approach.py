#!/usr/bin/env python3
"""Tests for the agent-based contact importer."""

import json
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from agent_approach import ContactTools, AgentContactImporter


class TestContactTools(unittest.TestCase):
    """Test the business logic tools."""
    
    def setUp(self):
        self.tools = ContactTools()
    
    def test_parse_csv_with_headers(self):
        """Test CSV parsing with headers."""
        csv_data = """First Name,Last Name,Email
John,Doe,john@example.com
Jane,Smith,jane@test.org"""
        
        result = self.tools.parse_csv(csv_data)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["has_headers"])
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0]["first name"], "John")
        self.assertEqual(result["rows"][0]["email"], "john@example.com")
    
    def test_parse_csv_without_headers(self):
        """Test CSV parsing without headers."""
        csv_data = """John Doe,john@example.com,555-123-4567
Jane Smith,jane@test.org,555-987-6543"""
        
        result = self.tools.parse_csv(csv_data)
        
        self.assertTrue(result["success"])
        self.assertFalse(result["has_headers"])
        self.assertEqual(result["delimiter"], ",")
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0]["column_0"], "John Doe")
        self.assertEqual(result["rows"][0]["column_1"], "john@example.com")
    
    def test_parse_csv_pipe_delimiter(self):
        """Test CSV parsing with pipe delimiter."""
        csv_data = """John Doe|john@example.com|555-123-4567
Jane Smith|jane@test.org|555-987-6543"""
        
        result = self.tools.parse_csv(csv_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["delimiter"], "|")
        self.assertEqual(result["rows"][0]["column_0"], "John Doe")
    
    def test_normalize_contact_with_separate_names(self):
        """Test contact normalization with separate first/last name fields."""
        row = {
            "first name": "John",
            "last name": "Doe", 
            "email": "john@example.com",
            "phone": "555-123-4567",
            "company": "Acme Corp"
        }
        
        result = self.tools.normalize_contact(row)
        
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")
        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(result["phone"], "(555) 123-4567")
        self.assertEqual(result["company"], "Acme Corp")
    
    def test_normalize_contact_with_full_name(self):
        """Test contact normalization with full name field."""
        row = {
            "full name": "John Doe",
            "email address": "john@example.com",
            "work phone": "(555) 123-4567"
        }
        
        result = self.tools.normalize_contact(row)
        
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")
        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(result["phone"], "(555) 123-4567")
    
    def test_normalize_contact_international(self):
        """Test contact normalization with international field names."""
        row = {
            "nombre": "Luis",
            "apellidos": "García",
            "correo": "luis@empresa.es",
            "teléfono": "+34 91 123 4567"
        }
        
        result = self.tools.normalize_contact(row)
        
        self.assertEqual(result["first_name"], "Luis")
        self.assertEqual(result["last_name"], "García")
        self.assertEqual(result["email"], "luis@empresa.es")
        self.assertEqual(result["phone"], "+34 91 123 4567")
    
    def test_normalize_contact_mixed_data(self):
        """Test contact normalization with mixed data in fields."""
        row = {
            "contact": "John Doe",
            "primary info": "john@example.com",
            "notes": "Phone: 555-123-4567 Company: Acme"
        }
        
        result = self.tools.normalize_contact(row)
        
        self.assertEqual(result["first_name"], "John")
        self.assertEqual(result["last_name"], "Doe")
        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(result["phone"], "(555) 123-4567")
    
    def test_format_contacts(self):
        """Test contact formatting."""
        contacts = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "(555) 123-4567",
                "company": "Acme Corp"
            }
        ]
        
        result = self.tools.format_contacts(contacts)
        
        # Should be valid JSON
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["first_name"], "John")
    
    def test_detect_delimiter(self):
        """Test delimiter detection."""
        self.assertEqual(self.tools._detect_delimiter("a,b,c"), ",")
        self.assertEqual(self.tools._detect_delimiter("a;b;c"), ";")
        self.assertEqual(self.tools._detect_delimiter("a\tb\tc"), "\t")
        self.assertEqual(self.tools._detect_delimiter("a|b|c"), "|")
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        self.assertEqual(self.tools._normalize_phone("5551234567"), "(555) 123-4567")
        self.assertEqual(self.tools._normalize_phone("15551234567"), "+1 (555) 123-4567")
        self.assertEqual(self.tools._normalize_phone("(555) 123-4567"), "(555) 123-4567")
        self.assertEqual(self.tools._normalize_phone("555.123.4567"), "(555) 123-4567")
        self.assertEqual(self.tools._normalize_phone("+34 91 123 4567"), "+34 91 123 4567")


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
        
        # The response should mention the contacts or processing
        result_lower = result.lower()
        self.assertTrue(
            any(term in result_lower for term in ['john', 'jane', 'contact', 'import', 'process']),
            f"Response doesn't seem to mention the contacts: {result}"
        )
    
    def test_import_international_csv_integration(self):
        """Integration test: Import international CSV format."""
        csv_data = """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567
María,López,maria@test.es,+34 93 987 6543"""
        
        result = self.importer.import_contacts(csv_data, "Import Spanish contact list")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Should handle the Spanish format
        result_lower = result.lower()
        self.assertTrue(
            any(term in result_lower for term in ['luis', 'maría', 'garcia', 'lopez', 'contact']),
            f"Response doesn't seem to handle Spanish names: {result}"
        )
    
    def test_import_pipe_delimited_integration(self):
        """Integration test: Import pipe-delimited CSV without headers."""
        csv_data = """John Doe|john@example.com|555-123-4567|Acme Corp
Jane Smith|jane@test.org|555-987-6543|Tech Inc"""
        
        result = self.importer.import_contacts(csv_data, "Import pipe-delimited data without headers")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Should handle the pipe format and extract data
        result_lower = result.lower()
        self.assertTrue(
            any(term in result_lower for term in ['john', 'jane', 'acme', 'tech', 'contact', 'parse', 'csv', 'data']),
            f"Response doesn't seem to handle pipe-delimited format: {result}"
        )
    
    def test_import_mixed_format_integration(self):
        """Integration test: Import CSV with mixed data in fields."""
        csv_data = """Contact,Primary Info,Notes
John Doe,john@example.com,Phone: 555-123-4567 Company: Acme
Jane Smith,Call 555-987-6543,Email: jane@test.org"""
        
        result = self.importer.import_contacts(csv_data, "Import contacts with mixed data in notes")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Should extract data from mixed fields
        result_lower = result.lower()
        self.assertTrue(
            any(term in result_lower for term in ['john', 'jane', 'email', 'phone', 'contact']),
            f"Response doesn't seem to handle mixed format: {result}"
        )
    
    def test_agent_uses_tools_integration(self):
        """Integration test: Verify agent actually uses the tools."""
        csv_data = """Name,Email
Test User,test@example.com"""
        
        # Patch the tools to track if they're called
        original_parse_csv = self.importer.tools.parse_csv
        original_normalize_contact = self.importer.tools.normalize_contact
        
        parse_csv_called = False
        normalize_contact_called = False
        
        def track_parse_csv(*args, **kwargs):
            nonlocal parse_csv_called
            parse_csv_called = True
            return original_parse_csv(*args, **kwargs)
        
        def track_normalize_contact(*args, **kwargs):
            nonlocal normalize_contact_called
            normalize_contact_called = True
            return original_normalize_contact(*args, **kwargs)
        
        self.importer.tools.parse_csv = track_parse_csv
        self.importer.tools.normalize_contact = track_normalize_contact
        
        result = self.importer.import_contacts(csv_data, "Import simple contact")
        
        # Verify we got a response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Verify tools were actually called by the agent
        self.assertTrue(parse_csv_called, "Agent should have called parse_csv tool")
        # Note: normalize_contact might not always be called depending on agent's approach


if __name__ == "__main__":
    unittest.main()