from typing import Dict, List, Any, Optional, Tuple
from langdetect import detect
from config import Config

class AdaptiveQA:
    def __init__(self):
        self.questions = {
            'en': {
                'filing_status': "What's your filing status?",
                'dependents': "How many dependents do you have?",
                'zip_code': "What's your ZIP code?",
                'gig_method': "For gig work, do you use standard mileage rate or actual expenses?",
                'miles': "How many business miles did you drive this year?",
                'phone_percent': "What percentage of your phone bill is for business use?",
                'home_office': "Do you have a home office? If yes, what's the square footage?",
                'state_specific': "Do you have any state-specific tax situations?"
            },
            'es': {
                'filing_status': "¿Cuál es tu estado civil para impuestos?",
                'dependents': "¿Cuántos dependientes tienes?",
                'zip_code': "¿Cuál es tu código postal?",
                'gig_method': "Para trabajo independiente, ¿usas tarifa de millaje estándar o gastos reales?",
                'miles': "¿Cuántas millas de negocio condujiste este año?",
                'phone_percent': "¿Qué porcentaje de tu factura de teléfono es para uso comercial?",
                'home_office': "¿Tienes una oficina en casa? Si es sí, ¿cuál es el área en pies cuadrados?",
                'state_specific': "¿Tienes alguna situación fiscal específica del estado?"
            }
        }

        self.options = {
            'en': {
                'filing_status': ['Single', 'Married Filing Jointly', 'Married Filing Separately', 'Head of Household', 'Qualifying Widow(er)'],
                'gig_method': ['Standard Mileage Rate', 'Actual Expenses']
            },
            'es': {
                'filing_status': ['Soltero', 'Casado Presentando Conjuntamente', 'Casado Presentando Separadamente', 'Cabeza de Hogar', 'Viudo Calificado'],
                'gig_method': ['Tarifa de Millaje Estándar', 'Gastos Reales']
            }
        }

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            lang = detect(text)
            return lang if lang in Config.SUPPORTED_LANGUAGES else 'en'
        except:
            return 'en'

    def get_next_question(self, user_data: Dict[str, Any], doc_types: List[str], language: str = 'en') -> Optional[Dict[str, Any]]:
        """Determine the next question to ask based on user data and documents"""

        # Basic information questions
        if 'filing_status' not in user_data:
            return {
                'key': 'filing_status',
                'question': self.questions[language]['filing_status'],
                'type': 'choice',
                'options': self.options[language]['filing_status']
            }

        if 'dependents' not in user_data:
            return {
                'key': 'dependents',
                'question': self.questions[language]['dependents'],
                'type': 'number'
            }

        if 'zip_code' not in user_data:
            return {
                'key': 'zip_code',
                'question': self.questions[language]['zip_code'],
                'type': 'text'
            }

        # Gig-specific questions if gig documents are present
        if any('1099' in doc_type.lower() for doc_type in doc_types):
            if 'gig_method' not in user_data:
                return {
                    'key': 'gig_method',
                    'question': self.questions[language]['gig_method'],
                    'type': 'choice',
                    'options': self.options[language]['gig_method']
                }

            if user_data.get('gig_method') == 'Standard Mileage Rate':
                if 'miles' not in user_data:
                    return {
                        'key': 'miles',
                        'question': self.questions[language]['miles'],
                        'type': 'number'
                    }
            elif user_data.get('gig_method') == 'Actual Expenses':
                # Check for various expense categories
                expense_questions = [
                    ('phone_percent', 'phone_percent'),
                    ('home_office_sqft', 'home_office')
                ]

                for key, question_key in expense_questions:
                    if key not in user_data:
                        return {
                            'key': key,
                            'question': self.questions[language][question_key],
                            'type': 'number' if 'percent' in key else 'text'
                        }

        # State-specific questions (simplified for CA)
        if user_data.get('zip_code', '').startswith(('9', '8')):  # California ZIP codes often start with 9 or 8
            if 'state_specific' not in user_data:
                return {
                    'key': 'state_specific',
                    'question': self.questions[language]['state_specific'],
                    'type': 'yes_no'
                }

        return None  # No more questions

    def validate_answer(self, question_key: str, answer: str) -> tuple[bool, str]:
        """Validate the answer to a question"""
        if question_key == 'zip_code':
            # Simple ZIP validation
            return len(answer.replace('-', '')) >= 5, "Please enter a valid ZIP code"
        elif question_key in ['dependents', 'miles', 'phone_percent', 'home_office_sqft']:
            try:
                val = float(answer)
                if question_key == 'phone_percent' and not (0 <= val <= 100):
                    return False, "Percentage must be between 0 and 100"
                elif val < 0:
                    return False, "Value cannot be negative"
                return True, ""
            except ValueError:
                return False, "Please enter a valid number"
        elif question_key == 'filing_status':
            valid_options = ['single', 'married_filing_jointly', 'married_filing_separately',
                           'head_of_household', 'qualifying_widow']
            return answer.lower().replace(' ', '_') in valid_options, "Please select a valid filing status"

        return True, ""

    def process_answer(self, question_key: str, answer: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store the answer"""
        if question_key == 'dependents':
            user_data[question_key] = int(float(answer))
        elif question_key in ['miles', 'phone_percent', 'home_office_sqft']:
            user_data[question_key] = float(answer)
        elif question_key == 'filing_status':
            # Normalize the answer
            normalized = answer.lower().replace(' ', '_')
            user_data[question_key] = normalized
        else:
            user_data[question_key] = answer

        return user_data
