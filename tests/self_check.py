import asyncio
import json
import tempfile
from pathlib import Path

from handoffer.models import ProviderConfig
from handoffer.providers import status
from handoffer import config
from handoffer.handoff import create_if_needed

with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "limits.json"
    source.write_text(json.dumps({"five_hour": {"remaining_percent": 5}, "weekly": {"used_percent": 20}}))
    result = asyncio.run(status(ProviderConfig(id="test", name="Test", executable="python3", source="json_file", json_file=str(source))))
    assert result.available
    assert result.five_hour.used_percent == 95
    assert result.weekly.remaining_percent == 80
print("self-check passed")

five_hour, weekly = __import__("handoffer.providers", fromlist=["_decode"])._decode({"rateLimits": {"primary": {"usedPercent": 33, "resetsAt": 1789908543}, "secondary": {"usedPercent": 21}}})
assert five_hour.remaining_percent == 67 and weekly.remaining_percent == 79
print("codex decode check passed")

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    source = directory / "limits.json"
    source.write_text(json.dumps({"five_hour": {"used_percent": 96}, "weekly": {"used_percent": 10}}))
    config.CONFIG_PATH = directory / "config.json"
    config.CONFIG_PATH.write_text(json.dumps({"threshold_percent": 95, "providers": [{"id": "test", "name": "Test", "executable": "python3", "source": "json_file", "json_file": str(source)}]}))
    created, _ = asyncio.run(create_if_needed("test", directory, "first state"))
    assert created and (directory / "HANDOFF.md").exists()
    (directory / "HANDOFF.md").write_text("user handoff notes")
    created, _ = asyncio.run(create_if_needed("test", directory, "second state"))
    assert created and len(list(directory.glob("HANDOFF-test-*.md"))) == 1
print("handoff check passed")
