import sys
sys.path.append(r"C:\Users\jcarl\OneDrive\Escritorio\ahp_portfolio")
from apps.api.services.pipeline import run_analysis_pipeline

profiles = ["conservador", "moderado", "agresivo", "muy_agresivo", "dividendos", "tecnologico", "esg"]

for p in profiles:
    print(f"Testing {p}...")
    try:
        res = run_analysis_pipeline(p, False)
        print("Success:", res.get('success'))
    except Exception as e:
        import traceback
        traceback.print_exc()
