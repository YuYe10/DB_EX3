"""
Validation utilities for user input and data validation.
"""
from typing import Any, Dict, List


def validate_fields(payload: Dict[str, Any], required_fields: List[str]):
    """Validate required fields in payload."""
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def validate_major_plan(data: Dict[str, Any]):
    """Validate major plan data."""
    validate_fields(data, ['major_name'])
    if not isinstance(data.get('major_name'), str) or len(data['major_name'].strip()) == 0:
        raise ValueError("major_name must be a non-empty string")
    return True


def validate_plan_course(data: Dict[str, Any]):
    """Validate major plan course data."""
    # plan_id comes from path; only validate payload fields
    validate_fields(data, ['course_id', 'semester'])
    
    if not isinstance(data.get('semester'), int) or data['semester'] < 1:
        raise ValueError("semester must be a positive integer")
    
    return True


def validate_semester(semester: Any):
    """Validate semester value."""
    try:
        sem = int(semester)
        if sem < 1:
            raise ValueError("Semester must be a positive integer")
        return sem
    except (ValueError, TypeError):
        raise ValueError("Invalid semester value")
