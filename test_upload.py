import requests
try:
    url = 'http://localhost:8000/api/upload'
    files = {'file': open('c:/dev/ai-command-center/zrsd002.csv', 'rb')}
    r = requests.post(url, files=files)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print(e)
