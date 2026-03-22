import requests

try:
    print("Testing Next.js Proxy on 3000...")
    res2 = requests.post("http://127.0.0.1:3000/api/analyze", json={"profile": "moderado", "use_live": False})
    print("Proxy Code:", res2.status_code)
    print("Proxy Response:", res2.text)
except Exception as e:
    print(e)
