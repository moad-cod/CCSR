"""Stable ASGI entry point for CCSR."""

from app.composition import create_app


app = create_app()
