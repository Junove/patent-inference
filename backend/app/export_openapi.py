"""Write the OpenAPI contract: python -m app.export_openapi"""
import sys
from pathlib import Path

import yaml

from app.main import app

CONTRACT = Path(__file__).resolve().parents[2] / "contract" / "openapi.yaml"


def render() -> str:
    return yaml.safe_dump(app.openapi(), sort_keys=False)


if __name__ == "__main__":
    CONTRACT.write_text(render())
    print(f"wrote {CONTRACT}", file=sys.stderr)
