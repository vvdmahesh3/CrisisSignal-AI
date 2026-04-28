"""
CrisisSignal AI — Application Entry Point

- Local dev:  python run.py  → starts Flask dev server on port 5000
- Production: gunicorn run:app  → Gunicorn imports `app` from this file
              (the __main__ block is never executed by Gunicorn)
"""

import os
from app import create_app

# ── Determine Environment ─────────────────────────────────────
config_name = os.getenv("FLASK_ENV", "development")

# `app` must be module-level so Gunicorn can find it via `run:app`
app = create_app(config_name)

if __name__ == "__main__":
    # Read PORT from environment (Render injects this dynamically)
    port = int(os.environ.get("PORT", 5000))

    print("\n" + "=" * 60)
    print("  => CrisisSignal AI - Starting Server")
    print(f"  => Environment: {config_name}")
    print(f"  => URL: http://localhost:{port}")
    print("=" * 60 + "\n")

    app.run(
        debug=app.config.get("DEBUG", True),
        host="0.0.0.0",
        port=port,
    )
