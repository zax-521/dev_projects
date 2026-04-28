#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支持DeepSeek模型的测试题生成器
支持PDF、Word文档处理，生成四种类型的测试题
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

# 文档处理相关库
try:
    from PyPDF2 import PdfReader
    import docx
    from docx import Document
except ImportError:
    print("请安装所需库: pip install PyPDF2 python-docx")

# 自然语言处理库
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk import pos_tag
    # 下载必要的NLTK数据
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
    print("如需使用NLTK功能，请安装: pip install nltk")

# 设置日志
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
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat_completion(self, messages: List[Dict], model: str = "deepseek-chat", 
                       temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """调用DeepSeek聊天补全API"""
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
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
        except KeyError as e:
            logger.error(f"DeepSeek API响应格式错误: {e}")
            raise

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']
    
    def extract_text(self, file_path: str) -> Tuple[str, Dict]:
        """从文件中提取文本并返回元数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_size = os.path.getsize(file_path)
        max_file_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_file_size:
            raise ValueError(f"文件过大: {file_size}字节，最大支持{max_file_size}字节")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            text = self._extract_from_word(file_path)
        elif ext == '.txt':
            text = self._extract_from_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        # 清理文本
        text = self._clean_text(text)
        
        # 生成元数据
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
        """从PDF提取文本"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"第{page_num + 1}页:\n{page_text}\n\n"
        except Exception as e:
            logger.error(f"PDF提取失败: {e}")
            raise
        return text
    
    def _extract_from_word(self, file_path: str) -> str:
        """从Word文档提取文本"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Word文档提取失败: {e}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """从文本文件提取文本"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"文本文件提取失败: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        try:
            # 对于中文文本，使用更合适的分割方法
            sentences = re.split(r'[。！？\n]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            if len(sentences) < 3:
                # 如果分割不够，尝试按句号分割
                sentences = re.split(r'[。！？\.\?!\n]+', text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            return sentences
        except:
            # 最终回退方案
            sentences = re.split(r'[。！？\.\?!\n]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _split_into_words(self, text: str) -> List[str]:
        """将文本分割成单词"""
        try:
            words = word_tokenize(text)
            return [w for w in words if w.isalnum()]
        except:
            return re.findall(r'\b\w+\b', text)

class TestGenerator:
    """测试题生成器"""
    
    def __init__(self, use_deepseek=False, api_key=None):
        self.use_deepseek = use_deepseek
        self.deepseek_client = None
        
        if use_deepseek and api_key:
            self.deepseek_client = DeepSeekClient(api_key)
        
        # 中文停用词
        self.chinese_stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
        ])
        
        logger.info(f"测试题生成器初始化完成 - DeepSeek: {use_deepseek}")
    
    def generate_questions(self, text: str, question_types: List[str], num_questions: int = 5) -> Dict[str, Any]:
        """生成测试题"""
        if len(text) < 50:
            raise ValueError("文本内容过短，无法生成有效的测试题")
        
        # 限制文本长度
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
                logger.warning(f"跳过不支持的题型: {q_type}")
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
                        logger.info(f"成功生成 {q_type} 题型第 {i+1} 题")
                    
                except Exception as e:
                    logger.error(f"生成 {q_type} 题型第 {i+1} 题失败: {e}")
                    continue
            
            questions[q_type] = type_questions
            metadata['total_questions'] += len(type_questions)
        
        return {
            'questions': questions,
            'metadata': metadata
        }
    
    def _generate_local(self, text: str, q_type: str) -> Dict[str, Any]:
        """本地生成题目"""
        strategies = {
            'choice': self._generate_choice,
            'sorting': self._generate_sorting,
            'matching': self._generate_matching,
            'essay': self._generate_essay
        }
        return strategies[q_type](text)
    
    def _generate_choice(self, text: str) -> Dict[str, Any]:
        """生成选择题"""
        sentences = self._split_into_sentences(text)
        if len(sentences) < 3:
            return None
        
        base_sentence = random.choice(sentences)
        
        question_templates = [
            f"关于\"{base_sentence}\"的理解，以下哪个选项最准确？",
            f"根据\"{base_sentence}\"的内容，以下哪个说法是正确的？",
            f"\"{base_sentence}\"主要表达了什么观点？"
        ]
        
        question = random.choice(question_templates)
        
        options = [
            "准确反映了原文的含义",
            "过度解读了原文",
            "忽略了重要细节", 
            "理解存在偏差"
        ]
        random.shuffle(options)
        
        return {
            'type': 'choice',
            'question': question,
            'options': options,
            'answer': 'A',
            'explanation': '请结合原文内容进行分析',
            'difficulty': random.choice(['简单', '中等', '困难'])
        }
    
    def _generate_sorting(self, text: str) -> Dict[str, Any]:
        """生成排序题"""
        sentences = self._split_into_sentences(text)
        if len(sentences) < 4:
            return None
        
        selected_sentences = random.sample(sentences, min(4, len(sentences)))
        random.shuffle(selected_sentences)
        
        return {
            'type': 'sorting',
            'question': '请将以下句子按照逻辑顺序排列：',
            'items': selected_sentences,
            'correct_order': list(range(len(selected_sentences))),
            'explanation': '正确的顺序应该符合逻辑连贯性'
        }
    
    def _generate_matching(self, text: str) -> Dict[str, Any]:
        """生成配对题"""
        keywords = self._extract_keywords(text)
        concepts = list(set(keywords))[:4]
        
        if len(concepts) < 2:
            return None
        
        left_items = concepts[:3]
        right_items = [f"关于{concept}的描述" for concept in left_items]
        random.shuffle(right_items)
        
        return {
            'type': 'matching',
            'question': '请将左边的概念与右边的描述正确配对：',
            'left_items': left_items,
            'right_items': right_items,
            'correct_pairs': list(zip(left_items, right_items)),
            'explanation': '正确的配对应该基于概念的本质特征'
        }
    
    def _generate_essay(self, text: str) -> Dict[str, Any]:
        """生成解答题"""
        essay_prompts = [
            "请总结本文的核心观点和主要论据",
            "分析本文的论证结构和逻辑关系",
            "本文对你有什么启发？请结合实际情况谈谈你的理解",
            "评价本文的优缺点，并提出改进建议"
        ]
        
        return {
            'type': 'essay',
            'question': random.choice(essay_prompts),
            'points': 15,
            'suggested_length': '300-500字',
            'evaluation_criteria': ['内容完整性', '逻辑清晰度', '观点深度', '语言表达']
        }
    
    def _generate_with_deepseek(self, text: str, q_type: str) -> Dict[str, Any]:
        """使用DeepSeek API生成题目"""
        prompts = {
            'choice': f"""根据以下文本生成一个高质量的选择题：
文本：{text[:1000]}
要求：
1. 问题要基于文本内容
2. 提供4个有区分度的选项
3. 标明正确答案
4. 提供解析
请以JSON格式返回：{{"question": "问题", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "解析"}}""",
            
            'sorting': f"""根据以下文本生成一个排序题：
文本：{text[:1000]}
要求：
1. 选择3-5个有逻辑关系的句子
2. 打乱它们的顺序
3. 提供正确顺序
请以JSON格式返回：{{"question": "问题", "items": ["句子1", "句子2", ...], "correct_order": [0,1,2,...]}}""",
            
            'matching': f"""根据以下文本生成一个配对题：
文本：{text[:1000]}
要求：
1. 左边列出3-4个关键概念
2. 右边列出对应的描述
3. 概念和描述要相关但顺序打乱
请以JSON格式返回：{{"question": "问题", "left_items": ["概念1", ...], "right_items": ["描述1", ...], "correct_pairs": [["概念1","描述1"], ...]}}""",
            
            'essay': f"""根据以下文本生成一个解答题：
文本：{text[:1000]}
要求：
1. 问题要有深度和启发性
2. 适合300-500字的回答
3. 提供评分标准
请以JSON格式返回：{{"question": "问题", "suggested_length": "300-500字", "evaluation_criteria": ["标准1", "标准2"]}}"""
        }
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的教育专家，擅长根据文本内容生成各种类型的测试题目。"},
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
            logger.error(f"DeepSeek API调用失败: {e}")
            return self._generate_local(text, q_type)
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """提取关键词"""
        try:
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            pos_filter = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']
            
            filtered_words = []
            for word, pos in pos_tags:
                if (any(pos.startswith(tag) for tag in pos_filter) and 
                    word.lower() not in stopwords.words('english') and
                    word not in self.chinese_stopwords and
                    len(word) > 1):
                    filtered_words.append(word)
            
            from collections import Counter
            word_freq = Counter(filtered_words)
            return [word for word, _ in word_freq.most_common(top_n)]
            
        except Exception as e:
            logger.warning(f"关键词提取失败: {e}")
            words = re.findall(r'\b\w+\b', text)
            filtered_words = [w for w in words if len(w) > 1 and w not in self.chinese_stopwords]
            from collections import Counter
            word_freq = Counter(filtered_words)
            return [word for word, _ in word_freq.most_common(top_n)]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        try:
            # 对于中文文本，使用更合适的分割方法
            sentences = re.split(r'[。！？\n]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            if len(sentences) < 3:
                # 如果分割不够，尝试按句号分割
                sentences = re.split(r'[。！？\.\?!\n]+', text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            return sentences
        except:
            # 最终回退方案
            sentences = re.split(r'[。！？\.\?!\n]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _get_default_points(self, q_type: str) -> int:
        """获取默认分值"""
        points_map = {
            'choice': 2,
            'sorting': 3,
            'matching': 4,
            'essay': 15
        }
        return points_map.get(q_type, 1)
    
    def _parse_ai_response(self, response: str, q_type: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 清理响应内容，移除可能的代码块标记
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # 移除 ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # 移除 ```
            cleaned_response = cleaned_response.strip()
            
            # 尝试解析JSON响应
            data = json.loads(cleaned_response)
            
            # 确保基本字段存在
            if 'question' not in data:
                data['question'] = f"请根据文本内容回答相关问题"
            
            data['type'] = q_type
            return data
            
        except json.JSONDecodeError:
            logger.warning("AI响应不是有效的JSON格式，使用默认结构")
            return {
                'type': q_type,
                'question': response[:150] + "..." if len(response) > 150 else response,
                'explanation': '请参考原文内容进行分析'
            }

class TestExporter:
    """测试题导出器"""
    
    @staticmethod
    def export_to_json(result: Dict, output_file: str):
        """导出为JSON文件"""
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON文件已导出: {output_file}")
    
    @staticmethod
    def export_to_txt(result: Dict, output_file: str):
        """导出为文本文件"""
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入元数据
            metadata = result.get('metadata', {})
            f.write("测试题生成报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {metadata.get('generation_time', 'N/A')}\n")
            f.write(f"文本长度: {metadata.get('text_length', 0)} 字符\n")
            f.write(f"题目类型: {', '.join(metadata.get('question_types', []))}\n")
            f.write(f"总题目数: {metadata.get('total_questions', 0)}\n")
            f.write("=" * 50 + "\n\n")
            
            # 写入题目
            questions = result.get('questions', {})
            for q_type, q_list in questions.items():
                f.write(f"\n{'='*50}\n")
                f.write(f"{q_type.upper()} 题型\n")
                f.write(f"{'='*50}\n")
                
                for i, question in enumerate(q_list, 1):
                    f.write(f"\n{i}. {question['question']}\n")
                    
                    if q_type == 'choice':
                        for j, option in enumerate(question['options']):
                            f.write(f"   {chr(65+j)}. {option}\n")
                        f.write(f"   答案: {question.get('answer', 'N/A')}\n")
                        f.write(f"   解析: {question.get('explanation', '请参考原文')}\n")
                    
                    elif q_type == 'sorting':
                        for j, item in enumerate(question['items']):
                            f.write(f"   {j+1}. {item}\n")
                        f.write(f"   解析: {question.get('explanation', '请参考原文')}\n")
                    
                    elif q_type == 'matching':
                        f.write("   左项: " + ", ".join(question['left_items']) + "\n")
                        f.write("   右项: " + ", ".join(question['right_items']) + "\n")
                        f.write(f"   解析: {question.get('explanation', '请参考原文')}\n")
                    
                    elif q_type == 'essay':
                        f.write(f"   建议字数: {question.get('suggested_length', 'N/A')}\n")
                        f.write(f"   分值: {question.get('points', 'N/A')}\n")
                        f.write(f"   评分标准: {', '.join(question.get('evaluation_criteria', []))}\n")
                    
                    f.write(f"   难度: {question.get('difficulty', '中等')}\n")
        
        logger.info(f"文本文件已导出: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='从文档生成测试题 (支持DeepSeek)')
    parser.add_argument('input_file', help='输入文件路径 (PDF/DOC/DOCX/TXT)')
    parser.add_argument('--output', '-o', default='output', help='输出文件名前缀')
    parser.add_argument('--types', '-t', nargs='+', 
                       default=['choice', 'sorting', 'matching', 'essay'],
                       help='题目类型: choice sorting matching essay')
    parser.add_argument('--num', '-n', type=int, default=3, help='每种题型的数量')
    parser.add_argument('--use-deepseek', action='store_true', help='使用DeepSeek API')
    parser.add_argument('--api-key', help='DeepSeek API密钥')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在 - {args.input_file}")
        return
    
    # 处理文档
    print("正在处理文档...")
    processor = DocumentProcessor()
    try:
        text, metadata = processor.extract_text(args.input_file)
        print(f"成功提取文本，长度: {len(text)} 字符")
        print(f"句子数: {metadata['sentences_count']}, 单词数: {metadata['words_count']}")
    except Exception as e:
        print(f"文档处理失败: {e}")
        return
    
    # 生成测试题
    print("正在生成测试题...")
    generator = TestGenerator(use_deepseek=args.use_deepseek, api_key=args.api_key)
    
    try:
        result = generator.generate_questions(text, args.types, args.num)
        
        # 导出结果
        exporter = TestExporter()
        exporter.export_to_json(result, f"{args.output}.json")
        exporter.export_to_txt(result, f"{args.output}.txt")
        
        print(f"\n测试题生成完成！")
        print(f"JSON文件: {args.output}.json")
        print(f"文本文件: {args.output}.txt")
        
        # 统计信息
        total_questions = result['metadata']['total_questions']
        print(f"\n生成统计:")
        for q_type, q_list in result['questions'].items():
            print(f"  {q_type}: {len(q_list)} 题")
        print(f"  总计: {total_questions} 题")
        
    except Exception as e:
        print(f"测试题生成失败: {e}")

if __name__ == "__main__":
    main()
