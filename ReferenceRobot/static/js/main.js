// Главный JavaScript файл Справочного Робота

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация
    initApp();
    
    // Установка текущей даты
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('ru-RU');
    
    // Переключение вкладок
    initTabSwitching();
    
    // Инициализация функциональных модулей
    initWeatherModule();
    initCurrencyModule();
    initTranslationModule();
    initCalculatorModule();
    initUnitConverterModule();
    initSpeechModule();
    initHistoryModule();
    initVoiceControls();
    
    // Проверка статуса системы
    checkSystemStatus();
});

// Инициализация приложения
function initApp() {
    console.log('Инициализация приложения Справочного Робота...');
}

// Функция переключения вкладок
function initTabSwitching() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Обновление активной кнопки
            navButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Отображение содержимого соответствующей вкладки
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
            
            // Если это вкладка истории, обновить историю
            if (tabId === 'history') {
                loadHistory();
            }
        });
    });
}

// Модуль погоды
function initWeatherModule() {
    const getWeatherBtn = document.getElementById('get-weather-btn');
    const cityInput = document.getElementById('city-input');
    
    getWeatherBtn.addEventListener('click', function() {
        const city = cityInput.value.trim();
        if (!city) {
            alert('Введите название города');
            return;
        }
        
        getWeather(city);
    });
    
    // Запрос по нажатию Enter
    cityInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            getWeatherBtn.click();
        }
    });
}

function getWeather(city) {
    const weatherResult = document.getElementById('weather-result');
    weatherResult.innerHTML = '<div class="loading">Запрос погоды...</div>';
    
    fetch('/api/weather', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ city: city })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayWeatherResult(data.data);
        } else {
            weatherResult.innerHTML = `<div class="error">Ошибка запроса: ${data.error}</div>`;
        }
    })
    .catch(error => {
        weatherResult.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayWeatherResult(weatherData) {
    const weatherResult = document.getElementById('weather-result');
    
    const weatherIcon = getWeatherIcon(weatherData.weather_main);
    
    const html = `
        <div class="result-card">
            <h3>Погода в ${weatherData.city}</h3>
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-size: 3rem;">${weatherIcon}</div>
                <div>
                    <p><span class="highlight">${weatherData.temperature}°C</span> (ощущается как: ${weatherData.feels_like}°C)</p>
                    <p>${weatherData.weather}</p>
                    <p>Влажность: ${weatherData.humidity}% | Скорость ветра: ${weatherData.wind_speed} м/с</p>
                    <p>Давление: ${weatherData.pressure} гПа | Видимость: ${weatherData.visibility} метров</p>
                    <p>Восход: ${weatherData.sunrise} | Закат: ${weatherData.sunset}</p>
                    <p style="font-size: 0.9rem; color: #666;">Источник данных: ${weatherData.source} | Обновлено: ${weatherData.timestamp}</p>
                </div>
            </div>
        </div>
    `;
    
    weatherResult.innerHTML = html;
}

function getWeatherIcon(weatherMain) {
    const icons = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Snow': '❄️',
        'Thunderstorm': '⛈️',
        'Mist': '🌫️',
        'Fog': '🌁'
    };
    
    return icons[weatherMain] || '🌤️';
}

// Модуль конвертации валют
function initCurrencyModule() {
    const convertBtn = document.getElementById('convert-currency-btn');
    
    convertBtn.addEventListener('click', function() {
        const amount = parseFloat(document.getElementById('amount-input').value);
        const fromCurrency = document.getElementById('from-currency').value;
        const toCurrency = document.getElementById('to-currency').value;
        
        if (isNaN(amount) || amount <= 0) {
            alert('Введите корректную сумму');
            return;
        }
        
        convertCurrency(amount, fromCurrency, toCurrency);
    });
}

function convertCurrency(amount, fromCurrency, toCurrency) {
    const currencyResult = document.getElementById('currency-result');
    currencyResult.innerHTML = '<div class="loading">Конвертация валюты...</div>';
    
    fetch('/api/currency', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            amount: amount,
            from: fromCurrency,
            to: toCurrency
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayCurrencyResult(data.data);
        } else {
            currencyResult.innerHTML = `<div class="error">Ошибка конвертации: ${data.error}</div>`;
        }
    })
    .catch(error => {
        currencyResult.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayCurrencyResult(currencyData) {
    const currencyResult = document.getElementById('currency-result');
    
    const html = `
        <div class="result-card">
            <h3>Результат конвертации валюты</h3>
            <p><span class="highlight">${currencyData.amount} ${currencyData.from_currency}</span> = 
               <span class="highlight">${currencyData.converted_amount} ${currencyData.to_currency}</span></p>
            <p>Курс: 1 ${currencyData.from_currency} = ${currencyData.exchange_rate} ${currencyData.to_currency}</p>
            <p>Обратный курс: 1 ${currencyData.to_currency} = ${(1/currencyData.exchange_rate).toFixed(6)} ${currencyData.from_currency}</p>
            <p style="font-size: 0.9rem; color: #666;">Источник данных: ${currencyData.source} | Обновлено: ${currencyData.last_updated}</p>
        </div>
    `;
    
    currencyResult.innerHTML = html;
}

// Модуль перевода
function initTranslationModule() {
    const translateBtn = document.getElementById('translate-btn');
    
    translateBtn.addEventListener('click', function() {
        const sourceText = document.getElementById('source-text').value.trim();
        const sourceLang = document.getElementById('source-lang').value;
        const targetLang = document.getElementById('target-lang').value;
        
        if (!sourceText) {
            alert('Введите текст для перевода');
            return;
        }
        
        translateText(sourceText, sourceLang, targetLang);
    });
}

function translateText(text, sourceLang, targetLang) {
    const translationResult = document.getElementById('translation-result');
    translationResult.innerHTML = '<div class="loading">Перевод...</div>';
    
    fetch('/api/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            source: sourceLang,
            target: targetLang
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayTranslationResult(data.data);
        } else {
            translationResult.innerHTML = `<div class="error">Ошибка перевода: ${data.error}</div>`;
        }
    })
    .catch(error => {
        translationResult.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayTranslationResult(translationData) {
    const translationResult = document.getElementById('translation-result');
    
    const html = `
        <div class="result-card">
            <h3>Результат перевода</h3>
            <p><strong>Исходный текст (${translationData.source_lang}):</strong> ${translationData.original_text}</p>
            <p><strong>Перевод (${translationData.target_lang}):</strong> <span class="highlight">${translationData.translated_text}</span></p>
            <p style="font-size: 0.9rem; color: #666;">Источник данных: ${translationData.source}</p>
        </div>
    `;
    
    translationResult.innerHTML = html;
}

// Модуль калькулятора
function initCalculatorModule() {
    const calculateBtn = document.getElementById('calculate-btn');
    const calcInput = document.getElementById('calc-input');
    const calcButtons = document.querySelectorAll('.calc-btn');
    
    // Событие нажатия кнопки вычисления
    calculateBtn.addEventListener('click', function() {
        const expression = calcInput.value.trim();
        if (!expression) {
            alert('Введите математическое выражение');
            return;
        }
        
        calculateExpression(expression);
    });
    
    // События нажатия кнопок калькулятора
    calcButtons.forEach(button => {
        button.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            
            if (this.id === 'calc-equals') {
                calculateExpression(calcInput.value);
            } else if (this.id === 'calc-clear') {
                calcInput.value = '';
                document.getElementById('calc-result').textContent = 'Результат будет отображен здесь';
            } else if (this.id === 'calc-backspace') {
                calcInput.value = calcInput.value.slice(0, -1);
            } else {
                calcInput.value += value;
            }
        });
    });
    
    // Вычисление по нажатию Enter
    calcInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculateExpression(this.value);
        }
    });
}

function calculateExpression(expression) {
    const calcResult = document.getElementById('calc-result');
    calcResult.textContent = 'Вычисление...';
    
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ expression: expression })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            calcResult.textContent = `Результат: ${data.result}`;
        } else {
            calcResult.textContent = `Ошибка: ${data.error}`;
        }
    })
    .catch(error => {
        calcResult.textContent = `Сетевая ошибка: ${error.message}`;
    });
}

// Модуль конвертера единиц
function initUnitConverterModule() {
    const convertBtn = document.getElementById('convert-units-btn');
    const unitCategory = document.getElementById('unit-category');
    
    convertBtn.addEventListener('click', function() {
        const value = parseFloat(document.getElementById('unit-value').value);
        const category = unitCategory.value;
        const fromUnit = document.getElementById('from-unit').value;
        const toUnit = document.getElementById('to-unit').value;
        
        if (isNaN(value)) {
            alert('Введите корректное значение');
            return;
        }
        
        convertUnits(value, category, fromUnit, toUnit);
    });
    
    // Обновление опций единиц при изменении категории
    unitCategory.addEventListener('change', function() {
        updateUnitOptions(this.value);
    });
    
    // Инициализация опций единиц
    updateUnitOptions(unitCategory.value);
}

function updateUnitOptions(category) {
    // Здесь должны быть получены доступные единицы из API, но для упрощения используем жестко заданные
    const units = {
        'length': ['meter', 'kilometer', 'centimeter', 'millimeter', 'mile', 'yard', 'foot', 'inch'],
        'weight': ['kilogram', 'gram', 'milligram', 'ton', 'pound', 'ounce', 'jin', 'liang'],
        'temperature': ['celsius', 'fahrenheit', 'kelvin'],
        'volume': ['liter', 'milliliter', 'cubic_meter', 'gallon', 'quart', 'pint'],
        'speed': ['mps', 'kph', 'mph', 'knot'],
        'area': ['square_meter', 'square_kilometer', 'hectare', 'acre', 'square_mile'],
        'time': ['second', 'minute', 'hour', 'day', 'week', 'month', 'year'],
        'data': ['byte', 'kilobyte', 'megabyte', 'gigabyte', 'terabyte']
    };
    
    const fromUnitSelect = document.getElementById('from-unit');
    const toUnitSelect = document.getElementById('to-unit');
    
    const categoryUnits = units[category] || units['length'];
    
    // Обновление опций
    fromUnitSelect.innerHTML = '';
    toUnitSelect.innerHTML = '';
    
    categoryUnits.forEach(unit => {
        const option1 = document.createElement('option');
        option1.value = unit;
        option1.textContent = formatUnitName(unit);
        fromUnitSelect.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = unit;
        option2.textContent = formatUnitName(unit);
        toUnitSelect.appendChild(option2);
    });
    
    // Установка значений по умолчанию
    if (categoryUnits.length > 1) {
        fromUnitSelect.value = categoryUnits[0];
        toUnitSelect.value = categoryUnits[1];
    }
}

function formatUnitName(unit) {
    const names = {
        'meter': 'Метр (m)',
        'kilometer': 'Километр (km)',
        'centimeter': 'Сантиметр (cm)',
        'millimeter': 'Миллиметр (mm)',
        'mile': 'Мили',
        'yard': 'Ярды',
        'foot': 'Футы',
        'inch': 'Дюймы',
        'kilogram': 'Килограмм (kg)',
        'gram': 'Грамм (g)',
        'milligram': 'Миллиграмм (mg)',
        'ton': 'Тонна',
        'pound': 'Фунт',
        'ounce': 'Унция',
        'jin': 'Цзинь',
        'liang': 'Лян',
        'celsius': 'Градусы Цельсия (°C)',
        'fahrenheit': 'Градусы Фаренгейта (°F)',
        'kelvin': 'Кельвин (K)',
        'liter': 'Литр (L)',
        'milliliter': 'Миллилитр (mL)',
        'cubic_meter': 'Кубический метр (m³)',
        'gallon': 'Галлон',
        'quart': 'Кварта',
        'pint': 'Пинта',
        'mps': 'Метры в секунду (m/s)',
        'kph': 'Километры в час (km/h)',
        'mph': 'Мили в час (mph)',
        'knot': 'Узлы (knot)',
        'square_meter': 'Квадратный метр (m²)',
        'square_kilometer': 'Квадратный километр (km²)',
        'hectare': 'Гектар',
        'acre': 'Акр',
        'square_mile': 'Квадратная миля',
        'second': 'Секунда',
        'minute': 'Минута',
        'hour': 'Час',
        'day': 'День',
        'week': 'Неделя',
        'month': 'Месяц',
        'year': 'Год',
        'byte': 'Байт (B)',
        'kilobyte': 'Килобайт (KB)',
        'megabyte': 'Мегабайт (MB)',
        'gigabyte': 'Гигабайт (GB)',
        'terabyte': 'Терабайт (TB)'
    };
    
    return names[unit] || unit;
}

function convertUnits(value, category, fromUnit, toUnit) {
    const unitResult = document.getElementById('unit-converter-result');
    unitResult.innerHTML = '<div class="loading">Конвертация единиц...</div>';
    
    fetch('/api/convert-units', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            value: value,
            category: category,
            from_unit: fromUnit,
            to_unit: toUnit
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayUnitConversionResult(data.data);
        } else {
            unitResult.innerHTML = `<div class="error">Ошибка конвертации: ${data.error}</div>`;
        }
    })
    .catch(error => {
        unitResult.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayUnitConversionResult(conversionData) {
    const unitResult = document.getElementById('unit-converter-result');
    
    const html = `
        <div class="result-card">
            <h3>Результат конвертации единиц (${conversionData.category_name})</h3>
            <p><span class="highlight">${conversionData.value} ${formatUnitName(conversionData.from_unit)}</span> = 
               <span class="highlight">${conversionData.converted_value} ${formatUnitName(conversionData.to_unit)}</span></p>
        </div>
    `;
    
    unitResult.innerHTML = html;
}

// Модуль голосовых функций
function initSpeechModule() {
    const textToSpeechBtn = document.getElementById('text-to-speech-btn');
    const uploadAudioBtn = document.getElementById('upload-audio-btn');
    const audioFileInput = document.getElementById('audio-file');
    
    textToSpeechBtn.addEventListener('click', function() {
        const text = document.getElementById('speech-text').value.trim();
        const language = document.getElementById('speech-language').value;
        
        if (!text) {
            alert('Введите текст для преобразования в речь');
            return;
        }
        
        convertTextToSpeech(text, language);
    });
    
    uploadAudioBtn.addEventListener('click', function() {
        audioFileInput.click();
    });
    
    audioFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            convertSpeechToText(this.files[0]);
        }
    });
}

function convertTextToSpeech(text, language) {
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.innerHTML = '<div class="loading">Генерация речи...</div>';
    
    fetch('/api/text-to-speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            language: language
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAudioPlayer(data.audio, text);
        } else {
            audioPlayer.innerHTML = `<div class="error">Ошибка генерации речи: ${data.error}</div>`;
        }
    })
    .catch(error => {
        audioPlayer.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function convertSpeechToText(audioFile) {
    const recognitionResult = document.getElementById('recognition-result');
    recognitionResult.innerHTML = '<div class="loading">Распознавание речи...</div>';
    
    const formData = new FormData();
    formData.append('audio', audioFile);
    
    fetch('/api/speech-to-text', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            recognitionResult.innerHTML = `
                <div class="result-card">
                    <h3>Результат распознавания речи</h3>
                    <p><span class="highlight">${data.text}</span></p>
                </div>
            `;
        } else {
            recognitionResult.innerHTML = `<div class="error">Ошибка распознавания речи: ${data.error}</div>`;
        }
    })
    .catch(error => {
        recognitionResult.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayAudioPlayer(audioBase64, text) {
    const audioPlayer = document.getElementById('audio-player');
    
    const html = `
        <div class="result-card">
            <h3>Аудиоплеер</h3>
            <p>Текст: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}</p>
            <audio controls style="width: 100%; margin-top: 10px;">
                <source src="data:audio/mp3;base64,${audioBase64}" type="audio/mp3">
                Ваш браузер не поддерживает аудиоплеер
            </audio>
            <button id="download-audio-btn" class="action-btn secondary" style="margin-top: 10px;">
                <i class="fas fa-download"></i> Скачать аудио
            </button>
        </div>
    `;
    
    audioPlayer.innerHTML = html;
    
    // Добавление события для кнопки скачивания
    document.getElementById('download-audio-btn').addEventListener('click', function() {
        downloadAudio(audioBase64, 'speech.mp3');
    });
}

function downloadAudio(audioBase64, filename) {
    const link = document.createElement('a');
    link.href = `data:audio/mp3;base64,${audioBase64}`;
    link.download = filename;
    link.click();
}

// Модуль истории
function initHistoryModule() {
    const refreshBtn = document.getElementById('refresh-history-btn');
    const clearBtn = document.getElementById('clear-history-btn');
    const filterSelect = document.getElementById('history-filter');
    
    refreshBtn.addEventListener('click', function() {
        loadHistory();
    });
    
    clearBtn.addEventListener('click', function() {
        if (confirm('Вы уверены, что хотите очистить всю историю? Это действие нельзя отменить.')) {
            clearHistory();
        }
    });
    
    filterSelect.addEventListener('change', function() {
        loadHistory(this.value);
    });
    
    // Начальная загрузка истории
    loadHistory();
}

function loadHistory(filter = 'all') {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="loading">Загрузка истории...</div>';
    
    let url = '/api/history';
    if (filter !== 'all') {
        url += `?operation_type=${filter}`;
    }
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayHistory(data.history);
        } else {
            historyList.innerHTML = `<div class="error">Ошибка загрузки: ${data.error}</div>`;
        }
    })
    .catch(error => {
        historyList.innerHTML = `<div class="error">Сетевая ошибка: ${error.message}</div>`;
    });
}

function displayHistory(history) {
    const historyList = document.getElementById('history-list');
    
    if (history.length === 0) {
        historyList.innerHTML = '<div class="loading">История пуста</div>';
        return;
    }
    
    let html = '';
    history.forEach(item => {
        const operationNames = {
            'weather': 'Прогноз погоды',
            'currency': 'Конвертация валюты',
            'translation': 'Перевод',
            'calculator': 'Калькулятор',
            'unit_conversion': 'Конвертация единиц'
        };
        
        const operationName = operationNames[item.operation_type] || item.operation_type;
        
        html += `
            <div class="history-item">
                <div class="history-item-header">
                    <span>${operationName}</span>
                    <span>${item.timestamp}</span>
                </div>
                <div class="history-item-content">
                    ${formatHistoryContent(item)}
                </div>
            </div>
        `;
    });
    
    historyList.innerHTML = html;
}

function formatHistoryContent(item) {
    switch (item.operation_type) {
        case 'weather':
            return `Город: ${item.input.city}`;
        case 'currency':
            return `${item.input.amount} ${item.input.from} → ${item.result.converted_amount} ${item.input.to}`;
        case 'translation':
            return `${item.input.text.substring(0, 30)}${item.input.text.length > 30 ? '...' : ''} → ${item.result.translated_text.substring(0, 30)}${item.result.translated_text.length > 30 ? '...' : ''}`;
        case 'calculator':
            return `${item.input.expression} = ${item.result.result}`;
        case 'unit_conversion':
            return `${item.input.value} ${item.input.from_unit} → ${item.result.converted_value} ${item.input.to_unit}`;
        default:
            return JSON.stringify(item.input);
    }
}

function clearHistory() {
    // Примечание: здесь должна быть реализация API для очистки истории
    // Из-за ограничений по времени показываем только сообщение
    alert('Функция очистки истории требует поддержки API на сервере');
    loadHistory();
}

// Голосовое управление
function initVoiceControls() {
    console.log('Инициализация голосового управления...');
    
    const recordBtn = document.getElementById('record-btn');
    const playBtn = document.getElementById('play-btn');
    const recordingStatus = document.getElementById('recording-status');
    
    if (!recordBtn) {
        console.error('Ошибка: Не найден элемент с ID record-btn');
        return;
    }
    
    if (!recordingStatus) {
        console.error('Ошибка: Не найден элемент с ID recording-status');
        return;
    }
    
    console.log('Элементы найдены:', { recordBtn, playBtn, recordingStatus });
    
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    
    // Проверка поддержки MediaRecorder API
    function checkMediaRecorderSupport() {
        console.log('Проверка поддержки браузера...');
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            const errorMsg = 'Браузер не поддерживает запись с микрофона';
            console.error(errorMsg);
            recordingStatus.textContent = errorMsg;
            recordBtn.disabled = true;
            return false;
        }
        
        if (!window.MediaRecorder) {
            const errorMsg = 'Браузер не поддерживает MediaRecorder API';
            console.error(errorMsg);
            recordingStatus.textContent = errorMsg;
            recordBtn.disabled = true;
            return false;
        }
        
        console.log('Браузер поддерживает запись голоса');
        return true;
    }
    
    // Инициализация проверки поддержки
    if (!checkMediaRecorderSupport()) {
        console.log('Браузер не поддерживает запись голоса');
        return;
    }
    
    recordBtn.addEventListener('click', async function() {
        if (!isRecording) {
            // Начать запись
            try {
                recordingStatus.textContent = 'Запрос доступа к микрофону...';
                
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 44100
                    }
                });
                
                // Создать MediaRecorder с настройками для WAV
                const options = { mimeType: 'audio/webm' };
                mediaRecorder = new MediaRecorder(stream, options);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    recordingStatus.textContent = 'Обработка записи...';
                    
                    try {
                        // Создать аудиофайл
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        
                        // Проверить размер файла
                        if (audioBlob.size < 100) {
                            recordingStatus.textContent = 'Запись слишком короткая или пустая';
                            stream.getTracks().forEach(track => track.stop());
                            resetRecordingState();
                            return;
                        }
                        
                        // Отправить аудио на сервер для распознавания
                        const formData = new FormData();
                        formData.append('audio', audioBlob, 'recording.webm');
                        
                        recordingStatus.textContent = 'Распознавание речи...';
                        
                        const response = await fetch('/api/speech-to-text', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            recordingStatus.textContent = 'Запись завершена ✓';
                            document.getElementById('speech-text').value = data.text;
                            
                            // Автоматическое переключение на вкладку речи
                            setTimeout(() => {
                                document.querySelector('[data-tab="speech"]').click();
                            }, 500);
                        } else {
                            recordingStatus.textContent = `Ошибка распознавания: ${data.error}`;
                        }
                    } catch (error) {
                        recordingStatus.textContent = `Ошибка обработки: ${error.message}`;
                        console.error('Ошибка обработки записи:', error);
                    } finally {
                        // Остановить поток
                        stream.getTracks().forEach(track => track.stop());
                        resetRecordingState();
                    }
                };
                
                mediaRecorder.onerror = (event) => {
                    console.error('Ошибка MediaRecorder:', event.error);
                    recordingStatus.textContent = `Ошибка записи: ${event.error.name}`;
                    resetRecordingState();
                };
                
                // Начать запись с интервалом сбора данных
                mediaRecorder.start(1000); // Собирать данные каждую секунду
                isRecording = true;
                recordBtn.innerHTML = '<i class="fas fa-stop"></i> Остановить запись';
                recordBtn.classList.add('recording');
                recordingStatus.textContent = 'Запись... Говорите сейчас';
                playBtn.disabled = true;
                
                // Автоматическая остановка через 30 секунд
                setTimeout(() => {
                    if (isRecording && mediaRecorder && mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                    }
                }, 30000);
                
            } catch (error) {
                console.error('Ошибка доступа к микрофону:', error);
                recordingStatus.textContent = `Ошибка доступа к микрофону: ${getErrorMessage(error)}`;
                resetRecordingState();
            }
        } else {
            // Остановить запись
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            resetRecordingState();
        }
    });
    
    // Функция сброса состояния записи
    function resetRecordingState() {
        isRecording = false;
        recordBtn.innerHTML = '<i class="fas fa-microphone"></i> Начать запись';
        recordBtn.classList.remove('recording');
        recordBtn.disabled = false;
        playBtn.disabled = false;
        
        // Если статус не был изменен, установить по умолчанию
        if (!recordingStatus.textContent.includes('✓') && !recordingStatus.textContent.includes('Ошибка')) {
            recordingStatus.textContent = 'Готов к записи';
        }
    }
    
    // Функция получения понятного сообщения об ошибке
    function getErrorMessage(error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            return 'Доступ к микрофону запрещен. Разрешите доступ в настройках браузера.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            return 'Микрофон не найден. Убедитесь, что микрофон подключен.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            return 'Микрофон используется другим приложением.';
        } else if (error.name === 'OverconstrainedError') {
            return 'Требуемые параметры микрофона недоступны.';
        } else {
            return error.message || 'Неизвестная ошибка';
        }
    }
    
    playBtn.addEventListener('click', function() {
        const text = document.getElementById('speech-text').value;
        if (text) {
            convertTextToSpeech(text, 'ru');
        }
    });
    
    // Установить начальный статус
    recordingStatus.textContent = 'Готов к записи';
}

// Проверка статуса системы
function checkSystemStatus() {
    const speechStatus = document.getElementById('speech-status');
    
    // Проверка голосовых функций
    fetch('/api/text-to-speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: 'test',
            language: 'ru'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            speechStatus.textContent = 'Доступно';
            speechStatus.className = 'status-indicator active';
        } else {
            speechStatus.textContent = 'Недоступно';
            speechStatus.className = 'status-indicator';
        }
    })
    .catch(() => {
        speechStatus.textContent = 'Ошибка проверки';
        speechStatus.className = 'status-indicator';
    });
}
