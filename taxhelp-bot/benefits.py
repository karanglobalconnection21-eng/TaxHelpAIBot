from typing import Dict, List, Any
from config import Config

class BenefitsEngine:
    def __init__(self):
        self.config = Config()

    def screen_benefits(self, user_data: Dict[str, Any], tax_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen for potential benefits based on user data and tax situation"""
        benefits = []

        zip_code = user_data.get('zip_code', '')
        income = tax_data.get('summary', {}).get('agi', 0)
        filing_status = user_data.get('filing_status', 'single')
        dependents = user_data.get('dependents', 0)
        state = self._get_state_from_zip(zip_code)

        # Earned Income Tax Credit (EITC)
        eitc_eligible = self._check_eitc_eligibility(income, dependents, filing_status)
        if eitc_eligible:
            benefits.append({
                'program': 'Earned Income Tax Credit (EITC)',
                'likely': True,
                'reason': f'Income (${income:,.0f}) and {dependents} dependents qualify',
                'apply_url': 'https://www.irs.gov/individuals/free-tax-return-preparation-for-qualifying-taxpayers',
                'estimated_amount': self._estimate_eitc(income, dependents)
            })

        # Child Tax Credit
        if dependents > 0:
            benefits.append({
                'program': 'Child Tax Credit',
                'likely': True,
                'reason': f'{dependents} dependent(s) qualify for up to $2,000 per child',
                'apply_url': 'https://www.irs.gov/credits-deductions/child-tax-credit',
                'estimated_amount': min(dependents * 2000, 0)  # Would calculate properly
            })

        # California EITC (CalEITC)
        if state == 'CA' and eitc_eligible:
            benefits.append({
                'program': 'California Earned Income Tax Credit (CalEITC)',
                'likely': True,
                'reason': 'California supplement to federal EITC',
                'apply_url': 'https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html',
                'estimated_amount': self._estimate_caleitc(income, dependents)
            })

        # Young Child Tax Credit (California)
        if state == 'CA' and dependents > 0:
            young_children = sum(1 for dep in user_data.get('dependents_details', []) if dep.get('age', 0) < 6)
            if young_children > 0:
                benefits.append({
                    'program': 'Young Child Tax Credit (California)',
                    'likely': True,
                    'reason': f'{young_children} child(ren) under 6 qualify',
                    'apply_url': 'https://www.ftb.ca.gov/file/personal/credits/young-child-tax-credit.html',
                    'estimated_amount': young_children * 129  # 2024 amount
                })

        # SNAP/Food Stamps screening
        snap_eligible = self._check_snap_eligibility(income, dependents, zip_code)
        if snap_eligible:
            benefits.append({
                'program': 'SNAP (Food Stamps)',
                'likely': True,
                'reason': f'Income and household size may qualify for food assistance',
                'apply_url': 'https://www.fns.usda.gov/snap/supplemental-nutrition-assistance-program',
                'estimated_amount': None  # Variable based on household
            })

        # WIC (Women, Infants, and Children)
        if dependents > 0:
            benefits.append({
                'program': 'WIC (Women, Infants, and Children)',
                'likely': True,
                'reason': 'Program provides nutrition assistance for women, infants, and children',
                'apply_url': 'https://www.fns.usda.gov/wic/wic-how-apply',
                'estimated_amount': None
            })

        # Medi-Cal (California Medicaid)
        if state == 'CA':
            medi_cal_eligible = self._check_medi_cal_eligibility(income, dependents)
            if medi_cal_eligible:
                benefits.append({
                    'program': 'Medi-Cal (California Medicaid)',
                    'likely': True,
                    'reason': 'May qualify for health coverage',
                    'apply_url': 'https://www.medi-cal.ca.gov/',
                    'estimated_amount': None
                })

        # LIHEAP (Low Income Home Energy Assistance)
        liheap_eligible = self._check_liheap_eligibility(income, dependents, zip_code)
        if liheap_eligible:
            benefits.append({
                'program': 'LIHEAP (Home Energy Assistance)',
                'likely': True,
                'reason': 'May qualify for energy bill assistance',
                'apply_url': 'https://www.acf.hhs.gov/ocs/liheap',
                'estimated_amount': None
            })

        return benefits

    def _check_eitc_eligibility(self, income: float, dependents: int, filing_status: str) -> bool:
        """Check EITC eligibility"""
        # Simplified EITC rules for 2024
        max_income = {
            0: 17050,
            1: 24000,
            2: 24000,
            3: 24000
        }.get(dependents, 24000)

        return income <= max_income and dependents >= 0

    def _estimate_eitc(self, income: float, dependents: int) -> float:
        """Estimate EITC amount (simplified)"""
        # Very simplified calculation
        base_credit = dependents * 400
        phase_out_start = 9000 + dependents * 1000
        if income > phase_out_start:
            reduction = (income - phase_out_start) * 0.0765
            return max(0, base_credit - reduction)
        return base_credit

    def _estimate_caleitc(self, income: float, dependents: int) -> float:
        """Estimate CalEITC amount"""
        # California EITC is about 3.5% of federal EITC
        federal_eitc = self._estimate_eitc(income, dependents)
        return federal_eitc * 0.035

    def _check_snap_eligibility(self, income: float, dependents: int, zip_code: str) -> bool:
        """Check SNAP eligibility"""
        # Simplified SNAP gross income limits (2024)
        household_size = dependents + 1  # Assuming user + dependents
        gross_limit = {
            1: 1526,
            2: 2064,
            3: 2602,
            4: 3140,
            5: 3678,
            6: 4216,
            7: 4754,
            8: 5292
        }.get(min(household_size, 8), 5292 + (household_size - 8) * 448)

        monthly_income = income / 12
        return monthly_income <= gross_limit

    def _check_medi_cal_eligibility(self, income: float, dependents: int) -> bool:
        """Check Medi-Cal eligibility"""
        # Simplified - Medi-Cal has higher income limits
        household_size = dependents + 1
        fpl_percentage = 138  # 138% of FPL for most adults
        estimated_fpl = household_size * 15000  # Rough estimate
        income_limit = estimated_fpl * (fpl_percentage / 100)

        return income <= income_limit

    def _check_liheap_eligibility(self, income: float, dependents: int, zip_code: str) -> bool:
        """Check LIHEAP eligibility"""
        # LIHEAP income limits vary by household size and location
        household_size = dependents + 1
        income_limit = household_size * 12000  # Simplified
        return income <= income_limit

    def _get_state_from_zip(self, zip_code: str) -> str:
        """Get state from ZIP code"""
        if not zip_code:
            return 'CA'

        # Simplified mapping
        zip_state_map = {
            '9': 'CA',  # California ZIPs often start with 9
            '8': 'CA',  # Some CA ZIPs start with 8
            '7': 'OR',  # Oregon
            '6': 'WA',  # Washington
        }

        first_digit = zip_code[0]
        return zip_state_map.get(first_digit, 'CA')
