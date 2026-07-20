from __future__ import annotations

from typing import Any

from flask import jsonify


def success_response(
    data: Any = None,
    meta: dict[str, Any] | None = None,
    status_code: int = 200,
):
    """
    Standard success response envelope.
    """

    response = {
        "success": True,
        "data": data,
        "meta": meta,
        "error": None,
        "validation_errors": [],
    }

    return jsonify(response), status_code


def error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
    validation_errors: list[dict[str, Any]] | None = None,
):
    """
    Standard error response envelope.
    """

    response = {
        "success": False,
        "data": None,
        "meta": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "validation_errors": validation_errors or [],
    }

    return jsonify(response), status_code