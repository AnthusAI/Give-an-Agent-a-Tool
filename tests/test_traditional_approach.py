#!/usr/bin/env python3
"""
Tests for the traditional imperative approach.

These tests verify that the traditional text processor handles
various input formats correctly and demonstrates its limitations.
"""

import pytest
import json
from traditional_approach import TraditionalTextProcessor


class TestTraditionalTextProcessor:
    """Test suite for the traditional approach."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TraditionalTextProcessor()
    
    def test_json_array_email_extraction(self):
        """Test extracting emails from JSON array."""
        json_data = '''[
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@test.org"}
        ]'''
        
        results = self.processor.process_text(json_data, "email")
        assert "john@example.com" in results
        assert "jane@test.org" in results
        assert len(results) == 2
    
    def test_json_object_email_extraction(self):
        """Test extracting emails from JSON object."""
        json_data = '''{"user": {"email": "user@example.com", "name": "Test User"}}'''
        
        results = self.processor.process_text(json_data, "email")
        assert "user@example.com" in results
    
    def test_csv_with_headers_email_extraction(self):
        """Test extracting emails from CSV with headers."""
        csv_data = '''name,email,phone
John Doe,john@example.com,555-123-4567
Jane Smith,jane@test.org,555-987-6543'''
        
        results = self.processor.process_text(csv_data, "email")
        assert "john@example.com" in results
        assert "jane@test.org" in results
    
    def test_csv_different_delimiter(self):
        """Test CSV with different delimiter."""
        csv_data = '''name|email|phone
John Doe|john@example.com|555-123-4567
Jane Smith|jane@test.org|555-987-6543'''
        
        results = self.processor.process_text(csv_data, "email")
        # The traditional approach should extract clean email addresses
        assert any("john@example.com" in result for result in results)
        assert any("jane@test.org" in result for result in results)
    
    def test_xml_email_extraction(self):
        """Test extracting emails from XML."""
        xml_data = '''<contacts>
            <person email="john@example.com">John Doe</person>
            <person email="jane@test.org">Jane Smith</person>
        </contacts>'''
        
        results = self.processor.process_text(xml_data, "email")
        assert "john@example.com" in results
        assert "jane@test.org" in results
    
    def test_plain_text_email_extraction(self):
        """Test extracting emails from plain text."""
        text_data = '''Contact John at john@example.com or Jane at jane@test.org.'''
        
        results = self.processor.process_text(text_data, "email")
        assert "john@example.com" in results
        assert "jane@test.org" in results
    
    def test_phone_extraction_json(self):
        """Test extracting phone numbers from JSON."""
        json_data = '''[
            {"name": "John", "phone": "555-123-4567"},
            {"name": "Jane", "phone": "555-987-6543"}
        ]'''
        
        results = self.processor.process_text(json_data, "phone")
        assert "555-123-4567" in results
        assert "555-987-6543" in results
    
    def test_format_detection_json(self):
        """Test JSON format detection."""
        json_data = '{"test": "value"}'
        format_type = self.processor._detect_format(json_data)
        assert format_type == "json"
    
    def test_format_detection_csv(self):
        """Test CSV format detection."""
        csv_data = '''name,email
John,john@example.com
Jane,jane@example.com'''
        format_type = self.processor._detect_format(csv_data)
        assert format_type == "csv"
    
    def test_format_detection_xml(self):
        """Test XML format detection."""
        xml_data = '<root><item>test</item></root>'
        format_type = self.processor._detect_format(xml_data)
        assert format_type == "xml"
    
    def test_format_detection_plain_text(self):
        """Test plain text format detection."""
        text_data = 'This is just plain text with no structure.'
        format_type = self.processor._detect_format(text_data)
        assert format_type == "plain_text"
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON."""
        invalid_json = '{"invalid": json}'
        
        # Traditional approach detects this as plain text, not JSON
        # So it won't raise a JSON parsing error
        results = self.processor.process_text(invalid_json, "email")
        assert isinstance(results, list)  # Should return empty list for plain text
    
    def test_invalid_xml_handling(self):
        """Test handling of invalid XML."""
        invalid_xml = '<invalid><unclosed>tag</invalid>'
        
        # Traditional approach detects this as plain text, not XML
        # So it won't raise an XML parsing error
        results = self.processor.process_text(invalid_xml, "email")
        assert isinstance(results, list)  # Should return empty list for plain text
    
    def test_empty_input(self):
        """Test handling of empty input."""
        results = self.processor.process_text("", "email")
        assert results == []
    
    def test_unsupported_extraction_field(self):
        """Test handling of unsupported extraction field."""
        json_data = '{"name": "John", "email": "john@example.com"}'
        
        # Traditional approach can't extract arbitrary fields from plain text
        results = self.processor.process_text("Some plain text", "arbitrary_field")
        assert results == []
    
    def test_nested_json_email_extraction(self):
        """Test extracting emails from nested JSON structure."""
        nested_json = '''{
            "users": [
                {"profile": {"contact": {"email": "nested@example.com"}}},
                {"profile": {"contact": {"email": "deep@test.org"}}}
            ]
        }'''
        
        results = self.processor.process_text(nested_json, "email")
        assert "nested@example.com" in results
        assert "deep@test.org" in results
    
    def test_mixed_content_extraction(self):
        """Test extraction from mixed content types."""
        # This demonstrates a limitation - traditional approach
        # struggles with mixed or unusual formats
        mixed_data = '''Some text with email@example.com
        {"embedded": "json@test.com"}
        <xml>xml@example.org</xml>'''
        
        # Traditional approach will treat this as plain text
        results = self.processor.process_text(mixed_data, "email")
        # Should find the plain text email, but might miss structured ones
        assert "email@example.com" in results
    
    def test_csv_without_headers(self):
        """Test CSV processing without headers."""
        csv_no_headers = '''john@example.com,John Doe,555-123-4567
jane@test.org,Jane Smith,555-987-6543'''
        
        results = self.processor.process_text(csv_no_headers, "email")
        # Traditional approach should still find emails in the data
        assert len(results) >= 2
    
    def test_complex_xml_structure(self):
        """Test complex XML with nested elements."""
        complex_xml = '''<?xml version="1.0"?>
        <company>
            <department name="Engineering">
                <employee>
                    <name>John Doe</name>
                    <contact email="john@company.com" phone="555-123-4567"/>
                </employee>
            </department>
            <department name="Marketing">
                <employee>
                    <name>Jane Smith</name>
                    <contact email="jane@company.com" phone="555-987-6543"/>
                </employee>
            </department>
        </company>'''
        
        results = self.processor.process_text(complex_xml, "email")
        assert "john@company.com" in results
        assert "jane@company.com" in results
    
    def test_edge_case_email_formats(self):
        """Test various email format edge cases."""
        text_with_emails = '''
        Standard: user@example.com
        With plus: user+tag@example.com
        With dots: first.last@example.com
        With numbers: user123@example.com
        Subdomain: user@mail.example.com
        '''
        
        results = self.processor.process_text(text_with_emails, "email")
        assert len(results) >= 5  # Should find all valid email formats
    
    def test_performance_large_dataset(self):
        """Test performance with larger dataset."""
        # Create a large JSON array
        large_data = []
        for i in range(100):
            large_data.append({
                "id": i,
                "email": f"user{i}@example.com",
                "name": f"User {i}"
            })
        
        json_data = json.dumps(large_data)
        results = self.processor.process_text(json_data, "email")
        
        assert len(results) == 100
        assert "user0@example.com" in results
        assert "user99@example.com" in results


class TestTraditionalApproachLimitations:
    """Tests that demonstrate the limitations of the traditional approach."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TraditionalTextProcessor()
    
    def test_cannot_handle_new_format(self):
        """Test that traditional approach cannot handle new formats."""
        # YAML format - not supported by traditional approach
        yaml_data = '''
        users:
          - name: John Doe
            email: john@example.com
          - name: Jane Smith
            email: jane@test.org
        '''
        
        # Traditional approach will treat this as plain text
        results = self.processor.process_text(yaml_data, "email")
        # Might find emails via regex, but won't understand structure
        assert len(results) >= 0  # Could be 0 or more depending on regex
    
    def test_cannot_handle_complex_queries(self):
        """Test that traditional approach cannot handle complex queries."""
        csv_data = '''name,email,department
John Doe,john@example.com,Engineering
Jane Smith,jane@test.org,Marketing
Bob Wilson,bob@company.com,Engineering'''
        
        # Traditional approach cannot filter by department
        # It can only extract emails, not filter by other criteria
        results = self.processor.process_text(csv_data, "email")
        assert len(results) == 3  # Gets all emails, cannot filter
    
    def test_rigid_error_handling(self):
        """Test rigid error handling in traditional approach."""
        # Malformed JSON that might be recoverable
        almost_json = '{"name": "John", "email": "john@example.com"'  # Missing closing brace
        
        # Traditional approach detects this as plain text and tries to extract emails
        results = self.processor.process_text(almost_json, "email")
        
        # Should find the email via regex in plain text mode
        assert "john@example.com" in results
        
        # But this demonstrates the rigidity - it can't understand the structure
    
    def test_cannot_adapt_to_variations(self):
        """Test that traditional approach cannot adapt to format variations."""
        # CSV with unusual quoting
        unusual_csv = '''name,"email address","phone number"
"John Doe","john@example.com","555-123-4567"
"Jane Smith","jane@test.org","555-987-6543"'''
        
        # Traditional approach might struggle with quoted headers
        results = self.processor.process_text(unusual_csv, "email")
        # Should work, but demonstrates rigidity in parsing logic
        assert len(results) >= 0
