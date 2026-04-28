"""
CrisisSignal AI — Application Entry Point
Run this file to start the development server.
"""

import os
from app import create_app
# Note: socketio.run() requires eventlet which has issues on Python 3.13
# For development, use standard Flask dev server

# ── Determine Environment ─────────────────────────────────────
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  => CrisisSignal AI - Starting Server")
    print(f"  => Environment: {config_name}")
    print(f"  => URL: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(
        debug=app.config.get("DEBUG", True),
        host="0.0.0.0",
        port=5000,
    )
