import os
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI


class ContactStorage:
    """
    Business logic for storing contacts.
    
    This is the only code that needs to be written - the business logic.
    The agent handles all the parsing, format detection, and orchestration.
    """
    
    def __init__(self):
        self.contacts: List[Dict[str, Optional[str]]] = []
    
    def file_contact(self, name: str, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        File a single contact record.
        
        Args:
            name: Full name of the contact (required)
            email: Email address (optional)
            phone: Phone number (optional)
            
        Returns:
            Dict with success status and contact details
        """
        # Validate required fields
        if not name or not name.strip():
            return {
                "success": False,
                "error": "Name is required"
            }
        
        # At least one contact method is required
        if not email and not phone:
            return {
                "success": False,
                "error": "Either email or phone is required"
            }
        
        # Parse name into first/last if possible
        name_parts = name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
        else:
            first_name = name.strip()
            last_name = None
        
        # Create contact record
        contact = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email.strip() if email else None,
            "phone": phone.strip() if phone else None
        }
        
        self.contacts.append(contact)
        
        return {
            "success": True,
            "message": f"Filed contact: {name}",
            "contact": contact
        }
    
    def get_contacts(self) -> List[Dict[str, Optional[str]]]:
        """Get all filed contacts."""
        return self.contacts.copy()
    
    def clear_contacts(self) -> None:
        """Clear all contacts."""
        self.contacts.clear()


class AgentContactImporter:
    """
    Agent-based contact importer that uses a single business logic tool.
    
    The agent analyzes the CSV structure and uses the file_contact tool
    to store each contact it finds.
    """
    
    def __init__(self):
        self.storage = ContactStorage()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        
        # Define the single tool for the OpenAI API
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "file_contact",
                    "description": "Store a single contact record where name is required and at least one of email or phone is provided",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string", 
                                "description": "Full name of the contact"
                            },
                            "email": {
                                "type": "string", 
                                "description": "Email address (optional)"
                            },
                            "phone": {
                                "type": "string", 
                                "description": "Phone number (optional)"
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        ]
    
    def import_contacts(self, csv_text: str, task: str = "Import and file contacts") -> str:
        """
        Import contacts using the agent approach.
        
        The agent will analyze the CSV structure and use the file_contact tool
        to store each contact it finds.
        """
        
        # Clear previous contacts
        self.storage.clear_contacts()
        
        system_prompt = """You are a contact import assistant.
Goal: read the CSV below and file each contact you can find.
Use the single tool file_contact(name, email?, phone?) to file each person.
Infer names and emails/phones from whatever headers or content appear.

You can handle various CSV formats:
- Different delimiters (comma, semicolon, tab, pipe)
- With or without headers
- Different column names and languages
- Mixed data in cells

For each person you identify, call file_contact with their name and any email/phone you find."""

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
        # Convert the message to a dictionary format for the API
        message_dict = {
            "role": message.role,
            "content": message.content,
        }
        if message.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        messages.append(message_dict)
        
        # Execute tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the file_contact method
                if function_name == "file_contact":
                    result = self.storage.file_contact(**function_args)
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

    def get_contacts(self) -> List[Dict[str, Optional[str]]]:
        """Get all contacts that have been filed."""
        return self.storage.get_contacts()


if __name__ == "__main__":
    # Example usage
    importer = AgentContactImporter()
    
    # Test with a simple CSV
    csv_data = """Name,Email
John Doe,john@example.com
Jane Smith,jane@test.org"""
    
    try:
        result = importer.import_contacts(csv_data)
        print("Agent Result:", result)
        print("\nFiled Contacts:")
        for contact in importer.get_contacts():
            print(f"  - {contact['first_name']} {contact['last_name']}: {contact['email']}")
    except Exception as e:
        print(f"Error: {e}")