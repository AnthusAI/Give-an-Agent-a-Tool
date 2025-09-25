#!/usr/bin/env python3
"""
Tests for the demo script that compares both approaches.
"""

import pytest
import os
from unittest.mock import patch, Mock
from demo import run_demo
from traditional_approach import TraditionalTextProcessor
from agent_approach import AgentTextProcessor


class TestDemo:
    """Test suite for the demo functionality."""
    
    def test_demo_runs_without_api_key(self, capsys):
        """Test that demo runs gracefully without OpenAI API key."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing API key
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
            
            run_demo()
            
            captured = capsys.readouterr()
            assert "PROGRAMMING PARADIGM COMPARISON" in captured.out
            assert "OPENAI_API_KEY not found" in captured.out
            assert "TRADITIONAL APPROACH:" in captured.out
            assert "AGENT APPROACH: (Skipped - no API key)" in captured.out
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_demo_runs_with_api_key(self, capsys):
        """Test that demo attempts to run both approaches with API key."""
        # Mock the AgentTextProcessor to avoid actual API calls
        with patch('demo.AgentTextProcessor') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.process_text.return_value = "Mocked agent result"
            mock_agent_class.return_value = mock_agent
            
            run_demo()
            
            captured = capsys.readouterr()
            assert "PROGRAMMING PARADIGM COMPARISON" in captured.out
            assert "TRADITIONAL APPROACH:" in captured.out
            assert "AGENT APPROACH:" in captured.out
            assert "Mocked agent result" in captured.out
    
    def test_traditional_processor_in_demo(self):
        """Test that traditional processor works as expected in demo context."""
        processor = TraditionalTextProcessor()
        
        # Test with simple JSON
        json_data = '''[{"email": "test@example.com"}]'''
        results = processor.process_text(json_data, "email")
        
        assert "test@example.com" in results
    
    def test_demo_handles_traditional_errors_gracefully(self, capsys):
        """Test that demo handles traditional approach errors gracefully."""
        with patch('demo.TraditionalTextProcessor') as mock_traditional:
            mock_processor = Mock()
            mock_processor.process_text.side_effect = Exception("Test error")
            mock_traditional.return_value = mock_processor
            
            with patch.dict(os.environ, {}, clear=True):
                run_demo()
            
            captured = capsys.readouterr()
            assert "Error - Test error" in captured.out
    
    def test_demo_shows_key_differences(self, capsys):
        """Test that demo explains the key differences between approaches."""
        with patch.dict(os.environ, {}, clear=True):
            run_demo()
            
            captured = capsys.readouterr()
            assert "KEY DIFFERENCES:" in captured.out
            assert "Traditional Approach:" in captured.out
            assert "Agent Approach:" in captured.out
            assert "business logic tools" in captured.out
    
    def test_demo_test_cases_are_meaningful(self):
        """Test that the demo test cases demonstrate the paradigm difference."""
        # This test verifies that our test cases actually show the difference
        processor = TraditionalTextProcessor()
        
        # Standard case - both should work
        json_data = '''[{"email": "test@example.com"}]'''
        results = processor.process_text(json_data, "email")
        assert len(results) > 0
        
        # Complex case - traditional approach should struggle
        complex_task_data = '''name|email|department
John|john@example.com|Engineering
Jane|jane@test.org|Marketing'''
        
        # Traditional approach can extract emails but can't filter by department
        results = processor.process_text(complex_task_data, "email")
        assert len(results) >= 2  # Gets all emails, can't filter
    
    def test_demo_educational_value(self, capsys):
        """Test that demo provides educational explanations."""
        with patch.dict(os.environ, {}, clear=True):
            run_demo()
            
            captured = capsys.readouterr()
            
            # Check for educational content
            assert "This demo shows the same tasks solved with two different approaches" in captured.out
            assert "Rigid - only handles pre-programmed scenarios" in captured.out
            assert "Flexible - adapts to new scenarios" in captured.out
            assert "Write business logic tools, let agents combine them!" in captured.out


class TestDemoIntegration:
    """Integration tests for the demo script."""
    
    def test_demo_imports_work(self):
        """Test that all required imports work correctly."""
        # This test ensures that the demo can import both approaches
        from demo import run_demo
        from traditional_approach import TraditionalTextProcessor
        
        # Should be able to create instances
        processor = TraditionalTextProcessor()
        assert processor is not None
        
        # Demo function should exist
        assert callable(run_demo)
    
    def test_demo_test_cases_cover_paradigm_differences(self):
        """Test that demo test cases effectively show paradigm differences."""
        # Verify that our test cases actually demonstrate the key differences
        
        # Case 1: Standard format - both approaches should work
        standard_case = {
            "name": "Standard JSON",
            "data": '''[{"email": "test@example.com"}]''',
            "task": "Extract all email addresses"
        }
        
        processor = TraditionalTextProcessor()
        results = processor.process_text(standard_case["data"], "email")
        assert len(results) > 0
        
        # Case 2: Complex task - shows agent advantage
        complex_case = {
            "name": "Mixed Format Challenge",
            "data": '''name|email|department
John|john@example.com|Engineering
Jane|jane@test.org|Marketing''',
            "task": "Find emails of people in Engineering department"
        }
        
        # Traditional approach cannot handle the filtering requirement
        # It can extract emails but not filter by department
        results = processor.process_text(complex_case["data"], "email")
        # Should get all emails, not just Engineering ones
        assert len(results) >= 2
    
    def test_demo_error_handling(self):
        """Test that demo handles various error conditions."""
        with patch('demo.TraditionalTextProcessor') as mock_traditional:
            # Test with processor that raises exceptions
            mock_processor = Mock()
            mock_processor.process_text.side_effect = [
                ["success@example.com"],  # First call succeeds
                Exception("Network error"),  # Second call fails
                ValueError("Invalid format")  # Third call fails differently
            ]
            mock_traditional.return_value = mock_processor
            
            # Should not crash despite errors
            with patch.dict(os.environ, {}, clear=True):
                try:
                    run_demo()
                except Exception as e:
                    pytest.fail(f"Demo should handle errors gracefully, but raised: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
