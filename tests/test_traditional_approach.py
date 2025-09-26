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
        csv_data = """First Name,Last Name,Email,Phone
John,Doe,john@example.com,555-123-4567
Jane,Smith,jane@test.org,555-987-6543"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        
        # Check first contact
        self.assertEqual(contacts[0]["first_name"], "John")
        self.assertEqual(contacts[0]["last_name"], "Doe")
        self.assertEqual(contacts[0]["email"], "john@example.com")
        self.assertEqual(contacts[0]["phone"], "(555) 123-4567")
    
    def test_import_combined_name_field(self):
        """Test importing CSV with combined name field."""
        csv_data = """Full Name,Email Address,Work Phone
John Doe,john@example.com,(555) 123-4567
Jane Smith,jane@test.org,555.987.6543"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["first_name"], "John")
        self.assertEqual(contacts[0]["last_name"], "Doe")
        self.assertEqual(contacts[0]["email"], "john@example.com")
    
    def test_import_pipe_delimited(self):
        """Test importing pipe-delimited CSV without headers - traditional approach struggles."""
        csv_data = """John Doe|john@example.com|555-123-4567
Jane Smith|jane@test.org|555-987-6543"""
        
        # Traditional approach may struggle with pipe-delimited data without headers
        # because it can't properly map the columns
        with self.assertRaises(ValueError) as context:
            self.importer.import_contacts(csv_data)
        
        self.assertIn("Unsupported format", str(context.exception))
    
    def test_international_format(self):
        """Test importing international format (Spanish)."""
        csv_data = """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567
María,López,maria@test.es,+34 93 987 6543"""
        
        contacts = self.importer.import_contacts(csv_data)
        
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0]["first_name"], "Luis")
        self.assertEqual(contacts[0]["last_name"], "García")
        self.assertEqual(contacts[0]["email"], "luis@empresa.es")
    
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
        self.assertEqual(
            self.importer._normalize_phone("+34 91 123 4567"),
            "+34 91 123 4567"
        )
    
    def test_detect_delimiter(self):
        """Test delimiter detection."""
        self.assertEqual(self.importer._detect_delimiter("a,b,c"), ",")
        self.assertEqual(self.importer._detect_delimiter("a;b;c"), ";")
        self.assertEqual(self.importer._detect_delimiter("a\tb\tc"), "\t")
        self.assertEqual(self.importer._detect_delimiter("a|b|c"), "|")
    
    def test_header_normalization(self):
        """Test header normalization with synonyms."""
        headers = ["First Name", "Last Name", "Email Address"]
        normalized = self.importer._normalize_headers(headers, self.importer.header_synonyms)
        
        self.assertEqual(normalized[0], "first_name")
        self.assertEqual(normalized[1], "last_name")
        self.assertEqual(normalized[2], "email")
    
    def test_unexpected_format_breaks_traditional(self):
        """Test that traditional approach breaks on unexpected formats."""
        # This format breaks the traditional approach
        csv_data = """"Contact Info","Details","Extra"
"Smith, Jane (Manager)","jane.smith@company.com | Mobile: +1-555-0123","Dept: Sales, Start: 2020"
"Rodriguez, Carlos","carlos.r@email.com Phone: 555.987.6543","Engineering Team Lead\""""
        
        # Traditional approach should struggle with this format
        with self.assertRaises(ValueError) as context:
            self.importer.import_contacts(csv_data)
        
        # Should raise an error about unsupported format
        self.assertIn("Unsupported format", str(context.exception))
    
    def test_mixed_format_with_notes(self):
        """Test mixed format with data in notes fields - traditional approach struggles."""
        csv_data = """Contact,Primary Info,Notes
John Doe,john@example.com,Phone: 555-123-4567 Company: Acme
Jane Smith,Call 555-987-6543,Email: jane@test.org"""
        
        # Traditional approach struggles because it doesn't recognize "Contact" as a name field
        # and can't extract email from mixed data in the second row
        with self.assertRaises(ValueError) as context:
            self.importer.import_contacts(csv_data)
        
        self.assertIn("Unsupported format", str(context.exception))


if __name__ == "__main__":
    unittest.main()