"""
Export API router — Excel and Word report downloads.
"""

import tempfile
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from apps.api.routers.analysis import get_last_result

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/excel")
async def export_excel():
    """Generate and download Excel report."""
    last = get_last_result()
    if not last or "_engine" not in last:
        raise HTTPException(status_code=400, detail="Run analysis first.")

    try:
        from modules.excel_export import export_to_excel
        from modules.profiles import get_profile_config

        profile = last["profile"]
        config = get_profile_config(profile)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        export_to_excel(
            profile=profile,
            filters=config["filters"],
            portfolios=last["_best_portfolios"],
            ranking=last["_ranking"],
            ahp_report=last["_engine"].get_full_report(),
            analysis=last["_consolidated"],
            filename=tmp.name,
            progress=False,
        )

        return FileResponse(
            tmp.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"AHP_Portfolio_{profile}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
