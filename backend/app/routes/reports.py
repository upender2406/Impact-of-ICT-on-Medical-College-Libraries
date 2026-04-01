from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.schemas import ReportOptions
from app.services.db_data_service import get_data_service
from app.database import get_db
from app.services.auth_service import get_current_active_user
from app.models.db_models import User
from app.utils.report_generator import get_report_generator
from typing import Optional
import json
from datetime import datetime

router = APIRouter()


@router.post("/generate")
async def generate_report(
    options: ReportOptions,
    format: str = Query("json", description="Export format: json, excel, pdf"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a report in specified format."""
    try:
        # Get data from database
        db_service = get_data_service(db)
        responses = db_service.get_all_responses()
        summary = db_service.get_summary_statistics()
        
        # Prepare report data
        report_data = {
            'reportInfo': {
                'title': options.template_id.replace('-', ' ').title(),
                'generatedAt': datetime.now().isoformat(),
                'generatedBy': current_user.email,
                'totalResponses': len(responses)
            },
            'summary': summary,
            'responses': responses
        }
        
        if format.lower() == 'excel':
            # Generate Excel report
            rg = get_report_generator()
            buffer = rg.generate_excel_report(report_data, options.template_id)
            filename = f"{options.template_id}-report-{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == 'pdf':
            # Generate PDF report
            rg = get_report_generator()
            buffer = rg.generate_pdf_report(report_data, options.template_id)
            filename = f"{options.template_id}-report-{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            # Default JSON format
            filename = f"{options.template_id}-report-{datetime.now().strftime('%Y%m%d')}.json"
            json_data = json.dumps(report_data, indent=2, default=str)
            
            return StreamingResponse(
                iter([json_data.encode()]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/templates")
async def get_report_templates(current_user: User = Depends(get_current_active_user)):
    """Get available report templates."""
    return [
        {
            'id': 'executive-summary',
            'name': 'Executive Summary',
            'description': 'High-level overview of ICT infrastructure and satisfaction metrics',
            'formats': ['json', 'excel', 'pdf']
        },
        {
            'id': 'infrastructure-analysis',
            'name': 'Infrastructure Analysis',
            'description': 'Detailed analysis of hardware, software, and connectivity infrastructure',
            'formats': ['json', 'excel', 'pdf']
        },
        {
            'id': 'satisfaction-report',
            'name': 'User Satisfaction Report',
            'description': 'Comprehensive analysis of user satisfaction and service quality',
            'formats': ['json', 'excel', 'pdf']
        },
        {
            'id': 'comparative-analysis',
            'name': 'College Comparison',
            'description': 'Side-by-side comparison of different medical colleges',
            'formats': ['json', 'excel', 'pdf']
        },
        {
            'id': 'trend-analysis',
            'name': 'Trend Analysis',
            'description': 'Time-based analysis showing trends and patterns',
            'formats': ['json', 'excel', 'pdf']
        },
        {
            'id': 'barriers-report',
            'name': 'Barriers Assessment',
            'description': 'Analysis of barriers to ICT adoption and implementation',
            'formats': ['json', 'excel', 'pdf']
        }
    ]


@router.get("/export/quick")
async def quick_export(
    format: str = Query("json", description="Export format: json, excel, pdf"),
    template: str = Query("executive-summary", description="Report template"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Quick export of data in specified format."""
    try:
        # Create quick report options
        options = ReportOptions(
            template_id=template,
            college_ids=[],
            sections=["summary", "data"],
            include_charts=True
        )
        
        # Use the generate_report function
        return await generate_report(options, format, current_user, db)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download a generated report."""
    # For now, redirect to quick export
    # In production, this would retrieve a previously generated report
    raise HTTPException(status_code=501, detail="Use /generate endpoint for report generation")
