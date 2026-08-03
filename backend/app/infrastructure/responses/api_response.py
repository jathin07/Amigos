from __future__ import annotations

from typing import Any

from flask import jsonify


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: dict | None = None,
    status_code: int = 200,
):
    response = {
        "success": True,
        "message": message,
    }

    if data is not None:
        response["data"] = data

    if meta:
        response["meta"] = meta

    return jsonify(response), status_code


def error_response(
    message: str,
    code: str = "ERR_BAD_REQUEST",
    errors: list[dict] | None = None,
    status_code: int = 400,
):
    response = {
        "success": False,
        "message": message,
        "code": code,
        "errors": errors
        or [
            {
                "code": code,
                "field": None,
                "message": message,
            }
        ],
    }

    return jsonify(response), status_code