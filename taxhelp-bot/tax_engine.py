class TaxEngine:
    def __init__(self):
        # 2023 Federal Income Tax Brackets (Single Filer)
        self.federal_brackets = {
            'single': [
                (0, 11000, 0.10),
                (11000, 44725, 0.12),
                (44725, 95375, 0.22),
                (95375, 182100, 0.24),
                (182100, 231250, 0.32),
                (231250, 578125, 0.35),
                (578125, float('inf'), 0.37)
            ],
            'married_filing_jointly': [
                (0, 22000, 0.10),
                (22000, 89450, 0.12),
                (89450, 190750, 0.22),
                (190750, 364200, 0.24),
                (364200, 462500, 0.32),
                (462500, 693750, 0.35),
                (693750, float('inf'), 0.37)
            ]
        }

        # Standard Deduction 2023
        self.standard_deduction = {
            'single': 13850,
            'married_filing_jointly': 27700
        }

    def calculate_federal_tax(self, tax_input):
        """Calculate federal income tax based on extracted data and user answers."""
        extracted_data = tax_input.get('extracted_data', {})
        user_answers = tax_input.get('user_answers', {})

        # Get filing status
        filing_status = user_answers.get('filing_status', 'single')

        # Calculate total income from W-2 forms
        total_wages = 0
        total_withheld = 0

        for doc_type, doc_data in extracted_data.items():
            if doc_type == 'w2' and 'data' in doc_data:
                data = doc_data['data']
                total_wages += data.get('wages_tips_other_comp', 0)
                total_withheld += data.get('federal_income_tax_withheld', 0)

        # Calculate taxable income (simplified - no deductions considered)
        taxable_income = max(0, total_wages - self.standard_deduction.get(filing_status, 0))

        # Calculate tax owed using progressive brackets
        tax_owed = self._calculate_progressive_tax(taxable_income, filing_status)

        # Calculate refund or amount due
        if total_withheld > tax_owed:
            refund = total_withheld - tax_owed
            amount_due = 0
        else:
            refund = 0
            amount_due = tax_owed - total_withheld

        return {
            'taxable_income': taxable_income,
            'tax_owed': tax_owed,
            'withheld': total_withheld,
            'refund': round(refund, 2),
            'amount_due': round(amount_due, 2)
        }

    def calculate_state_tax(self, tax_input, state):
        """Calculate state income tax (simplified for CA)."""
        extracted_data = tax_input.get('extracted_data', {})
        user_answers = tax_input.get('user_answers', {})

        # Calculate total income
        total_wages = 0
        for doc_type, doc_data in extracted_data.items():
            if doc_type == 'w2' and 'data' in doc_data:
                data = doc_data['data']
                total_wages += data.get('wages_tips_other_comp', 0)

        # CA State Tax (simplified single rate for demo)
        if state.upper() == 'CA':
            state_tax_rate = 0.133  # Approximate effective rate
            state_tax_owed = total_wages * state_tax_rate
            return {
                'state': state,
                'taxable_income': total_wages,
                'tax_owed': round(state_tax_owed, 2),
                'refund': 0,  # Simplified
                'amount_due': round(state_tax_owed, 2)
            }

        return {'state': state, 'tax_owed': 0, 'refund': 0, 'amount_due': 0}

    def calculate_self_employment_tax(self, tax_input):
        """Calculate self-employment tax for 1099 income."""
        extracted_data = tax_input.get('extracted_data', {})

        # Calculate total 1099 income
        total_1099_income = 0
        for doc_type, doc_data in extracted_data.items():
            if doc_type.startswith('1099') and 'data' in doc_data:
                data = doc_data['data']
                total_1099_income += data.get('nonemployee_compensation', 0)

        if total_1099_income == 0:
            return {'total_income': 0, 'social_security_tax': 0, 'medicare_tax': 0, 'total_tax': 0}

        # Self-employment tax calculation (2023 rates)
        # Social Security tax: 12.4% on 92.35% of income (self-employed pay both halves)
        social_security_base = min(total_1099_income * 0.9235, 160200)  # 2023 SS wage base
        social_security_tax = social_security_base * 0.124

        # Medicare tax: 2.9% on all income
        medicare_tax = total_1099_income * 0.029

        # Additional Medicare tax for high earners (0.9% on income over $200,000 single)
        additional_medicare_tax = 0
        if total_1099_income > 200000:
            additional_medicare_tax = (total_1099_income - 200000) * 0.009

        total_tax = social_security_tax + medicare_tax + additional_medicare_tax

        return {
            'total_income': round(total_1099_income, 2),
            'social_security_tax': round(social_security_tax, 2),
            'medicare_tax': round(medicare_tax, 2),
            'additional_medicare_tax': round(additional_medicare_tax, 2),
            'total_tax': round(total_tax, 2)
        }

    def _calculate_progressive_tax(self, taxable_income, filing_status):
        """Calculate tax using progressive brackets."""
        brackets = self.federal_brackets.get(filing_status, self.federal_brackets['single'])
        tax_owed = 0

        for min_income, max_income, rate in brackets:
            if taxable_income > min_income:
                taxable_in_bracket = min(taxable_income - min_income, max_income - min_income)
                tax_owed += taxable_in_bracket * rate
            else:
                break

        return round(tax_owed, 2)
