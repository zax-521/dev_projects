#!/usr/bin/env python3
"""
Главное приложение Справочного Робота
Предоставляет функции прогноза погоды, курсов валют, перевода слов, калькулятора и конвертера единиц
Поддерживает голосовое воспроизведение и голосовые команды, сохраняет результаты в базу данных
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Импорт пользовательских модулей
from api.weather import get_weather
from api.currency import get_exchange_rate
from api.translation import translate_text
from api.unit_converter import convert_units
from utils.calculator import calculate_expression
from utils.speech import text_to_speech, speech_to_text
from database.db import init_db, save_result, get_history

# Импорт модуля DeepSeek API
try:
    from api.deepseek_api import ask_deepseek_question
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Инициализация базы данных
init_db()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def weather_api():
    """API прогноза погоды"""
    data = request.json
    city = data.get('city', 'Moscow')
    
    try:
        weather_data = get_weather(city)
        save_result('weather', {'city': city, 'data': weather_data})
        return jsonify({'success': True, 'data': weather_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency', methods=['POST'])
def currency_api():
    """API конвертации валют"""
    data = request.json
    from_currency = data.get('from', 'USD')
    to_currency = data.get('to', 'RUB')
    amount = data.get('amount', 1)
    
    try:
        rate_data = get_exchange_rate(from_currency, to_currency, amount)
        save_result('currency', {
            'from': from_currency,
            'to': to_currency,
            'amount': amount,
            'data': rate_data
        })
        return jsonify({'success': True, 'data': rate_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_api():
    """API перевода слов"""
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source', 'en')
    target_lang = data.get('target', 'ru')
    
    try:
        translation = translate_text(text, source_lang, target_lang)
        save_result('translation', {
            'text': text,
            'source': source_lang,
            'target': target_lang,
            'translation': translation
        })
        return jsonify({'success': True, 'data': translation})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_api():
    """API калькулятора"""
    data = request.json
    expression = data.get('expression', '')
    
    try:
        result = calculate_expression(expression)
        save_result('calculator', {
            'expression': expression,
            'result': result
        })
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/convert-units', methods=['POST'])
def convert_units_api():
    """API конвертации единиц"""
    data = request.json
    value = data.get('value', 1)
    from_unit = data.get('from_unit', 'meter')
    to_unit = data.get('to_unit', 'kilometer')
    category = data.get('category', 'length')
    
    try:
        result = convert_units(value, from_unit, to_unit, category)
        save_result('unit_conversion', {
            'value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'category': category,
            'result': result
        })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text_api():
    """API преобразования речи в текст"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    try:
        text = speech_to_text(audio_file)
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech_api():
    """API преобразования текста в речь"""
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'ru')
    
    try:
        result = text_to_speech(text, language)
        if result['success']:
            return jsonify({'success': True, 'audio': result['audio']})
        else:
            return jsonify({'success': False, 'error': result.get('error', '未知错误')}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def history_api():
    """API получения истории операций"""
    try:
        history = get_history()
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/deepseek-ask', methods=['POST'])
def deepseek_ask_api():
    """API вопросов и ответов DeepSeek"""
    if not DEEPSEEK_AVAILABLE:
        return jsonify({'success': False, 'error': 'Модуль DeepSeek API недоступен'}), 501
    
    data = request.json
    question = data.get('question', '')
    context = data.get('context', '')
    
    if not question:
        return jsonify({'success': False, 'error': 'Вопрос не может быть пустым'}), 400
    
    try:
        answer_data = ask_deepseek_question(question, context)
        save_result('deepseek_qa', {
            'question': question,
            'context': context,
            'answer': answer_data
        })
        return jsonify({'success': True, 'data': answer_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Предоставление статических файлов"""
    return send_from_directory('static', filename)

@app.route('/debug_voice.html')
def debug_voice():
    """Страница отладки записи голоса"""
    return send_from_directory('.', 'debug_voice.html')

@app.route('/test_voice_recording.html')
def test_voice_recording():
    """Страница тестирования записи голоса"""
    return send_from_directory('.', 'test_voice_recording.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
