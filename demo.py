#!/usr/bin/env python3
"""
Side-by-side demonstration of both approaches.

This script runs the same contact import test cases through both the traditional
imperative approach and the agent-based approach to show the difference.
"""

import os
from traditional_approach import TraditionalContactImporter
from agent_approach import AgentContactImporter


def run_demo():
    """Run both approaches side by side for comparison."""
    
    # Test cases that demonstrate the paradigm difference
    test_cases = [
        {
            "name": "Standard CRM Export",
            "data": """First Name,Last Name,Email,Phone
John,Doe,john@example.com,555-123-4567
Jane,Smith,jane@test.org,555-987-6543""",
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
            "name": "International Format (Spanish)",
            "data": """Nombre,Apellidos,Correo,Teléfono
Luis,García,luis@empresa.es,+34 91 123 4567
María,López,maria@test.es,+34 93 987 6543""",
            "task": "Import Spanish contact list"
        },
        {
            "name": "Pipe-Delimited No Headers",
            "data": """John Doe|john@example.com|555-123-4567
Jane Smith|jane@test.org|555-987-6543""",
            "task": "Import pipe-delimited data without headers"
        },
        {
            "name": "Mixed Format with Notes",
            "data": """Contact,Primary Info,Notes
John Doe,john@example.com,Phone: 555-123-4567 Company: Acme
Jane Smith,Call 555-987-6543,Email: jane@test.org""",
            "task": "Import contacts with mixed data in notes"
        },
        {
            "name": "Unexpected Legacy System Export",
            "data": """"Contact Info","Details","Extra"
"Smith, Jane (Manager)","jane.smith@company.com | Mobile: +1-555-0123","Dept: Sales, Start: 2020"
"Rodriguez, Carlos","carlos.r@email.com Phone: 555.987.6543","Engineering Team Lead\"""",
            "task": "Import contacts from messy legacy system export"
        }
    ]
    
    print("=" * 80)
    print("CONTACT IMPORTER: TRADITIONAL vs AGENT-BASED PROGRAMMING")
    print("=" * 80)
    print()
    print("This demo shows the same contact import tasks solved with two approaches:")
    print("1. Traditional Imperative Programming (explicit handling of every format)")
    print("2. Agent-Based Programming (single tool + intelligent delegation)")
    print()
    
    # Initialize processors
    traditional = TraditionalContactImporter()
    
    # Check if we can run agent approach
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found - skipping agent approach")
        print("   Create a .env file with your API key to see the full comparison")
        print()
        agent = None
    else:
        try:
            agent = AgentContactImporter()
        except Exception as e:
            print(f"⚠️  Could not initialize agent: {e}")
            agent = None
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        print(f"Data: {test_case['data'][:60]}...")
        print()
        
        # Traditional approach
        print("🔧 TRADITIONAL APPROACH:")
        try:
            contacts = traditional.import_contacts(test_case['data'], test_case['task'])
            print("   Results:")
            for j, contact in enumerate(contacts, 1):
                # Format contact nicely
                name = f"{contact['first_name'] or ''} {contact['last_name'] or ''}".strip()
                email = contact['email'] or 'No email'
                phone = contact['phone'] or 'No phone'
                print(f"     {j}. {name} | {email} | {phone}")
        except Exception as e:
            print(f"   Result: ❌ Error - {e}")
        
        print()
        
        # Agent approach
        if agent:
            print("🤖 AGENT APPROACH:")
            try:
                result = agent.import_contacts(test_case['data'], test_case['task'])
                print("   Agent Response:")
                # Format the agent's response nicely
                lines = result.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
                
                # Show the contacts that were actually filed
                contacts = agent.get_contacts()
                print(f"   \n   Contacts Filed ({len(contacts)}):")
                for j, contact in enumerate(contacts, 1):
                    name = f"{contact['first_name'] or ''} {contact['last_name'] or ''}".strip()
                    email = contact['email'] or 'No email'
                    phone = contact['phone'] or 'No phone'
                    print(f"     {j}. {name} | {email} | {phone}")
                    
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
    print("  ✅ Works offline")
    print("  ❌ Rigid - only handles pre-programmed column names")
    print("  ❌ Complex branching logic for each delimiter/format")
    print("  ❌ Hard to extend with new languages/formats")
    print("  ❌ Struggles with mixed data formats")
    print("  ❌ Cannot adapt to unexpected CSV structures")
    print()
    print("Agent Approach:")
    print("  ✅ Flexible - adapts to new CSV structures automatically")
    print("  ✅ Simple business logic (single file_contact tool)")
    print("  ✅ Easy to extend with new tools")
    print("  ✅ Handles international formats and languages")
    print("  ✅ Can extract data from mixed/unstructured fields")
    print("  ✅ Adapts to unexpected column names and formats")
    print("  ❌ Requires API calls (cost/latency)")
    print("  ❌ Less predictable (AI behavior)")
    print("  ❌ Needs internet connection")
    print()
    print("🚀 The Future: Write simple business logic tools, let agents combine them intelligently!")
    print()
    print("Notice how the traditional approach requires explicit handling of every")
    print("possible CSV format, delimiter, and column name variation, while the")
    print("agent approach adapts automatically to new formats using the same single tool.")


if __name__ == "__main__":
    run_demo()