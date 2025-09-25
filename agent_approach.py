#!/usr/bin/env python3
"""
Agent-Based Contact Importer

This demonstrates how an AI agent with simple business logic tools can handle
complex, varied contact data formats without explicit programming for each scenario.
The agent adapts to different CSV structures, column names, and data formats.
"""

import csv
import json
import os
import re
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()


class ContactTools:
    """
    Simple business logic tools for contact processing.
    
    Notice how each tool does ONE thing well - the agent decides
    how to combine them based on the input data structure.
    """
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\+?[\d\s\-\(\)\.]{10,}')
    
    def parse_csv(self, text: str, delimiter: Optional[str] = None) -> Dict[str, Any]:
        """Parse CSV text with automatic delimiter and header detection."""
        try:
            if not text.strip():
                return {"success": False, "error": "Empty input"}
            
            # Auto-detect delimiter if not provided
            if delimiter is None:
                delimiter = self._detect_delimiter(text)
            
            # Parse the CSV
            reader = csv.reader(StringIO(text), delimiter=delimiter)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            
            if not rows:
                return {"success": False, "error": "No data rows found"}
            
            # Detect if first row contains headers
            has_headers = self._detect_headers(rows[0])
            
            if has_headers:
                headers = [h.strip().lower() for h in rows[0]]
                data_rows = []
                for row in rows[1:]:
                    row_dict = {}
                    for i, value in enumerate(row):
                        if i < len(headers):
                            row_dict[headers[i]] = value.strip()
                    data_rows.append(row_dict)
            else:
                # No headers - create generic column names
                data_rows = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[f"column_{i}"] = value.strip()
                    data_rows.append(row_dict)
            
            return {
                "success": True,
                "has_headers": has_headers,
                "delimiter": delimiter,
                "rows": data_rows
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def normalize_contact(self, row: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Normalize a contact row into standard fields."""
        
        # Extract first and last name
        first_name, last_name = self._extract_names(row)
        
        # Extract email
        email = self._extract_email(row)
        
        # Extract phone
        phone = self._extract_phone(row)
        
        # Extract company
        company = self._extract_company(row)
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "company": company
        }
    
    def format_contacts(self, contacts: List[Dict[str, Optional[str]]]) -> str:
        """Format contacts as JSON for display."""
        return json.dumps(contacts, indent=2, ensure_ascii=False)
    
    def _detect_delimiter(self, text: str) -> str:
        """Detect the most likely CSV delimiter."""
        first_line = text.split('\n')[0]
        delimiters = [',', ';', '\t', '|']
        
        # Count occurrences of each delimiter
        counts = {delim: first_line.count(delim) for delim in delimiters}
        
        # Return the delimiter with the highest count
        return max(counts, key=counts.get) or ','
    
    def _detect_headers(self, first_row: List[str]) -> bool:
        """Detect if the first row contains headers."""
        # Simple heuristic: if most values contain letters and aren't email/phone patterns
        header_indicators = 0
        for cell in first_row:
            cell = cell.strip().lower()
            if cell and not cell.replace('.', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
                if '@' not in cell:  # Not an email
                    header_indicators += 1
        
        return header_indicators >= len(first_row) * 0.5
    
    def _extract_names(self, row: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
        """Extract first and last names from a row."""
        first_name = None
        last_name = None
        
        # Look for explicit first/last name fields
        for key, value in row.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['first', 'fname', 'given', 'nombre']):
                first_name = value.strip() if value else None
            elif any(term in key_lower for term in ['last', 'lname', 'surname', 'family', 'apellido']):
                last_name = value.strip() if value else None
        
        # If no explicit fields, look for a full name field
        if not first_name and not last_name:
            for key, value in row.items():
                key_lower = key.lower()
                if any(term in key_lower for term in ['name', 'nombre', 'contact']):
                    if value and value.strip():
                        parts = value.strip().split()
                        if len(parts) >= 2:
                            first_name = parts[0]
                            last_name = ' '.join(parts[1:])
                        elif len(parts) == 1:
                            first_name = parts[0]
                        break
        
        return first_name, last_name
    
    def _extract_email(self, row: Dict[str, str]) -> Optional[str]:
        """Extract email address from a row."""
        # First look for explicit email fields
        for key, value in row.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['email', 'mail', 'correo']):
                if value and '@' in value:
                    match = self.email_pattern.search(value)
                    if match:
                        return match.group(0)
        
        # Then search all fields for email patterns
        for value in row.values():
            if value and '@' in value:
                match = self.email_pattern.search(value)
                if match:
                    return match.group(0)
        
        return None
    
    def _extract_phone(self, row: Dict[str, str]) -> Optional[str]:
        """Extract phone number from a row."""
        # Look for explicit phone fields first
        for key, value in row.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['phone', 'tel', 'mobile', 'cell', 'number']):
                if value:
                    phone = self._normalize_phone(value)
                    if phone:
                        return phone
        
        # Then search all fields for phone patterns
        for value in row.values():
            if value:
                phone = self._normalize_phone(value)
                if phone:
                    return phone
        
        return None
    
    def _normalize_phone(self, value: str) -> Optional[str]:
        """Normalize a phone number."""
        if not value:
            return None
        
        # Extract digits
        digits = re.sub(r'\D', '', value)
        
        if len(digits) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith('1'):
            # US format with country code: +1 (XXX) XXX-XXXX
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif len(digits) >= 10:
            # International format: keep as-is but clean up
            match = self.phone_pattern.search(value)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_company(self, row: Dict[str, str]) -> Optional[str]:
        """Extract company name from a row."""
        for key, value in row.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ['company', 'organization', 'org', 'employer', 'business']):
                return value.strip() if value else None
        
        return None


class AgentContactImporter:
    """
    Agent-based contact importer that uses tools flexibly.
    
    The agent analyzes the CSV structure and decides how to use
    the available tools to extract and normalize contact information.
    """
    
    def __init__(self):
        self.tools = ContactTools()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        
        # Define tools for the OpenAI API
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "parse_csv",
                    "description": "Parse CSV text with automatic delimiter and header detection",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The CSV text to parse"},
                            "delimiter": {"type": "string", "description": "Optional delimiter override"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "normalize_contact",
                    "description": "Normalize a contact row into standard fields (first_name, last_name, email, phone, company)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "row": {"type": "object", "description": "Contact row data as key-value pairs"}
                        },
                        "required": ["row"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "format_contacts",
                    "description": "Format a list of normalized contacts as JSON",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "contacts": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "List of normalized contact objects"
                            }
                        },
                        "required": ["contacts"]
                    }
                }
            }
        ]
    
    def import_contacts(self, csv_text: str, task: str = "Import and normalize contacts") -> str:
        """
        Import contacts using the agent approach.
        
        The agent will analyze the CSV structure and use tools to:
        1. Parse the CSV data
        2. Normalize each contact into standard fields
        3. Format the results for display
        """
        
        system_prompt = """You are a contact import assistant. Your job is to:

1. Parse the provided CSV data using the parse_csv tool
2. For each contact row, use normalize_contact to extract standard fields
3. Format the final results using format_contacts

You can handle various CSV formats:
- Different delimiters (comma, semicolon, tab, pipe)
- With or without headers
- Different column names (first/last name, full name, email variations, etc.)
- International formats and languages

Be flexible and adaptive - the CSV might have unexpected structures or column names."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task}\n\nCSV Data:\n{csv_text}"}
        ]
        
        # Get initial response with tool calls
        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            messages=messages,
            tools=self.tool_definitions,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # Execute tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the appropriate tool method
                if hasattr(self.tools, function_name):
                    result = getattr(self.tools, function_name)(**function_args)
                else:
                    result = {"error": f"Unknown function: {function_name}"}
                
                # Add tool result to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Get final response
            final_response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
                messages=messages
            )
            
            return final_response.choices[0].message.content
        else:
            return message.content


def main():
    """
    Demonstration of the agent-based contact importer.
    
    Notice how the agent can handle various CSV formats without
    explicit programming for each scenario.
    """
    
    # Test cases with different CSV formats and structures
    test_cases = [
        {
            "name": "Standard CRM Export",
            "data": """First Name,Last Name,Email,Phone,Company
John,Doe,john@example.com,555-123-4567,Acme Corp
Jane,Smith,jane@test.org,555-987-6543,Tech Inc""",
            "task": "Import standard contact list"
        },
        {
            "name": "Combined Name Field",
            "data": """Full Name,Email Address,Work Phone
John Doe,john@example.com,(555) 123-4567
Jane Smith,jane@test.org,555.987.6543""",
            "task": "Import contacts with combined names"
        },
        {
            "name": "International Format",
            "data": """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567
María,López,maria@test.es,+34 93 987 6543""",
            "task": "Import Spanish contact list"
        },
        {
            "name": "Pipe-Delimited No Headers",
            "data": """John Doe|john@example.com|555-123-4567|Acme Corp
Jane Smith|jane@test.org|555-987-6543|Tech Inc""",
            "task": "Import pipe-delimited data without headers"
        },
        {
            "name": "Mixed Format with Notes",
            "data": """Contact,Primary Info,Notes
John Doe,john@example.com,Phone: 555-123-4567 Company: Acme
Jane Smith,Call 555-987-6543,Email: jane@test.org""",
            "task": "Import contacts with mixed data in notes"
        }
    ]
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    try:
        importer = AgentContactImporter()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    print("=" * 70)
    print("AGENT-BASED CONTACT IMPORTER")
    print("=" * 70)
    print()
    print("The agent analyzes each CSV format and adapts its approach")
    print("without explicit programming for each scenario.")
    print()
    
    for test_case in test_cases:
        print(f"Processing: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        
        try:
            result = importer.import_contacts(test_case['data'], test_case['task'])
            print("Result:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)
        print()
    
    print("ADVANTAGES OF AGENT APPROACH:")
    print("• No explicit format detection logic needed")
    print("• Handles various column names and structures automatically")
    print("• Adapts to international formats and languages")
    print("• Can extract data from mixed/unstructured fields")
    print("• Easy to extend with new tools")


if __name__ == "__main__":
    main()