import re
from typing import Dict, Any, Optional
from decimal import Decimal

class DataExtractor:
    def __init__(self):
        # Regex patterns for common tax document fields
        self.patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'ein': r'\b\d{2}-\d{7}\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'currency': r'\$?(\d{1,3}(?:,\d{3})*\.\d{2}|\d+\.\d{2})',
            'date': r'\b(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}-\d{1,2})\b',
            'box_number': r'box\s+(\d+[a-z]?)',
        }

    def extract_ssn(self, text: str) -> Optional[str]:
        """Extract Social Security Number"""
        match = re.search(self.patterns['ssn'], text)
        return match.group(0) if match else None

    def extract_ein(self, text: str) -> Optional[str]:
        """Extract Employer Identification Number"""
        match = re.search(self.patterns['ein'], text)
        return match.group(0) if match else None

    def extract_currency_values(self, text: str) -> list:
        """Extract all currency values from text"""
        matches = re.findall(self.patterns['currency'], text)
        values = []
        for match in matches:
            # Remove commas and convert to float
            clean_value = match.replace(',', '').replace('$', '')
            try:
                values.append(float(clean_value))
            except ValueError:
                continue
        return values

    def extract_w2_data(self, text: str) -> Dict[str, Any]:
        """Extract W-2 specific data"""
        data = {}

        # Extract SSN
        data['ssn'] = self.extract_ssn(text)

        # Extract currency values (boxes 1-6 typically)
        currency_values = self.extract_currency_values(text)

        # Map to W-2 boxes (simplified mapping)
        box_mappings = {
            1: 'wages_tips_other_comp',
            2: 'federal_income_tax_withheld',
            3: 'social_security_wages',
            4: 'social_security_tax_withheld',
            5: 'medicare_wages',
            6: 'medicare_tax_withheld'
        }

        for i, value in enumerate(currency_values[:6]):
            box_num = i + 1
            if box_num in box_mappings:
                data[box_mappings[box_num]] = value

        return data

    def extract_1099_data(self, text: str) -> Dict[str, Any]:
        """Extract 1099 specific data"""
        data = {}

        # Extract SSN or EIN
        data['ssn'] = self.extract_ssn(text)
        data['ein'] = self.extract_ein(text)

        # Extract currency values
        currency_values = self.extract_currency_values(text)

        # For 1099-MISC, box 7 is nonemployee compensation
        if len(currency_values) >= 1:
            data['nonemployee_compensation'] = currency_values[0]
        if len(currency_values) >= 2:
            data['federal_income_tax_withheld'] = currency_values[1]

        return data

    def extract_receipt_data(self, text: str) -> Dict[str, Any]:
        """Extract receipt data"""
        data = {}

        # Extract total amount (usually the largest currency value)
        currency_values = self.extract_currency_values(text)
        if currency_values:
            data['total_amount'] = max(currency_values)

        # Extract date
        date_match = re.search(self.patterns['date'], text)
        if date_match:
            data['date'] = date_match.group(0)

        return data

    def extract_data(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract data based on document type"""
        if doc_type == 'w2':
            return self.extract_w2_data(text)
        elif doc_type.startswith('1099'):
            return self.extract_1099_data(text)
        elif doc_type == 'receipt':
            return self.extract_receipt_data(text)
        else:
            return {}
