#!/usr/bin/env python3
"""
Traditional Imperative Approach: Contact List Importer

This demonstrates the traditional way of programming where we must explicitly
handle every possible CSV format, column name variation, and data structure.
The complexity explodes as we try to handle all the edge cases.
"""

import csv
import re
from io import StringIO
from typing import Dict, List, Optional, Tuple, Any


class TraditionalContactImporter:
    """
    Traditional imperative approach to contact importing.
    
    Notice the explosion of conditional logic needed to handle every possible
    combination of CSV format, column names, delimiters, and data structures.
    """
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\+?[\d\s\-\(\)\.]{10,}')
        
        # All possible column name variations we need to handle
        self.first_name_variations = [
            'first name', 'first_name', 'fname', 'first', 'given name', 
            'given_name', 'given', 'nombre', 'prenom', 'vorname'
        ]
        self.last_name_variations = [
            'last name', 'last_name', 'lname', 'last', 'surname', 
            'family name', 'family_name', 'family', 'apellidos', 
            'apellido', 'nom', 'nachname'
        ]
        self.email_variations = [
            'email', 'e-mail', 'email address', 'email_address', 
            'mail', 'correo', 'courriel', 'e_mail'
        ]
        self.phone_variations = [
            'phone', 'phone number', 'phone_number', 'tel', 'telephone', 
            'mobile', 'cell', 'cellular', 'work phone', 'home phone',
            'teléfono', 'telefono', 'téléphone'
        ]
        self.company_variations = [
            'company', 'organization', 'org', 'employer', 'business',
            'empresa', 'société', 'unternehmen'
        ]
        self.full_name_variations = [
            'name', 'full name', 'full_name', 'display name', 
            'contact name', 'contact', 'nombre completo'
        ]
    
    def import_contacts(self, csv_text: str, task: str = "Import contacts") -> List[Dict[str, Optional[str]]]:
        """
        Main import function with rigid branching logic.
        
        This is where the complexity explodes - we need explicit handling
        for every possible combination of CSV format and column structure.
        """
        
        # Step 1: Detect delimiter (explicit logic for each possibility)
        delimiter = self._detect_delimiter(csv_text)
        
        # Step 2: Parse CSV with detected delimiter
        try:
            if delimiter == ',':
                parsed_data = self._parse_comma_csv(csv_text)
            elif delimiter == ';':
                parsed_data = self._parse_semicolon_csv(csv_text)
            elif delimiter == '\t':
                parsed_data = self._parse_tab_csv(csv_text)
            elif delimiter == '|':
                parsed_data = self._parse_pipe_csv(csv_text)
            else:
                raise ValueError(f"Unsupported delimiter: {delimiter}")
        except Exception as e:
            raise ValueError(f"CSV parsing failed: {e}")
        
        # Step 3: Detect if headers exist (more explicit logic)
        has_headers = self._detect_headers(parsed_data['rows'][0] if parsed_data['rows'] else [])
        
        # Step 4: Process based on header detection
        if has_headers:
            return self._process_csv_with_headers(parsed_data['rows'])
        else:
            return self._process_csv_without_headers(parsed_data['rows'])
    
    def _detect_delimiter(self, text: str) -> str:
        """
        Rigid delimiter detection with explicit rules.
        
        We must check each delimiter type with specific logic.
        """
        first_line = text.split('\n')[0] if text else ""
        
        # Count each delimiter type
        comma_count = first_line.count(',')
        semicolon_count = first_line.count(';')
        tab_count = first_line.count('\t')
        pipe_count = first_line.count('|')
        
        # Explicit decision tree for delimiter selection
        if comma_count > 0 and comma_count >= semicolon_count and comma_count >= tab_count and comma_count >= pipe_count:
            return ','
        elif semicolon_count > 0 and semicolon_count >= tab_count and semicolon_count >= pipe_count:
            return ';'
        elif tab_count > 0 and tab_count >= pipe_count:
            return '\t'
        elif pipe_count > 0:
            return '|'
        else:
            return ','  # Default fallback
    
    def _parse_comma_csv(self, text: str) -> Dict[str, Any]:
        """Parse comma-delimited CSV with specific comma handling."""
        try:
            reader = csv.reader(StringIO(text), delimiter=',')
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            return {"success": True, "rows": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_semicolon_csv(self, text: str) -> Dict[str, Any]:
        """Parse semicolon-delimited CSV with specific semicolon handling."""
        try:
            reader = csv.reader(StringIO(text), delimiter=';')
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            return {"success": True, "rows": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_tab_csv(self, text: str) -> Dict[str, Any]:
        """Parse tab-delimited CSV with specific tab handling."""
        try:
            reader = csv.reader(StringIO(text), delimiter='\t')
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            return {"success": True, "rows": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_pipe_csv(self, text: str) -> Dict[str, Any]:
        """Parse pipe-delimited CSV with specific pipe handling."""
        try:
            reader = csv.reader(StringIO(text), delimiter='|')
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            return {"success": True, "rows": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _detect_headers(self, first_row: List[str]) -> bool:
        """
        Detect headers with explicit rules for each scenario.
        """
        if not first_row:
            return False
        
        # Check each cell in first row
        header_score = 0
        for cell in first_row:
            cell = cell.strip().lower()
            
            # Explicit checks for header patterns
            if any(name_var in cell for name_var in self.first_name_variations):
                header_score += 2
            elif any(name_var in cell for name_var in self.last_name_variations):
                header_score += 2
            elif any(email_var in cell for email_var in self.email_variations):
                header_score += 2
            elif any(phone_var in cell for phone_var in self.phone_variations):
                header_score += 2
            elif any(company_var in cell for company_var in self.company_variations):
                header_score += 2
            elif any(name_var in cell for name_var in self.full_name_variations):
                header_score += 2
            elif cell and not cell.replace('.', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
                if '@' not in cell:  # Not an email
                    header_score += 1
        
        return header_score >= len(first_row)
    
    def _process_csv_with_headers(self, rows: List[List[str]]) -> List[Dict[str, Optional[str]]]:
        """
        Process CSV with headers - explicit mapping for each column type.
        """
        if not rows:
            return []
        
        headers = [h.strip().lower() for h in rows[0]]
        contacts = []
        
        for row in rows[1:]:
            contact = self._extract_contact_with_headers(headers, row)
            contacts.append(contact)
        
        return contacts
    
    def _process_csv_without_headers(self, rows: List[List[str]]) -> List[Dict[str, Optional[str]]]:
        """
        Process CSV without headers - must guess column meanings.
        """
        contacts = []
        
        for row in rows:
            contact = self._extract_contact_without_headers(row)
            contacts.append(contact)
        
        return contacts
    
    def _extract_contact_with_headers(self, headers: List[str], row: List[str]) -> Dict[str, Optional[str]]:
        """
        Extract contact with explicit header mapping logic.
        """
        contact = {
            "first_name": None,
            "last_name": None,
            "email": None,
            "phone": None,
            "company": None
        }
        
        # Create row dictionary
        row_dict = {}
        for i, value in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = value.strip() if value else ""
        
        # Explicit mapping for first name
        for header, value in row_dict.items():
            if any(var in header for var in self.first_name_variations):
                contact["first_name"] = value if value else None
                break
        
        # Explicit mapping for last name
        for header, value in row_dict.items():
            if any(var in header for var in self.last_name_variations):
                contact["last_name"] = value if value else None
                break
        
        # If no separate first/last, look for full name
        if not contact["first_name"] and not contact["last_name"]:
            for header, value in row_dict.items():
                if any(var in header for var in self.full_name_variations):
                    if value:
                        first, last = self._split_full_name(value)
                        contact["first_name"] = first
                        contact["last_name"] = last
                    break
        
        # Explicit mapping for email
        for header, value in row_dict.items():
            if any(var in header for var in self.email_variations):
                if value and '@' in value:
                    email = self._extract_email_from_text(value)
                    if email:
                        contact["email"] = email
                break
        
        # If no explicit email field, search all fields
        if not contact["email"]:
            for value in row_dict.values():
                if value and '@' in value:
                    email = self._extract_email_from_text(value)
                    if email:
                        contact["email"] = email
                        break
        
        # Explicit mapping for phone
        for header, value in row_dict.items():
            if any(var in header for var in self.phone_variations):
                if value:
                    phone = self._normalize_phone(value)
                    if phone:
                        contact["phone"] = phone
                break
        
        # If no explicit phone field, search all fields
        if not contact["phone"]:
            for value in row_dict.values():
                if value:
                    phone = self._normalize_phone(value)
                    if phone:
                        contact["phone"] = phone
                        break
        
        # Explicit mapping for company
        for header, value in row_dict.items():
            if any(var in header for var in self.company_variations):
                contact["company"] = value if value else None
                break
        
        return contact
    
    def _extract_contact_without_headers(self, row: List[str]) -> Dict[str, Optional[str]]:
        """
        Extract contact without headers - must guess based on patterns.
        """
        contact = {
            "first_name": None,
            "last_name": None,
            "email": None,
            "phone": None,
            "company": None
        }
        
        # Try to guess column meanings based on content patterns
        for i, value in enumerate(row):
            value = value.strip() if value else ""
            
            if not value:
                continue
            
            # Check if it's an email
            if '@' in value and not contact["email"]:
                email = self._extract_email_from_text(value)
                if email:
                    contact["email"] = email
                    continue
            
            # Check if it's a phone number
            phone = self._normalize_phone(value)
            if phone and not contact["phone"]:
                contact["phone"] = phone
                continue
            
            # Check if it looks like a name (first column usually)
            if i == 0 and not contact["first_name"]:
                if ' ' in value:
                    # Looks like full name
                    first, last = self._split_full_name(value)
                    contact["first_name"] = first
                    contact["last_name"] = last
                else:
                    # Single name, assume first name
                    contact["first_name"] = value
                continue
            
            # Remaining columns might be company
            if i >= 2 and not contact["company"]:
                # Skip if it looks like personal data
                if '@' not in value and not self._normalize_phone(value):
                    contact["company"] = value
        
        return contact
    
    def _split_full_name(self, full_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Split full name into first and last name."""
        if not full_name or not full_name.strip():
            return None, None
        
        parts = full_name.strip().split()
        
        if len(parts) == 1:
            return parts[0], None
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            # More than 2 parts - first is first name, rest is last name
            return parts[0], ' '.join(parts[1:])
    
    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email from text using regex."""
        if not text:
            return None
        
        match = self.email_pattern.search(text)
        return match.group(0) if match else None
    
    def _normalize_phone(self, value: str) -> Optional[str]:
        """
        Normalize phone number with explicit formatting rules.
        """
        if not value:
            return None
        
        # Extract digits only
        digits = re.sub(r'\D', '', value)
        
        # Explicit formatting based on digit count
        if len(digits) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith('1'):
            # US format with country code: +1 (XXX) XXX-XXXX
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif len(digits) >= 10:
            # International format - try to preserve original formatting
            match = self.phone_pattern.search(value)
            if match:
                return match.group(0).strip()
        
        return None


def main():
    """
    Demonstration of the traditional approach.
    
    Notice how rigid and complex this is - we must explicitly handle
    every possible CSV format and column name variation.
    """
    
    # Same test cases as agent approach
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
    
    importer = TraditionalContactImporter()
    
    print("=" * 70)
    print("TRADITIONAL IMPERATIVE APPROACH - CONTACT IMPORTER")
    print("=" * 70)
    print()
    print("Notice the rigid, explicit handling of each CSV format and")
    print("column name variation. Adding new formats requires modifying")
    print("the core logic with more conditional branches.")
    print()
    
    for test_case in test_cases:
        print(f"Processing: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        
        try:
            contacts = importer.import_contacts(test_case['data'], test_case['task'])
            print("Results:")
            for i, contact in enumerate(contacts, 1):
                print(f"  {i}. {contact}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)
        print()
    
    print("LIMITATIONS OF TRADITIONAL APPROACH:")
    print("• Must explicitly handle every CSV format combination")
    print("• Requires hardcoded lists of column name variations")
    print("• Adding new languages/formats requires core code changes")
    print("• Complex branching logic becomes unmaintainable")
    print("• Limited flexibility for unexpected data structures")
    print("• Cannot adapt to new column naming conventions")


if __name__ == "__main__":
    main()