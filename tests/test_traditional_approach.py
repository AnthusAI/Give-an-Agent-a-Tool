#!/usr/bin/env python3
"""Tests for the traditional contact importer."""

import unittest
from traditional_approach import TraditionalContactImporter


class TestTraditionalContactImporter(unittest.TestCase):
    """Test the traditional imperative contact importer."""
    
    def setUp(self):
        self.importer = TraditionalContactImporter()
    
    def test_import_standard_csv(self):
        """Test importing standard CSV with headers."""
        csv_data = """First Name,Last Name,Email,Phone,Company
John,Doe,john@example.com,555-123-4567,Acme Corp
Jane,Smith,jane@test.org,555-987-6543,Tech Inc"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        
        # Check first contact
        self.assertEqual(contacts[0]["first_name"], "John")
        self.assertEqual(contacts[0]["last_name"], "Doe")
        self.assertEqual(contacts[0]["email"], "john@example.com")
        self.assertEqual(contacts[0]["phone"], "(555) 123-4567")
        self.assertEqual(contacts[0]["company"], "Acme Corp")
    
    def test_import_pipe_delimited(self):
        """Test importing pipe-delimited CSV."""
        csv_data = """John Doe|john@example.com|555-123-4567|Acme Corp
Jane Smith|jane@test.org|555-987-6543|Tech Inc"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["first_name"], "John")
        self.assertEqual(contacts[0]["last_name"], "Doe")
        self.assertEqual(contacts[0]["email"], "john@example.com")
    
    def test_normalize_phone(self):
        """Test phone number normalization."""
        self.assertEqual(
            self.importer._normalize_phone("5551234567"),
            "(555) 123-4567"
        )
        self.assertEqual(
            self.importer._normalize_phone("15551234567"),
            "+1 (555) 123-4567"
        )
    
    def test_international_format_limitation(self):
        """Test limitation with international formats."""
        csv_data = """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        # This demonstrates the limitation - traditional approach
        # doesn't handle "Apellidos" correctly
        self.assertEqual(contacts[0]["first_name"], "Luis")
        # This should be "García" but traditional approach fails
        self.assertEqual(contacts[0]["last_name"], "Luis")  # Wrong!


if __name__ == "__main__":
    unittest.main()