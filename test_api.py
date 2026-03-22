import sys
sys.path.append(r"C:\Users\jcarl\OneDrive\Escritorio\ahp_portfolio")

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

print("Testing /api/questionnaire/submit...")
answers = {"q1": "b", "q2": "c", "q3": "b"} # Example, should be all 12 questions ideally
res = client.post("/api/questionnaire/submit", json={"answers": answers})
print("Submit Status:", res.status_code)
if res.status_code != 200:
    print("Error:", res.text)

print("\nTesting /api/analyze...")
res2 = client.post("/api/analyze", json={"profile": "moderado", "use_live": False})
print("Analyze Status:", res2.status_code)
if res2.status_code != 200:
    print("Error:", res2.text)

print("Done")
