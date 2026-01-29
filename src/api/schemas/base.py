"""Base pydantic models for API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    """snake_case -> camelCase (для JSON-ключей во внешнем API)."""
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() or "_" for p in parts[1:])


class ApiBaseModel(BaseModel):
    """
    Базовая модель для всех схем API:
    - JSON-ключи в camelCase (удобно фронту на TS)
    - populate_by_name=True — можно заполнять как по snake_case, так и по alias
    - from_attributes=True — поддержка ORM-объектов (.from_orm в v1)
    - extra='ignore' — игнорируем лишние поля во входящих данных
    """

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )


class ApiInputModel(BaseModel):
    """
    Базовая модель для входящих данных:
    - принимает только camelCase (populate_by_name=False)
    - запрещает лишние поля (extra='forbid')
    """

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=False,
        extra="forbid",
    )


__all__ = ["ApiBaseModel", "ApiInputModel"]
