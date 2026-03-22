import requests

try:
    print("Testing /submit...")
    answers = {"q1": "b", "q2": "b", "q3": "c", "q4": "b", "q5": "c", "q6": "a", "q7": "c", "q8": "b", "q9": "c", "q10": "a", "q11": "b", "q12": "c"}
    res = requests.post("http://127.0.0.1:8000/api/questionnaire/submit", json={"answers": answers})
    print("Submit Code:", res.status_code)
    print("Submit Response:", res.text)
    
    print("\nTesting /analyze...")
    res2 = requests.post("http://127.0.0.1:8000/api/analyze", json={"profile": "moderado", "use_live": False})
    print("Analyze Code:", res2.status_code)
    try:
        print("Analyze Response:", res2.json().keys())
    except:
        print("Analyze Response:", res2.text)

except Exception as e:
    print(e)
