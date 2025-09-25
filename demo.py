#!/usr/bin/env python3
"""
Side-by-side demonstration of both approaches.

This script runs the same test cases through both the traditional
imperative approach and the agent-based approach to show the difference.
"""

import os
from traditional_approach import TraditionalTextProcessor
from agent_approach import AgentTextProcessor


def run_demo():
    """Run both approaches side by side for comparison."""
    
    # Test cases that demonstrate the paradigm difference
    test_cases = [
        {
            "name": "Standard JSON",
            "data": '''[
                {"name": "John Doe", "email": "john@example.com"},
                {"name": "Jane Smith", "email": "jane@test.org"}
            ]''',
            "task": "Extract all email addresses"
        },
        {
            "name": "CSV with Unusual Delimiter",
            "data": '''name|email|department
John Doe|john@example.com|Engineering
Jane Smith|jane@test.org|Marketing''',
            "task": "Extract all email addresses"
        },
        {
            "name": "Mixed Format Challenge",
            "data": '''name|email|department
John Doe|john@example.com|Engineering
Jane Smith|jane@test.org|Marketing
Bob Wilson|bob@company.com|Engineering''',
            "task": "Find emails of people in Engineering department"
        }
    ]
    
    print("=" * 80)
    print("PROGRAMMING PARADIGM COMPARISON")
    print("=" * 80)
    print()
    print("This demo shows the same tasks solved with two different approaches:")
    print("1. Traditional Imperative Programming (explicit branching logic)")
    print("2. Agent-Based Programming (tools + delegation)")
    print()
    
    # Initialize processors
    traditional = TraditionalTextProcessor()
    
    # Check if we can run agent approach
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found - skipping agent approach")
        print("   Create a .env file with your API key to see the full comparison")
        print()
        agent = None
    else:
        agent = AgentTextProcessor()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        print(f"Input: {test_case['data'][:50]}...")
        print()
        
        # Traditional approach
        print("🔧 TRADITIONAL APPROACH:")
        try:
            if test_case['task'] == "Extract all email addresses":
                results = traditional.process_text(test_case['data'], "email")
                print(f"   Result: {results}")
            elif "Engineering department" in test_case['task']:
                # Traditional approach struggles with complex tasks
                print("   Result: ❌ Cannot handle complex filtering tasks")
                print("   (Would require additional explicit logic)")
            else:
                results = traditional.process_text(test_case['data'], "email")
                print(f"   Result: {results}")
        except Exception as e:
            print(f"   Result: ❌ Error - {e}")
        
        print()
        
        # Agent approach
        if agent:
            print("🤖 AGENT APPROACH:")
            try:
                result = agent.process_text(test_case['data'], test_case['task'])
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Result: ❌ Error - {e}")
        else:
            print("🤖 AGENT APPROACH: (Skipped - no API key)")
        
        print()
        print("-" * 80)
        print()
    
    print("KEY DIFFERENCES:")
    print()
    print("Traditional Approach:")
    print("  ✅ No external dependencies")
    print("  ✅ Predictable performance")
    print("  ❌ Rigid - only handles pre-programmed scenarios")
    print("  ❌ Complex branching logic")
    print("  ❌ Hard to extend with new formats/tasks")
    print("  ❌ Breaks on unexpected inputs")
    print()
    print("Agent Approach:")
    print("  ✅ Flexible - adapts to new scenarios")
    print("  ✅ Simple business logic tools")
    print("  ✅ Easy to extend with new tools")
    print("  ✅ Handles complex, multi-step tasks")
    print("  ❌ Requires API calls (cost/latency)")
    print("  ❌ Less predictable (AI behavior)")
    print()
    print("The Future: Write business logic tools, let agents combine them!")


if __name__ == "__main__":
    run_demo()
