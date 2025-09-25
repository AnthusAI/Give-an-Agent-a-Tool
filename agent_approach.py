#!/usr/bin/env python3
"""
Agent-Based Approach: Text Processing Pipeline

This demonstrates the new paradigm where we give an AI agent a set of tools
(business logic) and let it decide how to combine them to solve tasks.
The agent can handle unexpected inputs and edge cases without explicit programming.
"""

import json
import csv
import xml.etree.ElementTree as ET
import re
import os
from io import StringIO
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TextProcessingTools:
    """
    Simple business logic tools that the agent can use.
    
    Notice how each tool does ONE thing well, and the agent
    decides how to combine them based on the input.
    """
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    
    def parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON text into a Python object."""
        try:
            return {"success": True, "data": json.loads(text)}
        except json.JSONDecodeError as e:
            return {"success": False, "error": str(e)}
    
    def parse_csv(self, text: str, delimiter: str = None, has_headers: bool = None) -> Dict[str, Any]:
        """Parse CSV text with optional delimiter and header detection."""
        try:
            # Auto-detect delimiter if not provided
            if delimiter is None:
                for delim in [',', '\t', ';', '|']:
                    if delim in text:
                        delimiter = delim
                        break
                else:
                    delimiter = ','
            
            # Auto-detect headers if not specified
            if has_headers is None:
                lines = text.strip().split('\n')
                if len(lines) > 1:
                    # Simple heuristic: if first line has non-numeric values, assume headers
                    first_line_values = lines[0].split(delimiter)
                    has_headers = any(not val.strip().replace('.', '').replace('-', '').isdigit() 
                                    for val in first_line_values)
                else:
                    has_headers = False
            
            if has_headers:
                reader = csv.DictReader(StringIO(text), delimiter=delimiter)
                data = list(reader)
            else:
                reader = csv.reader(StringIO(text), delimiter=delimiter)
                data = [list(row) for row in reader]
            
            return {"success": True, "data": data, "has_headers": has_headers, "delimiter": delimiter}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parse_xml(self, text: str) -> Dict[str, Any]:
        """Parse XML text into a structured format."""
        try:
            root = ET.fromstring(text)
            
            def xml_to_dict(element):
                result = {}
                
                # Add attributes
                if element.attrib:
                    result['@attributes'] = element.attrib
                
                # Add text content
                if element.text and element.text.strip():
                    result['text'] = element.text.strip()
                
                # Add child elements
                for child in element:
                    child_data = xml_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_data)
                    else:
                        result[child.tag] = child_data
                
                return result
            
            return {"success": True, "data": {root.tag: xml_to_dict(root)}}
        
        except ET.ParseError as e:
            return {"success": False, "error": str(e)}
    
    def extract_field(self, data: Any, field_name: str) -> List[str]:
        """Extract all values for a specific field from structured data."""
        results = []
        
        def extract_recursive(obj, field):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() == field.lower():
                        if isinstance(value, list):
                            results.extend([str(v) for v in value])
                        else:
                            results.append(str(value))
                    else:
                        extract_recursive(value, field)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, field)
        
        extract_recursive(data, field_name)
        return results
    
    def extract_emails(self, text_or_data: Any) -> List[str]:
        """Extract email addresses from text or structured data."""
        emails = []
        
        def extract_from_text(text):
            if isinstance(text, str):
                emails.extend(self.email_pattern.findall(text))
        
        def extract_recursive(obj):
            if isinstance(obj, str):
                extract_from_text(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(text_or_data)
        return emails
    
    def extract_phones(self, text_or_data: Any) -> List[str]:
        """Extract phone numbers from text or structured data."""
        phones = []
        
        def extract_from_text(text):
            if isinstance(text, str):
                phones.extend(self.phone_pattern.findall(text))
        
        def extract_recursive(obj):
            if isinstance(obj, str):
                extract_from_text(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(text_or_data)
        return phones
    
    def filter_records(self, data: List[Dict], condition_field: str, condition_value: str) -> List[Dict]:
        """Filter records based on a field condition."""
        if not isinstance(data, list):
            return []
        
        filtered = []
        for record in data:
            if isinstance(record, dict):
                if condition_field in record and str(record[condition_field]).lower() == condition_value.lower():
                    filtered.append(record)
        
        return filtered
    
    def format_output(self, data: List[str], format_type: str = "list") -> str:
        """Format output data in different ways."""
        if format_type == "json":
            return json.dumps(data, indent=2)
        elif format_type == "csv":
            return '\n'.join(data)
        elif format_type == "numbered":
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(data))
        else:  # default to list
            return str(data)


class AgentTextProcessor:
    """
    Agent-based text processor that uses tools flexibly.
    
    The agent decides which tools to use and how to combine them
    based on the input and the task requirements.
    """
    
    def __init__(self):
        self.tools = TextProcessingTools()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Define the tools for the OpenAI API
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "parse_json",
                    "description": "Parse JSON text into a Python object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The JSON text to parse"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "parse_csv",
                    "description": "Parse CSV text with optional delimiter and header detection",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The CSV text to parse"},
                            "delimiter": {"type": "string", "description": "CSV delimiter (auto-detected if not provided)"},
                            "has_headers": {"type": "boolean", "description": "Whether CSV has headers (auto-detected if not provided)"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "parse_xml",
                    "description": "Parse XML text into a structured format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The XML text to parse"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_field",
                    "description": "Extract all values for a specific field from structured data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"description": "The structured data to search"},
                            "field_name": {"type": "string", "description": "The field name to extract"}
                        },
                        "required": ["data", "field_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_emails",
                    "description": "Extract email addresses from text or structured data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text_or_data": {"description": "Text or structured data to search for emails"}
                        },
                        "required": ["text_or_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_phones",
                    "description": "Extract phone numbers from text or structured data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text_or_data": {"description": "Text or structured data to search for phone numbers"}
                        },
                        "required": ["text_or_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_records",
                    "description": "Filter records based on a field condition",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "description": "List of records to filter"},
                            "condition_field": {"type": "string", "description": "Field to filter on"},
                            "condition_value": {"type": "string", "description": "Value to match"}
                        },
                        "required": ["data", "condition_field", "condition_value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "format_output",
                    "description": "Format output data in different ways",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "description": "Data to format"},
                            "format_type": {"type": "string", "enum": ["list", "json", "csv", "numbered"], "description": "Output format"}
                        },
                        "required": ["data"]
                    }
                }
            }
        ]
    
    def process_text(self, text: str, task: str) -> str:
        """
        Process text using the agent approach.
        
        The agent analyzes the input and task, then decides which tools
        to use and how to combine them to achieve the goal.
        """
        
        system_prompt = """You are a text processing agent with access to various parsing and extraction tools.

Your job is to analyze the input text and use the available tools to complete the requested task.

Key principles:
1. First, examine the input to determine its format (JSON, CSV, XML, or plain text)
2. Use the appropriate parsing tool to structure the data
3. Use extraction tools to find the requested information
4. Format the output appropriately

Available tools:
- parse_json: Parse JSON text
- parse_csv: Parse CSV text (auto-detects delimiter and headers)
- parse_xml: Parse XML text
- extract_field: Extract specific field values from structured data
- extract_emails: Find email addresses in any text or data
- extract_phones: Find phone numbers in any text or data
- filter_records: Filter data based on conditions
- format_output: Format results in different ways

Be flexible and adaptive - use the tools creatively to handle edge cases and unexpected input formats."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task}\n\nInput text:\n{text}"}
        ]
        
        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            messages=messages,
            tools=self.tool_definitions,
            tool_choice="auto"
        )
        
        # Process tool calls
        message = response.choices[0].message
        
        if message.tool_calls:
            # Execute tool calls
            messages.append(message)
            
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the appropriate tool method
                if hasattr(self.tools, function_name):
                    result = getattr(self.tools, function_name)(**function_args)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": json.dumps(result)
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
    Demonstration of the agent-based approach.
    
    Notice how the agent can handle the same inputs as the traditional
    approach, but with much more flexibility and no explicit branching logic.
    """
    
    # Same test cases as traditional approach
    test_cases = [
        {
            "name": "JSON Array",
            "data": '''[
                {"name": "John Doe", "email": "john@example.com", "phone": "555-123-4567"},
                {"name": "Jane Smith", "email": "jane@test.org", "phone": "555-987-6543"}
            ]''',
            "task": "Extract all email addresses"
        },
        {
            "name": "CSV with Headers",
            "data": '''name,email,phone
John Doe,john@example.com,555-123-4567
Jane Smith,jane@test.org,555-987-6543''',
            "task": "Extract all email addresses"
        },
        {
            "name": "XML",
            "data": '''<contacts>
                <person email="john@example.com" phone="555-123-4567">John Doe</person>
                <person email="jane@test.org" phone="555-987-6543">Jane Smith</person>
            </contacts>''',
            "task": "Extract all email addresses"
        },
        {
            "name": "Plain Text",
            "data": '''Contact John at john@example.com or call 555-123-4567.
Also reach Jane at jane@test.org or 555-987-6543.''',
            "task": "Extract all email addresses"
        },
        {
            "name": "Mixed Task",
            "data": '''name|email|department
John Doe|john@example.com|Engineering
Jane Smith|jane@test.org|Marketing
Bob Wilson|bob@company.com|Engineering''',
            "task": "Find all people in the Engineering department and get their email addresses"
        }
    ]
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    processor = AgentTextProcessor()
    
    print("=" * 60)
    print("AGENT-BASED APPROACH - TEXT PROCESSING")
    print("=" * 60)
    print()
    print("Notice how the agent flexibly combines tools to handle")
    print("different formats and tasks without explicit programming.")
    print()
    
    for test_case in test_cases:
        print(f"Processing: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        
        try:
            result = processor.process_text(test_case['data'], test_case['task'])
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)
    
    print()
    print("ADVANTAGES OF AGENT APPROACH:")
    print("• No explicit format detection logic needed")
    print("• Handles edge cases and variations automatically")
    print("• Easy to add new tools without changing core logic")
    print("• Adapts to unexpected input formats")
    print("• Can combine tools creatively for complex tasks")


if __name__ == "__main__":
    main()
