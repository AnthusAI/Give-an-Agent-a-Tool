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
        
        # Header synonyms - must maintain mappings for every language and variation
        self.header_synonyms = {
            "first_name": ["first", "first name", "given", "nombre", "prenom", "vorname"],
            "last_name": ["last", "last name", "surname", "apellidos", "apellido", "nom", "nachname"],
            "email": ["email", "work email", "correo", "email address", "e-mail", "mail"],
            "phone": ["phone", "telephone", "mobile", "cell", "teléfono", "telefono"],
            "name": ["name", "full name", "contact name", "nombre completo"]
        }
    
    def import_contacts(self, csv_text: str, task: str = "Import contacts") -> List[Dict[str, Optional[str]]]:
        """
        Main import function with rigid branching logic.
        
        Requires explicit handling for every possible CSV format scenario.
        """
        
        # Step 1: Parse table with auto-detect delimiter
        table = self._parse_table(csv_text, auto_detect_delimiter=True)
        
        # Step 2: Normalize headers using synonyms
        headers = self._normalize_headers(table["headers"], using=self.header_synonyms)
        
        # Step 3: Process each row
        out = []
        for row in table["rows"]:
            try:
                # Infer name using explicit rules
                first, last = self._infer_name(row, headers)
                
                # Find email with fallback logic
                email = self._find_email(row, headers, fallback_to_notes=True)
                
                # Check for missing required data
                if not (first or last) or not email:
                    raise ValueError("Missing name or email — add another case handler")
                
                out.append({
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "phone": self._find_phone(row, headers)
                })
                
            except ValueError as e:
                # Breaks on unexpected formats
                raise ValueError(f"Unsupported format: {e}")
        
        return out
    
    def _parse_table(self, text: str, auto_detect_delimiter: bool = True) -> Dict[str, Any]:
        """Parse table with delimiter detection."""
        if auto_detect_delimiter:
            delimiter = self._detect_delimiter(text)
        else:
            delimiter = ","
        
        try:
            reader = csv.reader(StringIO(text), delimiter=delimiter)
            rows = [row for row in reader if any(cell.strip() for cell in row)]
            
            if not rows:
                raise ValueError("No data found")
            
            # Assume first row is headers if it looks like headers
            if self._looks_like_headers(rows[0]):
                return {"headers": rows[0], "rows": rows[1:]}
            else:
                # Generate generic headers
                num_cols = len(rows[0]) if rows else 0
                headers = [f"column_{i}" for i in range(num_cols)]
                return {"headers": headers, "rows": rows}
                
        except Exception as e:
            raise ValueError(f"CSV parsing failed: {e}")
    
    def _detect_delimiter(self, text: str) -> str:
        """Detect delimiter with explicit rules."""
        first_line = text.split('\n')[0] if text else ""
        
        # Count each delimiter type
        comma_count = first_line.count(',')
        semicolon_count = first_line.count(';')
        tab_count = first_line.count('\t')
        pipe_count = first_line.count('|')
        
        # Explicit decision tree
        if comma_count > 0 and comma_count >= max(semicolon_count, tab_count, pipe_count):
            return ','
        elif semicolon_count > 0 and semicolon_count >= max(tab_count, pipe_count):
            return ';'
        elif tab_count > 0 and tab_count >= pipe_count:
            return '\t'
        elif pipe_count > 0:
            return '|'
        else:
            return ','  # Default fallback
    
    def _looks_like_headers(self, row: List[str]) -> bool:
        """Detect if row contains headers using explicit rules."""
        header_score = 0
        for cell in row:
            cell_lower = cell.strip().lower()
            
            # Check against known header patterns
            for canonical, variants in self.header_synonyms.items():
                if any(variant in cell_lower for variant in variants):
                    header_score += 1
                    break
        
        return header_score >= len(row) * 0.5
    
    def _normalize_headers(self, headers: List[str], using: Dict[str, List[str]]) -> List[str]:
        """Normalize headers using synonym mappings."""
        normalized = []
        for h in headers:
            key = h.strip().lower()
            best = None
            
            # Check each canonical field for matches
            for canonical, variants in using.items():
                if key in variants or key == canonical:
                    best = canonical
                    break
            
            normalized.append(best or key)  # Hope for the best if no match
        
        return normalized
    
    def _infer_name(self, row: List[str], headers: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Infer name with explicit branching logic."""
        row_dict = dict(zip(headers, row))
        
        # Try to find explicit first/last name fields
        first = row_dict.get("first_name")
        last = row_dict.get("last_name")
        
        if first or last:
            return first, last
        
        # Look for full name field
        name = row_dict.get("name")
        if name:
            # Handle different name formats with explicit rules
            if "," in name:  # "Last, First" format
                parts = [p.strip() for p in name.split(",", 1)]
                if len(parts) == 2:
                    return parts[1], parts[0]  # First, Last
            else:
                # Split on spaces
                parts = name.split()
                if len(parts) >= 2:
                    return parts[0], " ".join(parts[1:])
                elif len(parts) == 1:
                    return parts[0], None
        
        return None, None
    
    def _find_email(self, row: List[str], headers: List[str], fallback_to_notes: bool = False) -> Optional[str]:
        """Find email with explicit field checking."""
        row_dict = dict(zip(headers, row))
        
        # Check explicit email field
        email = row_dict.get("email")
        if email and "@" in email:
            match = self.email_pattern.search(email)
            if match:
                return match.group(0)
        
        # Fallback to searching all fields if enabled
        if fallback_to_notes:
            for value in row:
                if value and "@" in value:
                    match = self.email_pattern.search(value)
                    if match:
                        return match.group(0)
        
        return None
    
    def _find_phone(self, row: List[str], headers: List[str]) -> Optional[str]:
        """Find phone with explicit field checking."""
        row_dict = dict(zip(headers, row))
        
        # Check explicit phone field
        phone = row_dict.get("phone")
        if phone:
            normalized = self._normalize_phone(phone)
            if normalized:
                return normalized
        
        # Search all fields for phone patterns
        for value in row:
            if value:
                normalized = self._normalize_phone(value)
                if normalized:
                    return normalized
        
        return None
    
    def _normalize_phone(self, value: str) -> Optional[str]:
        """Normalize phone number with explicit formatting rules."""
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
    
    # Test cases that demonstrate the limitations
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
            "name": "International Format",
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
            "name": "Unexpected Legacy Export (This breaks!)",
            "data": """"Contact Info","Details","Extra"
"Smith, Jane (Manager)","jane.smith@company.com | Mobile: +1-555-0123","Dept: Sales, Start: 2020"
"Rodriguez, Carlos","carlos.r@email.com Phone: 555.987.6543","Engineering Team Lead\"""",
            "task": "Import contacts from messy legacy system export"
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
                name = f"{contact['first_name'] or ''} {contact['last_name'] or ''}".strip()
                email = contact['email'] or 'No email'
                phone = contact['phone'] or 'No phone'
                print(f"  {i}. {name} | {email} | {phone}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   ^ Breaks on unexpected formats")
        
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