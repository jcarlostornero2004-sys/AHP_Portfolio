import sys
import os

# Add root to sys.path
sys.path.append(r"C:\Users\jcarl\OneDrive\Escritorio\ahp_portfolio")

from apps.api.services.pipeline import run_analysis_pipeline

try:
    print("Running pipeline...")
    res = run_analysis_pipeline('moderado', False)
    print("Success:", res.keys())
except Exception as e:
    import traceback
    traceback.print_exc()
