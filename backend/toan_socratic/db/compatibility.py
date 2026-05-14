"""Database compatibility utilities for cross-database support"""

import uuid
import json
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB as PostgresJSONB


class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL UUID when available, otherwise falls back to String.
    """

    impl = String(36)

    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return uuid.UUID(value)


class JSONB(TypeDecorator):
    """Platform-independent JSONB type.

    Uses PostgreSQL JSONB when available, otherwise falls back to JSON.
    """

    impl = String

    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresJSONB())
        else:
            return dialect.type_descriptor(String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return json.loads(value)


class Vector(TypeDecorator):
    """Platform-independent Vector type.

    Uses pgvector when available, otherwise falls back to String.
    For testing purposes, we'll store vectors as JSON strings in SQLite.
    """

    impl = String

    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from pgvector.sqlalchemy import Vector as PostgresVector
            return dialect.type_descriptor(PostgresVector(1536))
        else:
            return dialect.type_descriptor(String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        # For SQLite, store as JSON string
        return json.dumps(value.tolist() if hasattr(value, 'tolist') else list(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        # For SQLite, parse from JSON string
        return json.loads(value)