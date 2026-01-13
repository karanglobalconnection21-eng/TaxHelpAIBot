# TaxHelp AI Telegram Bot

A comprehensive Telegram bot for tax assistance that processes documents, answers questions, calculates taxes, and generates forms.

## Features

- **Multi-language Support**: English, Spanish, Russian, Arabic
- **Document Processing**: OCR for W-2, 1099, receipts, and other tax documents
- **Adaptive Q&A**: Intelligent questioning based on uploaded documents
- **Tax Calculation**: Federal and state tax computation with benefits screening
- **Form Generation**: PDF generation of tax forms and summaries
- **Secure Storage**: Encrypted document storage with retention policies
- **Benefits Screening**: Automatic screening for EITC, CTC, SNAP, Medi-Cal, etc.

## Architecture

```
taxhelp-bot/
├── bot.py              # Main Telegram bot application
├── config.py           # Configuration and constants
├── ocr.py              # OCR processing for documents
├── classifier.py       # Document type classification
├── extractor.py        # Data extraction from OCR text
├── validator.py        # Data validation and cross-checking
├── qa.py               # Adaptive question-answering system
├── tax_engine.py       # Tax calculation engine
├── benefits.py         # Benefits screening engine
├── form_builder.py     # PDF form generation
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Tesseract OCR installed
- AWS account (for S3 storage, optional)

### 2. Installation

1. Clone or download the project:
   ```bash
   cd taxhelp-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location or update TESSERACT_PATH in .env

### 3. Configuration

1. Create a Telegram bot:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Copy the bot token

2. Edit `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ENCRYPTION_KEY=generate_a_random_32_character_key
   ```

3. (Optional) Configure AWS S3 for document storage:
   ```env
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   S3_BUCKET=your_bucket_name
   ```

### 4. Running the Bot

```bash
python bot.py
```

## Usage

1. **Start**: Send `/start` to the bot
2. **Language Selection**: Choose your preferred language
3. **Document Upload**: Send tax documents (PDF/JPG/PNG)
4. **Processing**: Type `/process` when done uploading
5. **Q&A**: Answer adaptive questions about your tax situation
6. **Review**: View tax calculations, forms, and export data
7. **Consent**: Grant consent for data processing

## User Journey

```
Start → Language Selection → Document Upload → OCR Processing →
Data Extraction → Adaptive Q&A → Tax Calculation → Benefits Screening →
Form Generation → Review & Export → Consent & Retention
```

## Security Features

- **Encryption**: Documents encrypted at rest and in transit
- **Access Control**: User-specific data isolation
- **Retention Policy**: Automatic data deletion after retention period
- **Consent Management**: Explicit user consent required
- **Audit Trail**: Logging of all operations

## Supported Document Types

- W-2 (Wage and Tax Statement)
- 1099-MISC (Miscellaneous Income)
- 1099-K (Payment Card and Third Party Network)
- 1099-NEC (Nonemployee Compensation)
- 1098 (Mortgage Interest)
- Receipts and expense documentation

## Tax Calculations

- **Federal Taxes**: Progressive brackets, standard deductions, credits
- **State Taxes**: California (CA-540), extensible to other states
- **Self-Employment Tax**: SE tax calculations for gig workers
- **Credits**: EITC, CTC, education credits
- **Benefits**: Automatic screening for assistance programs

## API Endpoints (Future)

The bot is designed to be extensible with REST API endpoints for:
- Document upload and processing
- Tax calculation requests
- Form generation
- Benefits screening

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational and informational purposes only. It does not constitute legal or tax advice. Users should consult with qualified tax professionals for their specific tax situations.

## Support

For support or questions:
- Create an issue on GitHub
- Contact the development team

---

**TaxHelp AI** - Making taxes simple with AI assistance! 🇺🇸

