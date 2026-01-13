from typing import Dict, List
import re

class DocumentClassifier:
    def __init__(self):
        # Keywords for different document types
        self.keywords = {
            'w2': [
                'w-2', 'wage and tax statement', 'wages, tips, other compensation',
                'federal income tax withheld', 'social security wages', 'medicare wages',
                'box 1', 'box 2', 'box 3', 'box 4', 'box 5', 'box 6'
            ],
            '1099-misc': [
                '1099-misc', 'miscellaneous income', 'rents', 'royalties',
                'other income', 'box 1', 'box 2', 'box 3', 'box 4'
            ],
            '1099-k': [
                '1099-k', 'payment card', 'third party network', 'merchant category code',
                'number of payment transactions', 'federal income tax withheld'
            ],
            '1099-nec': [
                '1099-nec', 'nonemployee compensation', 'services you performed',
                'box 1', 'box 4', 'box 5'
            ],
            '1098': [
                '1098', 'mortgage interest statement', 'mortgage interest received',
                'points paid', 'outstanding mortgage principal'
            ],
            'receipt': [
                'receipt', 'invoice', 'paid', 'amount due', 'total', 'tax',
                'subtotal', 'payment received', 'thank you for your business'
            ]
        }

    def classify_document(self, text: str) -> str:
        """Classify document type based on text content"""
        text_lower = text.lower()

        # Count keyword matches for each document type
        scores = {}
        for doc_type, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            scores[doc_type] = score

        # Find the document type with the highest score
        best_match = max(scores, key=scores.get)

        # If no keywords match, classify as 'other'
        if scores[best_match] == 0:
            return 'other'

        return best_match

    def get_confidence_score(self, text: str, doc_type: str) -> float:
        """Calculate confidence score for a document classification"""
        if doc_type not in self.keywords:
            return 0.0

        text_lower = text.lower()
        keywords = self.keywords[doc_type]

        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        total_keywords = len(keywords)

        return matches / total_keywords if total_keywords > 0 else 0.0
