import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from typing import Dict, Any, List
import json
import os
from datetime import datetime, timedelta

from config import Config
from ocr import OCRProcessor
from classifier import DocumentClassifier
from extractor import DataExtractor
from validator import DataValidator
from qa import AdaptiveQA
from tax_engine import TaxEngine
from benefits import BenefitsEngine
from form_builder import FormBuilder

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    LANGUAGE_SELECTION,
    DOCUMENT_UPLOAD,
    PROCESSING_DOCUMENTS,
    ADAPTIVE_QA,
    TAX_CALCULATION,
    REVIEW_EXPORT,
    CONSENT_RETENTION
) = range(7)

class TaxHelpBot:
    def __init__(self):
        self.config = Config()
        self.ocr_processor = OCRProcessor()
        self.classifier = DocumentClassifier()
        self.extractor = DataExtractor()
        self.validator = DataValidator()
        self.qa = AdaptiveQA()
        self.tax_engine = TaxEngine()
        self.benefits_engine = BenefitsEngine()
        self.form_builder = FormBuilder()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask for language selection."""
        user = update.effective_user

        # Initialize user data
        context.user_data.clear()
        context.user_data['user_id'] = user.id
        context.user_data['documents'] = []
        context.user_data['extracted_data'] = {}
        context.user_data['answers'] = {}

        welcome_text = (
            "Welcome to TaxHelp AI! 🇺🇸\n\n"
            "I'll help you prepare your taxes by:\n"
            "📄 Processing your tax documents\n"
            "🤖 Answering your tax questions\n"
            "💰 Calculating your taxes & benefits\n"
            "📋 Generating tax forms\n\n"
            "Let's start with your preferred language:"
        )

        keyboard = [
            [InlineKeyboardButton("English 🇺🇸", callback_data='lang_en')],
            [InlineKeyboardButton("Español 🇪🇸", callback_data='lang_es')],
            [InlineKeyboardButton("Русский 🇷🇺", callback_data='lang_ru')],
            [InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return LANGUAGE_SELECTION

    async def language_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle language selection."""
        query = update.callback_query
        await query.answer()

        lang_code = query.data.split('_')[1]
        context.user_data['language'] = lang_code

        lang_names = {
            'en': 'English',
            'es': 'Español',
            'ru': 'Русский',
            'ar': 'العربية'
        }

        await query.edit_message_text(
            f"Language set to {lang_names[lang_code]}! 🎉\n\n"
            "Now, please upload your tax documents. You can upload:\n"
            "• W-2 forms\n"
            "• 1099 forms\n"
            "• Receipts\n"
            "• Other tax documents\n\n"
            "📎 Send me your documents (PDF, JPG, PNG - max 10MB each)"
        )

        return DOCUMENT_UPLOAD

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle document upload."""
        document = update.message.document

        if not document:
            await update.message.reply_text("Please send a document file.")
            return DOCUMENT_UPLOAD

        # Check file size
        if document.file_size > self.config.MAX_FILE_SIZE:
            await update.message.reply_text("File too large. Please send files smaller than 10MB.")
            return DOCUMENT_UPLOAD

        # Check file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if document.mime_type not in allowed_types:
            await update.message.reply_text("Please send PDF, JPG, or PNG files only.")
            return DOCUMENT_UPLOAD

        # Download file
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()

        # Store document info
        doc_info = {
            'file_name': document.file_name,
            'mime_type': document.mime_type,
            'file_size': document.file_size,
            'file_bytes': file_bytes,
            'uploaded_at': datetime.now().isoformat()
        }

        context.user_data['documents'].append(doc_info)

        await update.message.reply_text(
            f"✅ Document '{document.file_name}' uploaded successfully!\n\n"
            "Send more documents or type /process when you're done uploading."
        )

        return DOCUMENT_UPLOAD

    async def process_documents(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process uploaded documents."""
        if not context.user_data.get('documents'):
            await update.message.reply_text("Please upload at least one document first.")
            return DOCUMENT_UPLOAD

        await update.message.reply_text("🔄 Processing your documents... This may take a moment.")

        extracted_data = {}
        doc_types = []

        for doc in context.user_data['documents']:
            try:
                # OCR processing
                if doc['mime_type'] == 'application/pdf':
                    text = self.ocr_processor.extract_text_from_pdf(doc['file_bytes'])
                else:
                    text = self.ocr_processor.extract_text(doc['file_bytes'])

                # Document classification
                doc_type = self.classifier.classify_document(text)
                doc_types.append(doc_type)

                # Data extraction
                data = self.extractor.extract_data(text, doc_type)

                # Data validation
                validation_result = self.validator.validate_data(data, doc_type)

                extracted_data[doc_type] = {
                    'data': data,
                    'validation': validation_result,
                    'confidence': 0.8  # Placeholder
                }

            except Exception as e:
                logger.error(f"Error processing document {doc['file_name']}: {e}")
                continue

        context.user_data['extracted_data'] = extracted_data
        context.user_data['doc_types'] = doc_types

        await update.message.reply_text(
            f"✅ Processed {len(extracted_data)} documents successfully!\n\n"
            "Now I'll ask you a few questions to complete your tax information."
        )

        return await self.ask_next_question(update, context)

    async def ask_next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Ask the next adaptive question."""
        language = context.user_data.get('language', 'en')
        doc_types = context.user_data.get('doc_types', [])
        answers = context.user_data.get('answers', {})

        question = self.qa.get_next_question(answers, doc_types, language)

        if question:
            if question['type'] == 'choice':
                keyboard = []
                for option in question['options']:
                    keyboard.append([InlineKeyboardButton(option, callback_data=f"answer_{question['key']}_{option}")])
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_message(chat_id=update.effective_chat.id, text=question['question'], reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=question['question'])

            context.user_data['current_question'] = question
            return ADAPTIVE_QA
        else:
            # No more questions, proceed to tax calculation
            await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ All questions answered! Calculating your taxes...")
            return await self.calculate_taxes(update, context)

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user answers to questions."""
        if update.callback_query:
            query = update.callback_query
            await query.answer()

            data = query.data
            if data.startswith('answer_'):
                _, question_key, answer = data.split('_', 2)
            else:
                return ADAPTIVE_QA
        else:
            answer = update.message.text
            question_key = context.user_data.get('current_question', {}).get('key')

        if not question_key:
            await update.message.reply_text("Please answer the current question.")
            return ADAPTIVE_QA

        # Validate answer
        is_valid, error_msg = self.qa.validate_answer(question_key, answer)
        if not is_valid:
            await update.message.reply_text(f"Invalid answer: {error_msg}")
            return ADAPTIVE_QA

        # Process and store answer
        answers = context.user_data.get('answers', {})
        answers = self.qa.process_answer(question_key, answer, answers)
        context.user_data['answers'] = answers

        return await self.ask_next_question(update, context)

    async def calculate_taxes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Calculate taxes and benefits."""
        extracted_data = context.user_data.get('extracted_data', {})
        answers = context.user_data.get('answers', {})

        # Combine extracted data with user answers
        tax_input = {
            'extracted_data': extracted_data,
            'user_answers': answers
        }

        # Calculate federal taxes
        federal_tax = self.tax_engine.calculate_federal_tax(tax_input)

        # Calculate state taxes (simplified for CA)
        state_tax = self.tax_engine.calculate_state_tax(tax_input, 'CA')

        # Calculate self-employment tax if applicable
        se_tax = {}
        if any('1099' in dt.lower() for dt in context.user_data.get('doc_types', [])):
            se_tax = self.tax_engine.calculate_self_employment_tax(tax_input)

        # Screen for benefits
        benefits = self.benefits_engine.screen_benefits(answers, {'federal': federal_tax, 'state': state_tax})

        # Store results
        context.user_data['tax_results'] = {
            'federal': federal_tax,
            'state': state_tax,
            'self_employment': se_tax,
            'benefits': benefits
        }

        # Generate summary
        summary = self._generate_tax_summary(federal_tax, state_tax, se_tax, benefits)

        await update.message.reply_text(
            "💰 Tax Calculation Complete!\n\n" + summary + "\n\n"
            "Would you like to:\n"
            "📄 View detailed forms\n"
            "📊 Export data\n"
            "🔄 Review and edit information"
        )

        keyboard = [
            [InlineKeyboardButton("📄 View Forms", callback_data='view_forms')],
            [InlineKeyboardButton("📊 Export Data", callback_data='export_data')],
            [InlineKeyboardButton("🔄 Review Info", callback_data='review_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
        return REVIEW_EXPORT

    def _generate_tax_summary(self, federal: Dict, state: Dict, se: Dict, benefits: List) -> str:
        """Generate a human-readable tax summary."""
        summary = []

        if federal.get('refund', 0) > 0:
            summary.append(f"🎉 Estimated Federal Refund: ${federal['refund']:,.2f}")
        elif federal.get('amount_due', 0) > 0:
            summary.append(f"💸 Federal Amount Due: ${federal['amount_due']:,.2f}")

        if state.get('refund', 0) > 0:
            summary.append(f"🏛️ Estimated State Refund: ${state['refund']:,.2f}")
        elif state.get('amount_due', 0) > 0:
            summary.append(f"🏛️ State Amount Due: ${state['amount_due']:,.2f}")

        if se.get('total_tax', 0) > 0:
            summary.append(f"🏢 Self-Employment Tax: ${se['total_tax']:,.2f}")

        if benefits:
            summary.append(f"🎁 Found {len(benefits)} potential benefits programs")

        return "\n".join(summary)

    async def handle_review_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle review/export choices."""
        query = update.callback_query
        await query.answer()

        choice = query.data

        if choice == 'view_forms':
            await self.send_forms(update, context)
        elif choice == 'export_data':
            await self.export_data(update, context)
        elif choice == 'review_info':
            await self.review_info(update, context)

        return REVIEW_EXPORT

    async def send_forms(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send generated tax forms."""
        tax_results = context.user_data.get('tax_results', {})
        answers = context.user_data.get('answers', {})

        # Generate 1040 summary
        pdf_1040 = self.form_builder.generate_1040_summary(tax_results, answers)

        # Send PDF
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_1040,
            filename='tax_return_summary.pdf',
            caption='📄 Your Tax Return Summary'
        )

        # Generate benefits summary if applicable
        benefits = tax_results.get('benefits', [])
        if benefits:
            pdf_benefits = self.form_builder.generate_benefits_summary(benefits)
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_benefits,
                filename='benefits_summary.pdf',
                caption='🎁 Potential Benefits Summary'
            )

    async def export_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export tax data as JSON."""
        export_data = {
            'user_info': context.user_data.get('answers', {}),
            'documents_processed': len(context.user_data.get('documents', [])),
            'tax_results': context.user_data.get('tax_results', {}),
            'exported_at': datetime.now().isoformat()
        }

        json_data = json.dumps(export_data, indent=2, default=str)

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=json_data.encode('utf-8'),
            filename='tax_data_export.json',
            caption='📊 Your Tax Data Export'
        )

    async def review_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show review of entered information."""
        answers = context.user_data.get('answers', {})

        review_text = "📋 Review Your Information:\n\n"

        for key, value in answers.items():
            display_key = key.replace('_', ' ').title()
            review_text += f"• {display_key}: {value}\n"

        review_text += "\nIf anything looks incorrect, you can start over with /start"

        chat_id = update.effective_chat.id if update.effective_chat else update.callback_query.message.chat.id
        await context.bot.send_message(chat_id=chat_id, text=review_text)

    async def consent_and_retention(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle consent and data retention."""
        consent_text = (
            "🔒 Data Privacy & Consent\n\n"
            "Your data is encrypted and stored securely. We retain your information for "
            f"{self.config.DATA_RETENTION_DAYS} days for tax purposes.\n\n"
            "Do you consent to data processing and storage?"
        )

        keyboard = [
            [InlineKeyboardButton("✅ I Consent", callback_data='consent_yes')],
            [InlineKeyboardButton("❌ No Consent", callback_data='consent_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(consent_text, reply_markup=reply_markup)
        return CONSENT_RETENTION

    async def handle_consent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle consent response."""
        query = update.callback_query
        await query.answer()

        if query.data == 'consent_yes':
            await query.edit_message_text(
                "✅ Consent granted. Your data will be securely stored.\n\n"
                "Thank you for using TaxHelp AI! 🇺🇸\n\n"
                "You can start a new session anytime with /start"
            )
        else:
            await query.edit_message_text(
                "❌ Consent not granted. Your data will be deleted immediately.\n\n"
                "Thank you for considering TaxHelp AI!"
            )
            # Clear user data
            context.user_data.clear()

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        await update.message.reply_text("Operation cancelled. Type /start to begin again.")
        return ConversationHandler.END

def main():
    """Run the bot."""
    # Create application
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Create bot instance
    bot = TaxHelpBot()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", bot.start)],
        states={
            LANGUAGE_SELECTION: [CallbackQueryHandler(bot.language_selected, pattern=r'^lang_')],
            DOCUMENT_UPLOAD: [
                MessageHandler(filters.Document.ALL, bot.handle_document),
                CommandHandler("process", bot.process_documents)
            ],
            PROCESSING_DOCUMENTS: [],
            ADAPTIVE_QA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_answer),
                CallbackQueryHandler(bot.handle_answer, pattern=r'^answer_')
            ],
            TAX_CALCULATION: [],
            REVIEW_EXPORT: [CallbackQueryHandler(bot.handle_review_choice)],
            CONSENT_RETENTION: [CallbackQueryHandler(bot.handle_consent, pattern=r'^consent_')]
        },
        fallbacks=[CommandHandler("cancel", bot.cancel), CommandHandler("start", bot.start)]
    )

    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
