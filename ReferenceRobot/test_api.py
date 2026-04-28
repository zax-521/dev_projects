import requests
import json

def test_weather_api():
    try:
        response = requests.post('http://localhost:5000/api/weather', 
                               json={'city': 'Moscow'},
                               headers={'Content-Type': 'application/json'})
        print('Status Code:', response.status_code)
        print('Response:', response.json())
    except Exception as e:
        print('Error:', e)

def test_translation_api():
    try:
        response = requests.post('http://localhost:5000/api/translate', 
                               json={'text': 'Hello', 'source': 'en', 'target': 'ru'},
                               headers={'Content-Type': 'application/json'})
        print('\nTranslation API Test:')
        print('Status Code:', response.status_code)
        print('Response:', response.json())
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    test_weather_api()
    test_translation_api()
