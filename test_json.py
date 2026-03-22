import sys
import os
import json

sys.path.append(r"C:\Users\jcarl\OneDrive\Escritorio\ahp_portfolio")

from apps.api.services.pipeline import run_analysis_pipeline
from fastapi.encoders import jsonable_encoder

try:
    print("Running pipeline...")
    res = run_analysis_pipeline('moderado', False)
    
    response = {k: v for k, v in res.items() if not k.startswith("_")}
    
    # Try encode
    encoded = jsonable_encoder(response)
    print("Encoder passed")
    
    # Try json dump
    jsonstr = json.dumps(encoded)
    print("JSON passed")
    
except Exception as e:
    import traceback
    traceback.print_exc()
