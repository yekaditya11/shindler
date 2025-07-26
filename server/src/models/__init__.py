# Import all models to ensure they are registered with SQLAlchemy
from .unsafe_event_models import (
    UnsafeEventEITech,
    UnsafeEventSRS,
    UnsafeEventNITCT,
    UnsafeEventNITCTAugmented
)
from .base_models import BaseModel, UploadLog
from .upload_data_versioning import VersionByMonth
from .data_health_models import DataHealthHistory, DataQualityAlert

# Make models available at package level
__all__ = [
    'UnsafeEventEITech',
    'UnsafeEventSRS',
    'UnsafeEventNITCT',
    'UnsafeEventNITCTAugmented',
    'BaseModel',
    'UploadLog',
    'VersionByMonth',
    'DataHealthHistory',
    'DataQualityAlert'
]
