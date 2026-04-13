"""
Legal Document Simplifier Backend
Flask application for analyzing and simplifying complex legal documents
Uses LEGAL-BERT for clause extraction + Claude API for plain English explanations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import json
import re
from io import BytesIO
import logging

# Setup logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLP and LLM imports
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False
    logger.warning("Torch/Transformers not available. Using fallback clause extraction.")

import pdfplumber
import anthropic

# Database imports
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///legal_documents.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class DocumentAnalysis(Base):
    """Store document analysis results"""
    __tablename__ = 'document_analysis'
    
    id = Column(Integer, primary_key=True, index=True)
    document_hash = Column(String(64), unique=True, index=True)
    original_text = Column(Text)
    score = Column(Float)
    score_label = Column(String(50))
    score_desc = Column(Text)
    summary = Column(Text)
    clauses = Column(JSON)
    negotiation_tips = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# Initialize LEGAL-BERT model for clause extraction
def load_legal_bert_model():
    """Load LEGAL-BERT model for legal clause extraction"""
    if not HAS_TRANSFORMER:
        logger.warning("Transformers library not available. Using fallback pattern matching for clause extraction.")
        return None
    
    try:
        model_name = "nlpaueb/legal-bert-base-uncased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
        logger.info("LEGAL-BERT model loaded successfully")
        return ner_pipeline
    except Exception as e:
        logger.warning(f"Could not load LEGAL-BERT model: {e}. Using fallback clause extraction.")
        return None


legal_bert_pipeline = load_legal_bert_model()


# Legal clause patterns for fallback extraction
CLAUSE_PATTERNS = {
    'TERMINATION': r'(?i)(termination|end\s+of|cease|discontinue|cancel)',
    'LIABILITY': r'(?i)(liability|liable|damage|indemnif|warrant)',
    'PAYMENT': r'(?i)(payment|pay|fee|price|cost|rent|compensation)',
    'NON-COMPETE': r'(?i)(non[- ]?compet|compete|competitor|exclusiv)',
    'CONFIDENTIALITY': r'(?i)(confidential|secret|proprietary|disclosure)',
    'ARBITRATION': r'(?i)(arbitrat|dispute|mediat|resolution)',
    'AUTO-RENEWAL': r'(?i)(auto[- ]?renewal|automatic|renew|extend)',
    'INTELLECTUAL PROPERTY': r'(?i)(intellectual\s+property|patent|copyright|ownership|rights)',
    'DATA/PRIVACY': r'(?i)(data|privacy|personal|information|gdpr|ccpa)',
    'FORCE MAJEURE': r'(?i)(force\s+majeure|unforeseeable|act\s+of\s+god)',
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Legal Document Simplifier'
    }), 200


@app.route('/api/simplify', methods=['POST'])
def simplify_document():
    """
    Main endpoint to analyze and simplify legal documents
    
    Expected JSON payload:
    {
        "text": "Legal document text to analyze"
    }
    
    Returns JSON with:
    {
        "score": 0-100,
        "score_label": "Risk assessment",
        "score_desc": "Description",
        "clauses": [...],
        "summary": "...",
        "negotiation_tips": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field in request'}), 400
        
        legal_text = data['text'].strip()
        
        if not legal_text or len(legal_text) < 50:
            return jsonify({'error': 'Text too short. Please provide at least 50 characters.'}), 400
        
        logger.info(f"Processing document of length: {len(legal_text)}")
        
        # Extract clauses from document
        clauses = extract_clauses(legal_text)
        logger.info(f"Extracted {len(clauses)} clauses")
        
        # Generate plain English explanations and risk scores using Claude
        enriched_clauses = enrich_clauses_with_ai(clauses, legal_text)
        
        # Calculate overall favorability score
        favorable_score = calculate_favorability_score(enriched_clauses)
        
        # Generate overall summary and negotiation tips
        summary, negotiation_tips = generate_summary_and_tips(legal_text, enriched_clauses)
        
        # Prepare response
        response = {
            'score': favorable_score,
            'score_label': get_score_label(favorable_score),
            'score_desc': get_score_description(favorable_score),
            'clauses': enriched_clauses,
            'summary': summary,
            'negotiation_tips': negotiation_tips,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to database
        try:
            save_analysis(legal_text, response)
        except Exception as db_error:
            logger.warning(f"Could not save to database: {db_error}")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Handle PDF file uploads
    Extracts text from PDF and processes it
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Extract text from PDF
        pdf_text = extract_pdf_text(file.stream)
        
        if not pdf_text or len(pdf_text) < 50:
            return jsonify({'error': 'Could not extract sufficient text from PDF'}), 400
        
        logger.info(f"Extracted {len(pdf_text)} characters from PDF")
        
        # Process the extracted text
        return simplify_document_from_text(pdf_text)
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500


def extract_pdf_text(pdf_file):
    """Extract text from PDF file using pdfplumber"""
    try:
        text_content = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return '\n'.join(text_content)
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


def simplify_document_from_text(text):
    """Process document text and return analysis"""
    try:
        clauses = extract_clauses(text)
        enriched_clauses = enrich_clauses_with_ai(clauses, text)
        favorable_score = calculate_favorability_score(enriched_clauses)
        summary, negotiation_tips = generate_summary_and_tips(text, enriched_clauses)
        
        response = {
            'score': favorable_score,
            'score_label': get_score_label(favorable_score),
            'score_desc': get_score_description(favorable_score),
            'clauses': enriched_clauses,
            'summary': summary,
            'negotiation_tips': negotiation_tips,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            save_analysis(text, response)
        except Exception as db_error:
            logger.warning(f"Could not save to database: {db_error}")
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return jsonify({'error': str(e)}), 500


def extract_clauses(text):
    """
    Extract legal clauses from document text
    Uses LEGAL-BERT if available, falls back to pattern matching
    """
    clauses = []
    
    # Use LEGAL-BERT if available
    if legal_bert_pipeline:
        try:
            # Process in chunks to manage token limits
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            for chunk in chunks:
                entities = legal_bert_pipeline(chunk[:512])  # Process first 512 chars per chunk
                for entity in entities:
                    if entity['score'] > 0.5:
                        clauses.append({
                            'type': entity['entity_group'],
                            'text': entity['word'],
                            'confidence': entity['score']
                        })
        except Exception as e:
            logger.warning(f"LEGAL-BERT extraction failed: {e}. Using fallback.")
            clauses = extract_clauses_fallback(text)
    else:
        clauses = extract_clauses_fallback(text)
    
    return clauses if clauses else extract_clauses_fallback(text)


def extract_clauses_fallback(text):
    """
    Fallback clause extraction using pattern matching
    when LEGAL-BERT is not available
    """
    clauses = []
    sentences = re.split(r'[.!?]\s+', text)
    
    for pattern_name, pattern in CLAUSE_PATTERNS.items():
        for sentence in sentences:
            if re.search(pattern, sentence):
                # Extract the sentence that contains the clause
                clause_text = sentence[:200].strip() if len(sentence) > 200 else sentence.strip()
                if clause_text:
                    clauses.append({
                        'type': pattern_name,
                        'text': clause_text,
                        'confidence': 0.7  # Default confidence for pattern matches
                    })
                break  # Only one match per clause type
    
    return clauses


def enrich_clauses_with_ai(clauses, full_text):
    """
    Use Claude API to generate plain English explanations
    and risk assessments for each clause
    """
    enriched_clauses = []
    
    # Group clauses by type to avoid duplicates
    clause_types = {}
    for clause in clauses:
        clause_type = clause.get('type', 'UNKNOWN')
        if clause_type not in clause_types:
            clause_types[clause_type] = clause
    
    for clause_type, clause in clause_types.items():
        try:
            # Generate explanation and risk score using Claude
            prompt = f"""You are a legal expert. Analyze this legal clause and provide:
1. A plain English explanation (1-2 sentences)
2. Risk level (high/medium/low)
3. A negotiation tip if applicable

Clause type: {clause_type}
Clause text: {clause['text']}

Full document context (first 1000 chars):
{full_text[:1000]}

Respond in this exact JSON format:
{{
  "title": "{clause_type}",
  "plain": "Plain English explanation here",
  "risk": "high|medium|low",
  "tip": "Negotiation tip or suggestion",
  "original": "{clause['text'][:100]}"
}}"""

            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            response_text = response.content[0].text
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                clause_data = json.loads(json_match.group())
                enriched_clauses.append(clause_data)
            else:
                # Create default enriched clause if parsing fails
                enriched_clauses.append({
                    'title': clause_type,
                    'risk': 'medium',
                    'original': clause['text'][:100],
                    'plain': response_text[:200],
                    'tip': 'Review this clause carefully with a legal professional.'
                })
        
        except Exception as e:
            logger.warning(f"Error enriching clause {clause_type}: {e}")
            # Add basic enrichment as fallback
            enriched_clauses.append({
                'title': clause_type,
                'risk': 'medium',
                'original': clause['text'][:100],
                'plain': f'This clause relates to {clause_type.lower()}. Ensure you understand all implications.',
                'tip': 'Consider consulting a lawyer about this clause.'
            })
    
    return enriched_clauses


def calculate_favorability_score(clauses):
    """
    Calculate overall document favorability score (0-100)
    100 = fully favorable to signer
    0 = very unfavorable to signer
    """
    if not clauses:
        return 50
    
    risk_scores = {'high': 20, 'medium': 50, 'low': 80}
    
    total_score = 0
    for clause in clauses:
        risk = clause.get('risk', 'medium').lower()
        total_score += risk_scores.get(risk, 50)
    
    avg_score = total_score / len(clauses)
    return max(0, min(100, int(avg_score)))


def get_score_label(score):
    """Get descriptive label for favorability score"""
    if score >= 70:
        return "Highly favorable"
    elif score >= 55:
        return "Moderately favorable"
    elif score >= 45:
        return "Neutral"
    elif score >= 25:
        return "Somewhat risky"
    else:
        return "Very risky"


def get_score_description(score):
    """Get detailed description for favorability score"""
    descriptions = {
        'high': 'This document appears fair and balanced. Standard terms apply.',
        'medium': 'Some clauses favor the other party. Consider negotiating.',
        'neutral': 'Mixed terms with both favorable and unfavorable clauses.',
        'low': 'Several risky clauses detected. Seek legal advice before signing.',
        'very_low': 'Multiple high-risk items. Do not sign without legal review.'
    }
    
    if score >= 70:
        return descriptions['high']
    elif score >= 55:
        return descriptions['medium']
    elif score >= 45:
        return descriptions['neutral']
    elif score >= 25:
        return descriptions['low']
    else:
        return descriptions['very_low']


def generate_summary_and_tips(text, clauses):
    """
    Generate overall summary and negotiation tips using Claude
    """
    try:
        high_risk_count = sum(1 for c in clauses if c.get('risk') == 'high')
        medium_risk_count = sum(1 for c in clauses if c.get('risk') == 'medium')
        
        prompt = f"""You are a legal expert. Based on the following document analysis, provide:
1. A 2-3 sentence overall summary
2. 3 specific negotiation tips

Document excerpt: {text[:500]}

Risk analysis summary:
- High risk clauses: {high_risk_count}
- Medium risk clauses: {medium_risk_count}
- Total clauses analyzed: {len(clauses)}

Respond in this exact JSON format:
{{
  "summary": "2-3 sentence summary here",
  "tips": ["tip 1", "tip 2", "tip 3"]
}}"""

        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response_text = response.content[0].text
        
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get('summary', ''), data.get('tips', [])
        else:
            return response_text[:300], ['Review all clauses carefully', 'Seek legal advice for complex terms', 'Negotiate unfavorable conditions']
    
    except Exception as e:
        logger.warning(f"Error generating summary: {e}")
        return "Document analysis complete. Review each clause carefully.", ["Consult a lawyer", "Identify key concerns", "Prepare negotiation points"]


def save_analysis(text, analysis):
    """Save document analysis to database"""
    try:
        import hashlib
        doc_hash = hashlib.sha256(text.encode()).hexdigest()
        
        db = SessionLocal()
        
        # Check if already exists
        existing = db.query(DocumentAnalysis).filter_by(document_hash=doc_hash).first()
        if existing:
            db.close()
            return
        
        analysis_record = DocumentAnalysis(
            document_hash=doc_hash,
            original_text=text[:5000],  # Store first 5000 chars
            score=analysis.get('score'),
            score_label=analysis.get('score_label'),
            score_desc=analysis.get('score_desc'),
            summary=analysis.get('summary'),
            clauses=analysis.get('clauses'),
            negotiation_tips=analysis.get('negotiation_tips')
        )
        
        db.add(analysis_record)
        db.commit()
        db.close()
        logger.info("Analysis saved to database")
    
    except Exception as e:
        logger.warning(f"Database save error: {e}")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
