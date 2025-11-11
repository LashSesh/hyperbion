#!/usr/bin/env python3
"""
Start the Hyperbion API Server
===============================

Convenience script to start the FastAPI server.
"""

import uvicorn
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperbion.api.server import app


def main():
    """Start the API server."""
    print("=" * 60)
    print("Hyperbion Tripolar Network API")
    print("=" * 60)
    print("\nStarting server on http://localhost:8000")
    print("\nEndpoints:")
    print("  - API Root:          http://localhost:8000/")
    print("  - Interactive Docs:  http://localhost:8000/docs")
    print("  - Alternative Docs:  http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
