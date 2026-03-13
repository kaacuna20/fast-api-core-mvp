from fastapi import HTTPException


# Parameter-related exceptions
class ParameterError(HTTPException):
    """Base exception for parameter-related errors"""
    pass

class ParameterNotFoundError(ParameterError):
    def __init__(self, parameter_id=None):
        message = "Parameter not found" if parameter_id is None else f"Parameter with id {parameter_id} not found"
        super().__init__(status_code=404, detail=message)


# ParameterValue-related exceptions
class ParameterValueError(ParameterError):
    """Base exception for parameter value-related errors"""
    pass


class ParameterValueNotFoundError(ParameterValueError):
    def __init__(self, value_id=None):
        message = "Parameter value not found" if value_id is None else f"Parameter value with id {value_id} not found"
        super().__init__(status_code=404, detail=message)

# ActivityLog-related exceptions
class ActivityLogError(HTTPException):
    """Base exception for activity log-related errors"""
    pass

class ActivityLogNotFoundError(ActivityLogError):
    def __init__(self, log_id=None):
        message = "Activity log not found" if log_id is None else f"Activity log with id {log_id} not found"
        super().__init__(status_code=404, detail=message)

    