from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
from src.services.saved_charts_service import SavedChartsService

saved_charts_router = APIRouter()
saved_charts_service = SavedChartsService()

class SaveChartRequest(BaseModel):
    chart_data: Dict[str, Any]
    title: str
    description: str = ""

class UpdateChartRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

@saved_charts_router.post("/save-chart")
def save_chart(request: SaveChartRequest):
    """Save a chart to the server"""
    try:
        result = saved_charts_service.save_chart(
            chart_data=request.chart_data,
            title=request.title,
            description=request.description
        )
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Chart saved successfully",
            "body": result
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error saving chart: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to save chart",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@saved_charts_router.get("/get-all-charts")
def get_all_charts():
    """Get all saved charts"""
    try:
        charts = saved_charts_service.get_all_charts()
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Charts retrieved successfully",
            "body": charts
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error retrieving charts: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to retrieve charts",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@saved_charts_router.get("/get-all-charts-with-data")
def get_all_charts_with_data():
    """Get all saved charts with their chart data included"""
    try:
        charts = saved_charts_service.get_all_charts_with_data()
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Charts with data retrieved successfully",
            "body": charts
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error retrieving charts with data: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to retrieve charts with data",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@saved_charts_router.get("/get-chart/{chart_id}")
def get_chart_by_id(chart_id: str):
    """Get a specific chart by ID"""
    try:
        chart = saved_charts_service.get_chart_by_id(chart_id)
        
        if not chart:
            content = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Chart not found",
                "body": {"detail": f"Chart with ID {chart_id} not found"}
            }
            return JSONResponse(
                content=content,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Chart retrieved successfully",
            "body": chart
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error retrieving chart: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to retrieve chart",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@saved_charts_router.put("/update-chart/{chart_id}")
def update_chart(chart_id: str, request: UpdateChartRequest):
    """Update chart metadata"""
    try:
        result = saved_charts_service.update_chart(
            chart_id=chart_id,
            title=request.title,
            description=request.description
        )
        
        if not result:
            content = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Chart not found",
                "body": {"detail": f"Chart with ID {chart_id} not found"}
            }
            return JSONResponse(
                content=content,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Chart updated successfully",
            "body": result
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error updating chart: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to update chart",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@saved_charts_router.delete("/delete-chart/{chart_id}")
def delete_chart(chart_id: str):
    """Delete a chart by ID"""
    try:
        success = saved_charts_service.delete_chart(chart_id)
        
        if not success:
            content = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Chart not found",
                "body": {"detail": f"Chart with ID {chart_id} not found"}
            }
            return JSONResponse(
                content=content,
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        content = {
            "status_code": status.HTTP_200_OK,
            "message": "Chart deleted successfully",
            "body": {"id": chart_id}
        }
        
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        print(f"Error deleting chart: {e}")
        content = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Failed to delete chart",
            "body": {"detail": str(e)}
        }
        return JSONResponse(
            content=content,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 