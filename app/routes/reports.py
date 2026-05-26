from fastapi import APIRouter  # type: ignore[reportMissingImports]
from fastapi import UploadFile, File  # type: ignore[reportMissingImports]
from fastapi import HTTPException # type: ignore[reportMissingImports]
from app.storage.memory_store import get_report
from app.services.report_service import create_report
from app.parser.parser_adapter import process_xml
from fastapi.responses import FileResponse
from app.services.pdf_generator import generate_pdf

router = APIRouter()

@router.post("/reports")
async def upload_report(
    file: UploadFile = File(...)
):

    content = await file.read()

    report_id = create_report(content)

    return {
        "report_id": report_id
    }


@router.get("/summary/{report_id}")
def get_summary(report_id: str):

    report = get_report(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report["summary"]



@router.get("/reports/{report_id}")
def get_report_by_id(report_id: str):

    report = get_report(report_id)

    if not report:

        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


@router.get("/report/{report_id}/pdf")
def download_pdf(report_id: str):

    report = get_report(report_id)

    if not report:

        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    pdf_path = f"{report_id}.pdf"

    generate_pdf(report, pdf_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="report.pdf"
    )