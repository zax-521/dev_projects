#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Test Question Generator
Supports PDF, Word document processing, generates four types of test questions
"""

import os
import re
import json
import argparse
import random
import logging
import chardet
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Document processing libraries
try:
    from PyPDF2 import PdfReader
    import docx
    from docx import Document
except ImportError:
    print("Please install required libraries: pip install PyPDF2 python-docx")

# Natural language processing library
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk import pos_tag
    # Download necessary NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
except ImportError:
    print("To use NLTK features, please install: pip install nltk")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API Client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat_completion(self, messages: List[Dict], model: str = "deepseek-chat", 
                       temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Call DeepSeek chat completion API"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"DeepSeek API response format error: {e}")
            raise

class DocumentProcessor:
    """Document Processor"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']
    
    def extract_text(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from file and return metadata"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        file_size = os.path.getsize(file_path)
        max_file_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_file_size:
            raise ValueError(f"File too large: {file_size} bytes, maximum supported {max_file_size} bytes")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            text = self._extract_from_word(file_path)
        elif ext == '.txt':
            text = self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Clean text
        text = self._clean_text(text)
        
        # Generate metadata
        metadata = {
            'file_path': file_path,
            'file_size': file_size,
            'file_extension': ext,
            'text_length': len(text),
            'extraction_time': datetime.now().isoformat(),
            'sentences_count': len(self._split_into_sentences(text)),
            'words_count': len(self._split_into_words(text))
        }
        
        return text, metadata
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"Page {page_num + 1}:\n{page_text}\n\n"
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
        return text
    
    def _extract_from_word(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Word document extraction failed: {e}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from text file"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Text file extraction failed: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            sentences = sent_tokenize(text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
        except:
            sentences = re.split(r'[.!?\n]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _split_into_words(self, text: str) -> List[str]:
        """Split text into words"""
        try:
            words = word_tokenize(text)
            return [w for w in words if w.isalnum()]
        except:
            return re.findall(r'\b\w+\b', text)

class TestGenerator:
    """Test Question Generator"""
    
    def __init__(self, use_deepseek=False, api_key=None):
        self.use_deepseek = use_deepseek
        self.deepseek_client = None
        
        if use_deepseek and api_key:
            self.deepseek_client = DeepSeekClient(api_key)
        
        # English stopwords
        self.english_stopwords = set(stopwords.words('english'))
        
        logger.info(f"Test generator initialized - DeepSeek: {use_deepseek}")
    
    def generate_questions(self, text: str, question_types: List[str], num_questions: int = 5) -> Dict[str, Any]:
        """Generate test questions"""
        if len(text) < 50:
            raise ValueError("Text content is too short to generate effective test questions")
        
        # Limit text length
        processed_text = text[:2000]
        
        questions = {}
        metadata = {
            'generation_time': datetime.now().isoformat(),
            'text_length': len(processed_text),
            'question_types': question_types,
            'total_questions': 0
        }
        
        for q_type in question_types:
            if q_type not in ['choice', 'sorting', 'matching', 'essay']:
                logger.warning(f"Skipping unsupported question type: {q_type}")
                continue
            
            type_questions = []
            successful_count = 0
            
            for i in range(num_questions):
                try:
                    if self.use_deepseek:
                        question = self._generate_with_deepseek(processed_text, q_type)
                    else:
                        question = self._generate_local(processed_text, q_type)
                    
                    if question:
                        question['id'] = f"{q_type}_{i+1}"
                        question['points'] = self._get_default_points(q_type)
                        type_questions.append(question)
                        successful_count += 1
                        logger.info(f"Successfully generated {q_type} question {i+1}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate {q_type} question {i+1}: {e}")
                    continue
            
            questions[q_type] = type_questions
            metadata['total_questions'] += len(type_questions)
        
        return {
            'questions': questions,
            'metadata': metadata
        }
    
    def _generate_local(self, text: str, q_type: str) -> Dict[str, Any]:
        """Generate questions locally"""
        strategies = {
            'choice': self._generate_choice,
            'sorting': self._generate_sorting,
            'matching': self._generate_matching,
            'essay': self._generate_essay
        }
        return strategies[q_type](text)
    
    def _generate_choice(self, text: str) -> Dict[str, Any]:
        """Generate multiple choice questions"""
        sentences = self._split_into_sentences(text)
        if len(sentences) < 3:
            return None
        
        base_sentence = random.choice(sentences)
        
        question_templates = [
            f"Which of the following best describes the meaning of: \"{base_sentence}\"?",
            f"Based on the content: \"{base_sentence}\", which statement is correct?",
            f"What is the main point expressed in: \"{base_sentence}\"?"
        ]
        
        question = random.choice(question_templates)
        
        options = [
            "Accurately reflects the original meaning",
            "Overinterprets the original text",
            "Ignores important details", 
            "Contains misunderstanding"
        ]
        random.shuffle(options)
        
        return {
            'type': 'choice',
            'question': question,
            'options': options,
            'answer': 'A',
            'explanation': 'Please analyze based on the original text content',
            'difficulty': random.choice(['Easy', 'Medium', 'Hard'])
        }
    
    def _generate_sorting(self, text: str) -> Dict[str, Any]:
        """Generate sorting questions"""
        sentences = self._split_into_sentences(text)
        if len(sentences) < 4:
            return None
        
        selected_sentences = random.sample(sentences, min(4, len(sentences)))
        random.shuffle(selected_sentences)
        
        return {
            'type': 'sorting',
            'question': 'Please arrange the following sentences in logical order:',
            'items': selected_sentences,
            'correct_order': list(range(len(selected_sentences))),
            'explanation': 'The correct order should follow logical coherence'
        }
    
    def _generate_matching(self, text: str) -> Dict[str, Any]:
        """Generate matching questions"""
        keywords = self._extract_keywords(text)
        concepts = list(set(keywords))[:4]
        
        if len(concepts) < 2:
            return None
        
        left_items = concepts[:3]
        right_items = [f"Description of {concept}" for concept in left_items]
        random.shuffle(right_items)
        
        return {
            'type': 'matching',
            'question': 'Please match the concepts on the left with their correct descriptions on the right:',
            'left_items': left_items,
            'right_items': right_items,
            'correct_pairs': list(zip(left_items, right_items)),
            'explanation': 'Correct matching should be based on the essential characteristics of the concepts'
        }
    
    def _generate_essay(self, text: str) -> Dict[str, Any]:
        """Generate essay questions"""
        essay_prompts = [
            "Please summarize the core viewpoints and main arguments of this text",
            "Analyze the argument structure and logical relationships in this text",
            "What insights does this text provide you? Please discuss your understanding in combination with actual situations",
            "Evaluate the strengths and weaknesses of this text and provide improvement suggestions"
        ]
        
        return {
            'type': 'essay',
            'question': random.choice(essay_prompts),
            'points': 15,
            'suggested_length': '300-500 words',
            'evaluation_criteria': ['Content completeness', 'Logical clarity', 'Depth of viewpoint', 'Language expression']
        }
    
    def _generate_with_deepseek(self, text: str, q_type: str) -> Dict[str, Any]:
        """Generate questions using DeepSeek API"""
        prompts = {
            'choice': f"""Generate a high-quality multiple choice question based on the following text:
Text: {text[:1000]}
Requirements:
1. The question should be based on the text content
2. Provide 4 distinctive options
3. Mark the correct answer
4. Provide explanation
Please return in JSON format: {{"question": "question", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "explanation"}}""",
            
            'sorting': f"""Generate a sorting question based on the following text:
Text: {text[:1000]}
Requirements:
1. Select 3-5 logically related sentences
2. Shuffle their order
3. Provide correct order
Please return in JSON format: {{"question": "question", "items": ["sentence1", "sentence2", ...], "correct_order": [0,1,2,...]}}""",
            
            'matching': f"""Generate a matching question based on the following text:
Text: {text[:1000]}
Requirements:
1. List 3-4 key concepts on the left
2. List corresponding descriptions on the right
3. Concepts and descriptions should be related but shuffled
Please return in JSON format: {{"question": "question", "left_items": ["concept1", ...], "right_items": ["description1", ...], "correct_pairs": [["concept1","description1"], ...]}}""",
            
            'essay': f"""Generate an essay question based on the following text:
Text: {text[:1000]}
Requirements:
1. The question should be deep and inspiring
2. Suitable for 300-500 word answers
3. Provide evaluation criteria
Please return in JSON format: {{"question": "question", "suggested_length": "300-500 words", "evaluation_criteria": ["criterion1", "criterion2"]}}"""
        }
        
        try:
            messages = [
                {"role": "system", "content": "You are a professional education expert skilled in generating various types of test questions based on text content."},
                {"role": "user", "content": prompts[q_type]}
            ]
            
            content = self.deepseek_client.chat_completion(
                messages=messages,
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=1000
            )
            
            return self._parse_ai_response(content, q_type)
            
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            return self._generate_local(text, q_type)
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords"""
        try:
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            pos_filter = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']
            
            filtered_words = []
            for word, pos in pos_tags:
                if (any(pos.startswith(tag) for tag in pos_filter) and 
                    word.lower() not in self.english_stopwords and
                    len(word) > 1):
                    filtered_words.append(word)
            
            from collections import Counter
            word_freq = Counter(filtered_words)
            return [word for word, _ in word_freq.most_common(top_n)]
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            words = re.findall(r'\b\w+\b', text)
            filtered_words = [w for w in words if len(w) > 1 and w.lower() not in self.english_stopwords]
            from collections import Counter
            word_freq = Counter(filtered_words)
            return [word for word, _ in word_freq.most_common(top_n)]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            sentences = sent_tokenize(text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
        except:
            sentences = re.split(r'[.!?\n]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _get_default_points(self, q_type: str) -> int:
        """Get default points"""
        points_map = {
            'choice': 2,
            'sorting': 3,
            'matching': 4,
            'essay': 15
        }
        return points_map.get(q_type, 1)
    
    def _parse_ai_response(self, response: str, q_type: str) -> Dict[str, Any]:
        """Parse AI response"""
        try:
            # Clean response content, remove possible code block markers
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            # Try to parse JSON response
            data = json.loads(cleaned_response)
            
            # Ensure basic fields exist
            if 'question' not in data:
                data['question'] = f"Please answer related questions based on the text content"
            
            data['type'] = q_type
            return data
            
        except json.JSONDecodeError:
            logger.warning("AI response is not valid JSON format, using default structure")
            return {
                'type': q_type,
                'question': response[:150] + "..." if len(response) > 150 else response,
                'explanation': 'Please refer to the original text content for analysis'
            }

class TestExporter:
    """Test Question Exporter"""
    
    @staticmethod
    def export_to_json(result: Dict, output_file: str):
        """Export to JSON file"""
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON file exported: {output_file}")
    
    @staticmethod
    def export_to_txt(result: Dict, output_file: str):
        """Export to text file"""
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write metadata
            metadata = result.get('metadata', {})
            f.write("Test Question Generation Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generation Time: {metadata.get('generation_time', 'N/A')}\n")
            f.write(f"Text Length: {metadata.get('text_length', 0)} characters\n")
            f.write(f"Question Types: {', '.join(metadata.get('question_types', []))}\n")
            f.write(f"Total Questions: {metadata.get('total_questions', 0)}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write questions
            questions = result.get('questions', {})
            for q_type, q_list in questions.items():
                f.write(f"\n{'='*50}\n")
                f.write(f"{q_type.upper()} QUESTIONS\n")
                f.write(f"{'='*50}\n")
                
                for i, question in enumerate(q_list, 1):
                    f.write(f"\n{i}. {question['question']}\n")
                    
                    if q_type == 'choice':
                        for j, option in enumerate(question['options']):
                            f.write(f"   {chr(65+j)}. {option}\n")
                        f.write(f"   Answer: {question.get('answer', 'N/A')}\n")
                        f.write(f"   Explanation: {question.get('explanation', 'Please refer to original text')}\n")
                    
                    elif q_type == 'sorting':
                        for j, item in enumerate(question['items']):
                            f.write(f"   {j+1}. {item}\n")
                        f.write(f"   Explanation: {question.get('explanation', 'Please refer to original text')}\n")
                    
                    elif q_type == 'matching':
                        f.write("   Left Items: " + ", ".join(question['left_items']) + "\n")
                        f.write("   Right Items: " + ", ".join(question['right_items']) + "\n")
                        f.write(f"   Explanation: {question.get('explanation', 'Please refer to original text')}\n")
                    
                    elif q_type == 'essay':
                        f.write(f"   Suggested Length: {question.get('suggested_length', 'N/A')}\n")
                        f.write(f"   Points: {question.get('points', 'N/A')}\n")
                        f.write(f"   Evaluation Criteria: {', '.join(question.get('evaluation_criteria', []))}\n")
                    
                    f.write(f"   Difficulty: {question.get('difficulty', 'Medium')}\n")
        
        logger.info(f"Text file exported: {output_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate test questions from documents (supports DeepSeek)')
    parser.add_argument('input_file', help='Input file path (PDF/DOC/DOCX/TXT)')
    parser.add_argument('--output', '-o', default='output', help='Output filename prefix')
    parser.add_argument('--types', '-t', nargs='+', 
                       default=['choice', 'sorting', 'matching', 'essay'],
                       help='Question types: choice sorting matching essay')
    parser.add_argument('--num', '-n', type=int, default=3, help='Number of questions per type')
    parser.add_argument('--use-deepseek', action='store_true', help='Use DeepSeek API')
    parser.add_argument('--api-key', help='DeepSeek API key')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File does not exist - {args.input_file}")
        return
    
    # Process document
    print("Processing document...")
    processor = DocumentProcessor()
    try:
        text, metadata = processor.extract_text(args.input_file)
        print(f"Successfully extracted text, length: {len(text)} characters")
        print(f"Sentences: {metadata['sentences_count']}, Words: {metadata['words_count']}")
    except Exception as e:
        print(f"Document processing failed: {e}")
        return
    
    # Generate test questions
    print("Generating test questions...")
    generator = TestGenerator(use_deepseek=args.use_deepseek, api_key=args.api_key)
    
    try:
        result = generator.generate_questions(text, args.types, args.num)
        
        # Export results
        exporter = TestExporter()
        exporter.export_to_json(result, f"{args.output}.json")
        exporter.export_to_txt(result, f"{args.output}.txt")
        
        print(f"\nTest question generation completed!")
        print(f"JSON file: {args.output}.json")
        print(f"Text file: {args.output}.txt")
        
        # Statistics
        total_questions = result['metadata']['total_questions']
        print(f"\nGeneration Statistics:")
        for q_type, q_list in result['questions'].items():
            print(f"  {q_type}: {len(q_list)} questions")
        print(f"  Total: {total_questions} questions")
        
    except Exception as e:
        print(f"Test question generation failed: {e}")

if __name__ == "__main__":
    main()
