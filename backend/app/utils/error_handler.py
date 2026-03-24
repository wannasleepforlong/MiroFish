"""
Error handling utilities.
Provides consistent error response format, prevents sensitive info leakage in production.
"""

import traceback
from typing import Dict, Any, Optional
from flask import jsonify

from ..config import Config


def error_response(
    message: str,
    status_code: int = 500,
    include_traceback: Optional[bool] = None,
    original_error: Optional[Exception] = None
) -> tuple:
    """
    Create a unified error response.

    Only returns detailed traceback in DEBUG mode to avoid leaking sensitive info
    in production environments.

    Args:
        message: Error message
        status_code: HTTP status code
        include_traceback: Whether to include traceback (defaults to DEBUG mode setting)
        original_error: Original exception object (for getting traceback)

    Returns:
        (jsonify_response, status_code) tuple
    """
    error_data = {
        "success": False,
        "error": message
    }

    # Only include traceback in DEBUG mode
    if include_traceback is None:
        include_traceback = Config.DEBUG

    if include_traceback and original_error:
        error_data["traceback"] = traceback.format_exc()

    return jsonify(error_data), status_code


def log_error(logger, error: Exception, context: str = ""):
    """
    Log an error.

    Args:
        logger: Logger instance
        error: Exception object
        context: Context information
    """
    if context:
        logger.error(f"{context}: {str(error)}")
    else:
        logger.error(str(error))

    # Always log traceback to logs
    logger.debug(traceback.format_exc())
