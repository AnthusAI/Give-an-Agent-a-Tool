#!/usr/bin/env python3
"""
Traditional Imperative Approach: Text Processing Pipeline

This demonstrates the traditional way of programming where we must explicitly
handle every possible input format and scenario with rigid conditional logic.
The complexity grows exponentially as we add more formats and edge cases.
"""

import json
import csv
import xml.etree.ElementTree as ET
import re
from io import StringIO
from typing import Dict, List, Any, Optional, Union


class TraditionalTextProcessor:
    """
    Traditional imperative approach to text processing.
    
    Notice the explosion of conditional logic needed to handle every possible
    combination of input format, structure, and extraction requirement.
    """
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    
    def process_text(self, text: str, extract_field: str) -> List[str]:
        """
        Main processing function with rigid branching logic.
        
        This is where the complexity explodes - we need explicit handling
        for every possible combination of input format and extraction type.
        """
        
        # First, try to detect the format
        format_type = self._detect_format(text)
        
        if format_type == "json":
            return self._process_json(text, extract_field)
        elif format_type == "csv":
            return self._process_csv(text, extract_field)
        elif format_type == "xml":
            return self._process_xml(text, extract_field)
        elif format_type == "plain_text":
            return self._process_plain_text(text, extract_field)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _detect_format(self, text: str) -> str:
        """
        Rigid format detection with explicit rules for each format.
        
        This becomes a maintenance nightmare as we add more formats.
        """
        text = text.strip()
        
        # JSON detection
        if (text.startswith('{') and text.endswith('}')) or \
           (text.startswith('[') and text.endswith(']')):
            try:
                json.loads(text)
                return "json"
            except json.JSONDecodeError:
                pass
        
        # XML detection
        if text.startswith('<') and text.endswith('>'):
            try:
                ET.fromstring(text)
                return "xml"
            except ET.ParseError:
                pass
        
        # CSV detection (very basic)
        if ',' in text and '\n' in text:
            lines = text.split('\n')
            if len(lines) > 1:
                # Check if first two lines have same number of commas
                first_commas = lines[0].count(',')
                second_commas = lines[1].count(',') if len(lines) > 1 else 0
                if first_commas > 0 and first_commas == second_commas:
                    return "csv"
        
        # Default to plain text
        return "plain_text"
    
    def _process_json(self, text: str, extract_field: str) -> List[str]:
        """
        Process JSON with explicit handling for different structures.
        
        Notice how we need separate logic for arrays vs objects,
        nested vs flat structures, etc.
        """
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        results = []
        
        if isinstance(data, list):
            # Handle JSON array
            for item in data:
                if isinstance(item, dict):
                    # Handle object in array
                    if extract_field == "email":
                        results.extend(self._extract_emails_from_dict(item))
                    elif extract_field == "phone":
                        results.extend(self._extract_phones_from_dict(item))
                    elif extract_field in item:
                        results.append(str(item[extract_field]))
                elif isinstance(item, str):
                    # Handle string in array
                    if extract_field == "email":
                        results.extend(self.email_pattern.findall(item))
                    elif extract_field == "phone":
                        results.extend(self.phone_pattern.findall(item))
        
        elif isinstance(data, dict):
            # Handle JSON object
            if extract_field == "email":
                results.extend(self._extract_emails_from_dict(data))
            elif extract_field == "phone":
                results.extend(self._extract_phones_from_dict(data))
            elif extract_field in data:
                value = data[extract_field]
                if isinstance(value, list):
                    results.extend([str(v) for v in value])
                else:
                    results.append(str(value))
        
        return results
    
    def _process_csv(self, text: str, extract_field: str) -> List[str]:
        """
        Process CSV with explicit handling for different delimiters and structures.
        
        We need separate logic for headers vs no headers, different delimiters,
        quoted vs unquoted fields, etc.
        """
        results = []
        
        # Try different delimiters
        for delimiter in [',', '\t', ';', '|']:
            try:
                # Try with headers
                reader = csv.DictReader(StringIO(text), delimiter=delimiter)
                first_row = next(reader, None)
                if first_row and extract_field in first_row:
                    results.append(first_row[extract_field])
                    for row in reader:
                        if extract_field in row and row[extract_field]:
                            results.append(row[extract_field])
                    break
            except:
                continue
        
        # If no headers worked, try without headers
        if not results:
            for delimiter in [',', '\t', ';', '|']:
                try:
                    reader = csv.reader(StringIO(text), delimiter=delimiter)
                    rows = list(reader)
                    if len(rows) > 0:
                        # Assume first column contains what we want
                        for row in rows:
                            if len(row) > 0:
                                if extract_field == "email":
                                    results.extend(self.email_pattern.findall(row[0]))
                                elif extract_field == "phone":
                                    results.extend(self.phone_pattern.findall(row[0]))
                                else:
                                    results.append(row[0])
                        break
                except:
                    continue
        
        return results
    
    def _process_xml(self, text: str, extract_field: str) -> List[str]:
        """
        Process XML with explicit handling for different structures.
        
        We need separate logic for attributes vs text content,
        different nesting levels, namespaces, etc.
        """
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {e}")
        
        results = []
        
        # Try to find elements with the field name
        for elem in root.iter():
            # Check element tag
            if elem.tag.lower() == extract_field.lower():
                if elem.text:
                    results.append(elem.text)
            
            # Check attributes
            for attr_name, attr_value in elem.attrib.items():
                if attr_name.lower() == extract_field.lower():
                    results.append(attr_value)
            
            # For email/phone, search in text content
            if elem.text:
                if extract_field == "email":
                    results.extend(self.email_pattern.findall(elem.text))
                elif extract_field == "phone":
                    results.extend(self.phone_pattern.findall(elem.text))
        
        return results
    
    def _process_plain_text(self, text: str, extract_field: str) -> List[str]:
        """
        Process plain text with pattern matching.
        
        Limited to what we can extract with regex patterns.
        """
        if extract_field == "email":
            return self.email_pattern.findall(text)
        elif extract_field == "phone":
            return self.phone_pattern.findall(text)
        else:
            # Can't extract arbitrary fields from plain text
            return []
    
    def _extract_emails_from_dict(self, data: dict) -> List[str]:
        """Extract emails from dictionary values."""
        emails = []
        for key, value in data.items():
            if isinstance(value, str):
                emails.extend(self.email_pattern.findall(value))
            elif isinstance(value, dict):
                emails.extend(self._extract_emails_from_dict(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        emails.extend(self.email_pattern.findall(item))
                    elif isinstance(item, dict):
                        emails.extend(self._extract_emails_from_dict(item))
        return emails
    
    def _extract_phones_from_dict(self, data: dict) -> List[str]:
        """Extract phone numbers from dictionary values."""
        phones = []
        for key, value in data.items():
            if isinstance(value, str):
                phones.extend(self.phone_pattern.findall(value))
            elif isinstance(value, dict):
                phones.extend(self._extract_phones_from_dict(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        phones.extend(self.phone_pattern.findall(item))
                    elif isinstance(item, dict):
                        phones.extend(self._extract_phones_from_dict(item))
        return phones


def main():
    """
    Demonstration of the traditional approach.
    
    Notice how rigid and limited this is - we can only handle the exact
    scenarios we've explicitly programmed for.
    """
    
    # Example inputs
    test_cases = [
        {
            "name": "JSON Array",
            "data": '''[
                {"name": "John Doe", "email": "john@example.com", "phone": "555-123-4567"},
                {"name": "Jane Smith", "email": "jane@test.org", "phone": "555-987-6543"}
            ]''',
            "extract": "email"
        },
        {
            "name": "CSV with Headers",
            "data": '''name,email,phone
John Doe,john@example.com,555-123-4567
Jane Smith,jane@test.org,555-987-6543''',
            "extract": "email"
        },
        {
            "name": "XML",
            "data": '''<contacts>
                <person email="john@example.com" phone="555-123-4567">John Doe</person>
                <person email="jane@test.org" phone="555-987-6543">Jane Smith</person>
            </contacts>''',
            "extract": "email"
        },
        {
            "name": "Plain Text",
            "data": '''Contact John at john@example.com or call 555-123-4567.
Also reach Jane at jane@test.org or 555-987-6543.''',
            "extract": "email"
        }
    ]
    
    processor = TraditionalTextProcessor()
    
    print("=" * 60)
    print("TRADITIONAL IMPERATIVE APPROACH - TEXT PROCESSING")
    print("=" * 60)
    print()
    print("Notice the rigid, explicit handling of each format type.")
    print("Adding new formats or extraction types requires modifying")
    print("the core logic with more conditional branches.")
    print()
    
    for test_case in test_cases:
        print(f"Processing: {test_case['name']}")
        print(f"Extracting: {test_case['extract']}")
        
        try:
            results = processor.process_text(test_case['data'], test_case['extract'])
            print(f"Results: {results}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)
    
    print()
    print("LIMITATIONS OF TRADITIONAL APPROACH:")
    print("• Must explicitly handle every format combination")
    print("• Adding new formats requires core code changes")
    print("• Complex branching logic becomes unmaintainable")
    print("• Limited flexibility for edge cases")
    print("• Cannot adapt to unexpected input variations")


if __name__ == "__main__":
    main()