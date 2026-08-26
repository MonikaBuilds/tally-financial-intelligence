from fastapi import APIRouter

from app.tally.client import TallyClient
from app.tally.service import fetch_companies

router = APIRouter()

tally_client = TallyClient()


@router.get("/status")
async def tally_status():
    result = await tally_client.check_connection()

    if result["connected"]:
        return {
            "connected": True,
            "message": "Tally is reachable",
            "url": result.get("url"),
            "status_code": result.get("status_code")
        }

    return {
        "connected": False,
        "message": "Unable to connect to Tally",
        "error": result.get("error")
    }


@router.get("/companies")
async def get_companies():
    try:
        companies = await fetch_companies()

        return {
            "success": True,
            "companies": companies
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Unable to fetch companies from Tally",
            "error": str(e)
        }