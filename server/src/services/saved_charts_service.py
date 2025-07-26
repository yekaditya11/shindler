import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class SavedChartsService:
    def __init__(self):
        self.saved_charts_dir = Path("saved_charts")
        self.saved_charts_dir.mkdir(exist_ok=True)
        self.charts_index_file = self.saved_charts_dir / "charts_index.json"
        self._ensure_index_file()

    def _ensure_index_file(self):
        """Ensure the charts index file exists"""
        if not self.charts_index_file.exists():
            self._save_index([])

    def _load_index(self) -> List[Dict[str, Any]]:
        """Load the charts index"""
        try:
            with open(self.charts_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_index(self, index: List[Dict[str, Any]]):
        """Save the charts index"""
        with open(self.charts_index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False, default=str)

    def save_chart(self, chart_data: Dict[str, Any], title: str, description: str = "") -> Dict[str, Any]:
        """Save a chart to the server"""
        timestamp = datetime.now().isoformat()
        chart_id = f"chart_{int(datetime.now().timestamp())}"
        
        # Create chart file
        chart_file = self.saved_charts_dir / f"{chart_id}.json"
        chart_info = {
            "id": chart_id,
            "title": title,
            "description": description,
            "timestamp": timestamp,
            "chart_data": chart_data
        }
        
        with open(chart_file, 'w', encoding='utf-8') as f:
            json.dump(chart_info, f, indent=2, ensure_ascii=False, default=str)

        # Update index
        index = self._load_index()
        index_entry = {
            "id": chart_id,
            "title": title,
            "description": description,
            "timestamp": timestamp,
            "filename": f"{chart_id}.json"
        }
        index.append(index_entry)
        self._save_index(index)

        return {
            "id": chart_id,
            "title": title,
            "description": description,
            "timestamp": timestamp,
            "message": "Chart saved successfully"
        }

    def get_all_charts(self) -> List[Dict[str, Any]]:
        """Get all saved charts"""
        index = self._load_index()
        return index

    def get_all_charts_with_data(self) -> List[Dict[str, Any]]:
        """Get all saved charts with their chart data included"""
        index = self._load_index()
        charts_with_data = []
        
        for chart_entry in index:
            chart_id = chart_entry["id"]
            chart_data = self.get_chart_by_id(chart_id)
            if chart_data:
                charts_with_data.append(chart_data)
        
        return charts_with_data

    def get_chart_by_id(self, chart_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chart by ID"""
        chart_file = self.saved_charts_dir / f"{chart_id}.json"
        if not chart_file.exists():
            return None
        
        try:
            with open(chart_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def delete_chart(self, chart_id: str) -> bool:
        """Delete a chart by ID"""
        chart_file = self.saved_charts_dir / f"{chart_id}.json"
        if not chart_file.exists():
            return False
        
        # Remove file
        chart_file.unlink()
        
        # Update index
        index = self._load_index()
        index = [entry for entry in index if entry["id"] != chart_id]
        self._save_index(index)
        
        return True

    def update_chart(self, chart_id: str, title: str = None, description: str = None) -> Optional[Dict[str, Any]]:
        """Update chart metadata"""
        chart_file = self.saved_charts_dir / f"{chart_id}.json"
        if not chart_file.exists():
            return None
        
        try:
            with open(chart_file, 'r', encoding='utf-8') as f:
                chart_info = json.load(f)
            
            if title is not None:
                chart_info["title"] = title
            if description is not None:
                chart_info["description"] = description
            
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_info, f, indent=2, ensure_ascii=False, default=str)
            
            # Update index
            index = self._load_index()
            for entry in index:
                if entry["id"] == chart_id:
                    if title is not None:
                        entry["title"] = title
                    if description is not None:
                        entry["description"] = description
                    break
            self._save_index(index)
            
            return chart_info
        except (FileNotFoundError, json.JSONDecodeError):
            return None 