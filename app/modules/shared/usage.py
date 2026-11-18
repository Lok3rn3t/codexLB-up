from __future__ import annotations

from sqlalchemy import Integer, and_, cast, func
from sqlalchemy.sql.elements import ColumnElement

from app.db.models import RequestLog


def token_usage_coverage_columns() -> tuple[ColumnElement, ...]:
    """Count coverage alongside an existing raw request-log aggregate scan."""
    complete = and_(RequestLog.input_tokens.is_not(None), RequestLog.output_tokens.is_not(None))
    missing = and_(
        RequestLog.input_tokens.is_(None),
        RequestLog.output_tokens.is_(None),
        RequestLog.reasoning_tokens.is_(None),
    )
    return (
        func.coalesce(func.sum(cast(complete, Integer)), 0).label("complete_requests"),
        func.coalesce(func.sum(cast(and_(~complete, ~missing), Integer)), 0).label("partial_requests"),
        func.coalesce(func.sum(cast(missing, Integer)), 0).label("missing_requests"),
    )
