#!/usr/bin/env python3
"""
Tests for the agent-based approach.

These tests verify that the agent approach handles various scenarios
flexibly and demonstrates its advantages over the traditional approach.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from agent_approach import TextProcessingTools, AgentTextProcessor


class TestTextProcessingTools:
    """Test suite for the business logic tools."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tools = TextProcessingTools()
    
    def test_parse_json_valid(self):
        """Test parsing valid JSON."""
        json_text = '{"name": "John", "email": "john@example.com"}'
        result = self.tools.parse_json(json_text)
        
        assert result["success"] is True
        assert result["data"]["name"] == "John"
        assert result["data"]["email"] == "john@example.com"
    
    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        invalid_json = '{"invalid": json}'
        result = self.tools.parse_json(invalid_json)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_parse_csv_with_headers(self):
        """Test parsing CSV with headers."""
        csv_text = '''name,email,phone
John Doe,john@example.com,555-123-4567
Jane Smith,jane@test.org,555-987-6543'''
        
        result = self.tools.parse_csv(csv_text)
        
        assert result["success"] is True
        assert result["has_headers"] is True
        assert result["delimiter"] == ","
        assert len(result["data"]) == 2
        assert result["data"][0]["email"] == "john@example.com"
    
    def test_parse_csv_without_headers(self):
        """Test parsing CSV without headers."""
        csv_text = '''john@example.com,John Doe,555-123-4567
jane@test.org,Jane Smith,555-987-6543'''
        
        result = self.tools.parse_csv(csv_text, has_headers=False)
        
        assert result["success"] is True
        assert result["has_headers"] is False
        assert len(result["data"]) == 2
        assert result["data"][0][0] == "john@example.com"
    
    def test_parse_csv_auto_detect_delimiter(self):
        """Test CSV delimiter auto-detection."""
        pipe_csv = '''name|email|phone
John Doe|john@example.com|555-123-4567'''
        
        result = self.tools.parse_csv(pipe_csv)
        
        assert result["success"] is True
        assert result["delimiter"] == "|"
        assert result["data"][0]["email"] == "john@example.com"
    
    def test_parse_xml_simple(self):
        """Test parsing simple XML."""
        xml_text = '''<contacts>
            <person email="john@example.com">John Doe</person>
        </contacts>'''
        
        result = self.tools.parse_xml(xml_text)
        
        assert result["success"] is True
        assert "contacts" in result["data"]
    
    def test_parse_xml_invalid(self):
        """Test parsing invalid XML."""
        invalid_xml = '<invalid><unclosed>tag</invalid>'
        result = self.tools.parse_xml(invalid_xml)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_extract_field_from_dict(self):
        """Test extracting field from dictionary."""
        data = {"name": "John", "email": "john@example.com"}
        results = self.tools.extract_field(data, "email")
        
        assert "john@example.com" in results
    
    def test_extract_field_from_list(self):
        """Test extracting field from list of dictionaries."""
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@test.org"}
        ]
        results = self.tools.extract_field(data, "email")
        
        assert "john@example.com" in results
        assert "jane@test.org" in results
        assert len(results) == 2
    
    def test_extract_field_nested(self):
        """Test extracting field from nested structure."""
        data = {
            "users": [
                {"profile": {"email": "nested@example.com"}},
                {"profile": {"email": "deep@test.org"}}
            ]
        }
        results = self.tools.extract_field(data, "email")
        
        assert "nested@example.com" in results
        assert "deep@test.org" in results
    
    def test_extract_emails_from_text(self):
        """Test extracting emails from plain text."""
        text = "Contact John at john@example.com or Jane at jane@test.org"
        results = self.tools.extract_emails(text)
        
        assert "john@example.com" in results
        assert "jane@test.org" in results
    
    def test_extract_emails_from_structure(self):
        """Test extracting emails from structured data."""
        data = {
            "contacts": [
                {"name": "John", "email": "john@example.com"},
                {"name": "Jane", "email": "jane@test.org"}
            ]
        }
        results = self.tools.extract_emails(data)
        
        assert "john@example.com" in results
        assert "jane@test.org" in results
    
    def test_extract_phones_from_text(self):
        """Test extracting phone numbers from text."""
        text = "Call John at 555-123-4567 or Jane at 555.987.6543"
        results = self.tools.extract_phones(text)
        
        assert "555-123-4567" in results
        assert "555.987.6543" in results
    
    def test_filter_records(self):
        """Test filtering records by condition."""
        data = [
            {"name": "John", "department": "Engineering"},
            {"name": "Jane", "department": "Marketing"},
            {"name": "Bob", "department": "Engineering"}
        ]
        
        results = self.tools.filter_records(data, "department", "Engineering")
        
        assert len(results) == 2
        assert all(r["department"] == "Engineering" for r in results)
    
    def test_format_output_json(self):
        """Test JSON output formatting."""
        data = ["item1", "item2", "item3"]
        result = self.tools.format_output(data, "json")
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data
    
    def test_format_output_csv(self):
        """Test CSV output formatting."""
        data = ["item1", "item2", "item3"]
        result = self.tools.format_output(data, "csv")
        
        assert result == "item1\nitem2\nitem3"
    
    def test_format_output_numbered(self):
        """Test numbered output formatting."""
        data = ["item1", "item2"]
        result = self.tools.format_output(data, "numbered")
        
        assert "1. item1" in result
        assert "2. item2" in result


class TestAgentTextProcessor:
    """Test suite for the agent-based processor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock the OpenAI client to avoid API calls in tests
        self.mock_client = Mock()
        
        with patch('agent_approach.OpenAI') as mock_openai:
            mock_openai.return_value = self.mock_client
            self.processor = AgentTextProcessor()
    
    def test_initialization(self):
        """Test that processor initializes correctly."""
        assert self.processor.tools is not None
        assert len(self.processor.tool_definitions) > 0
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_process_text_with_tool_calls(self):
        """Test processing text with tool calls."""
        # Mock the OpenAI response with tool calls
        mock_message = Mock()
        mock_tool_call = Mock()
        mock_tool_call.id = "call_1"
        mock_tool_call.function.name = "parse_json"
        mock_tool_call.function.arguments = '{"text": "{\\"email\\": \\"test@example.com\\"}"}'
        mock_message.tool_calls = [mock_tool_call]
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=mock_message)]
        
        # Mock final response
        mock_final_message = Mock()
        mock_final_message.content = "Found email: test@example.com"
        mock_final_response = Mock()
        mock_final_response.choices = [Mock(message=mock_final_message)]
        
        self.mock_client.chat.completions.create.side_effect = [
            mock_response,
            mock_final_response
        ]
        
        result = self.processor.process_text('{"email": "test@example.com"}', "Extract email")
        
        assert result == "Found email: test@example.com"
        assert self.mock_client.chat.completions.create.call_count == 2
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_process_text_without_tool_calls(self):
        """Test processing text without tool calls."""
        # Mock response without tool calls
        mock_message = Mock()
        mock_message.tool_calls = None
        mock_message.content = "No tools needed for this task"
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=mock_message)]
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.processor.process_text("Simple text", "Simple task")
        
        assert result == "No tools needed for this task"
        assert self.mock_client.chat.completions.create.call_count == 1
    
    def test_tool_definitions_completeness(self):
        """Test that all tool definitions are properly defined."""
        expected_tools = [
            "parse_json", "parse_csv", "parse_xml", "extract_field",
            "extract_emails", "extract_phones", "filter_records", "format_output"
        ]
        
        defined_tools = [tool["function"]["name"] for tool in self.processor.tool_definitions]
        
        for expected_tool in expected_tools:
            assert expected_tool in defined_tools
    
    def test_tool_definitions_have_required_fields(self):
        """Test that tool definitions have all required fields."""
        for tool_def in self.processor.tool_definitions:
            assert "type" in tool_def
            assert tool_def["type"] == "function"
            assert "function" in tool_def
            
            function = tool_def["function"]
            assert "name" in function
            assert "description" in function
            assert "parameters" in function
            
            parameters = function["parameters"]
            assert "type" in parameters
            assert "properties" in parameters
            assert "required" in parameters


class TestAgentApproachIntegration:
    """Integration tests for the agent approach."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tools = TextProcessingTools()
    
    def test_json_to_email_extraction_workflow(self):
        """Test complete workflow: JSON -> parse -> extract emails."""
        json_text = '''[
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@test.org"}
        ]'''
        
        # Step 1: Parse JSON
        parse_result = self.tools.parse_json(json_text)
        assert parse_result["success"] is True
        
        # Step 2: Extract emails
        emails = self.tools.extract_emails(parse_result["data"])
        assert "john@example.com" in emails
        assert "jane@test.org" in emails
    
    def test_csv_to_filtered_extraction_workflow(self):
        """Test complete workflow: CSV -> parse -> filter -> extract."""
        csv_text = '''name,email,department
John Doe,john@example.com,Engineering
Jane Smith,jane@test.org,Marketing
Bob Wilson,bob@company.com,Engineering'''
        
        # Step 1: Parse CSV
        parse_result = self.tools.parse_csv(csv_text)
        assert parse_result["success"] is True
        
        # Step 2: Filter by department
        engineering_people = self.tools.filter_records(
            parse_result["data"], "department", "Engineering"
        )
        assert len(engineering_people) == 2
        
        # Step 3: Extract emails from filtered results
        emails = self.tools.extract_field(engineering_people, "email")
        assert "john@example.com" in emails
        assert "bob@company.com" in emails
        assert "jane@test.org" not in emails
    
    def test_xml_to_structured_extraction_workflow(self):
        """Test complete workflow: XML -> parse -> extract."""
        xml_text = '''<company>
            <employee email="john@company.com" department="Engineering"/>
            <employee email="jane@company.com" department="Marketing"/>
        </company>'''
        
        # Step 1: Parse XML
        parse_result = self.tools.parse_xml(xml_text)
        assert parse_result["success"] is True
        
        # Step 2: Extract emails
        emails = self.tools.extract_emails(parse_result["data"])
        assert "john@company.com" in emails
        assert "jane@company.com" in emails
    
    def test_error_recovery_workflow(self):
        """Test that tools handle errors gracefully."""
        # Invalid JSON
        invalid_json = '{"invalid": json}'
        parse_result = self.tools.parse_json(invalid_json)
        assert parse_result["success"] is False
        
        # Tools should not crash on invalid input
        emails = self.tools.extract_emails("not structured data")
        assert isinstance(emails, list)
    
    def test_format_flexibility(self):
        """Test that tools handle format variations."""
        # Different CSV delimiters
        pipe_csv = "name|email\nJohn|john@example.com"
        tab_csv = "name\temail\nJohn\tjohn@example.com"
        
        pipe_result = self.tools.parse_csv(pipe_csv)
        tab_result = self.tools.parse_csv(tab_csv)
        
        assert pipe_result["success"] is True
        assert tab_result["success"] is True
        assert pipe_result["delimiter"] == "|"
        assert tab_result["delimiter"] == "\t"


class TestAgentApproachAdvantages:
    """Tests that demonstrate advantages of the agent approach."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tools = TextProcessingTools()
    
    def test_handles_new_format_gracefully(self):
        """Test that tools can handle unexpected formats."""
        # Even if we don't have a YAML parser, the email extractor
        # can still find emails in the text
        yaml_like_text = '''
        users:
          - name: John Doe
            email: john@example.com
          - name: Jane Smith
            email: jane@test.org
        '''
        
        emails = self.tools.extract_emails(yaml_like_text)
        assert "john@example.com" in emails
        assert "jane@test.org" in emails
    
    def test_flexible_field_extraction(self):
        """Test flexible field extraction from various structures."""
        # Same field name in different structures
        structures = [
            {"email": "direct@example.com"},
            {"user": {"email": "nested@example.com"}},
            {"contacts": [{"email": "array@example.com"}]},
            [{"email": "list@example.com"}]
        ]
        
        all_emails = []
        for structure in structures:
            emails = self.tools.extract_field(structure, "email")
            all_emails.extend(emails)
        
        assert "direct@example.com" in all_emails
        assert "nested@example.com" in all_emails
        assert "array@example.com" in all_emails
        assert "list@example.com" in all_emails
    
    def test_composable_operations(self):
        """Test that tools can be composed for complex operations."""
        data = '''[
            {"name": "John", "email": "john@example.com", "active": true},
            {"name": "Jane", "email": "jane@test.org", "active": false},
            {"name": "Bob", "email": "bob@company.com", "active": true}
        ]'''
        
        # Parse -> Filter -> Extract -> Format
        parsed = self.tools.parse_json(data)["data"]
        
        # Filter active users (would need a custom filter, but demonstrates concept)
        active_users = [user for user in parsed if user.get("active", False)]
        
        emails = self.tools.extract_field(active_users, "email")
        formatted = self.tools.format_output(emails, "numbered")
        
        assert "john@example.com" in formatted
        assert "bob@company.com" in formatted
        assert "jane@test.org" not in formatted
        assert "1." in formatted  # Numbered format
    
    def test_error_tolerance(self):
        """Test that agent approach is more error-tolerant."""
        # Partially malformed data that might still be processable
        partial_json = '''[
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane"  // missing email and closing brace
        ]'''
        
        # Traditional approach would fail completely
        # Agent approach might still extract what it can
        emails = self.tools.extract_emails(partial_json)
        assert "john@example.com" in emails  # At least gets the valid email
