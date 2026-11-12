from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_PATH = ROOT / "content" / "moodboard.json"
ARCHIVE_PATH = ROOT / "content" / "moodboard-archive.json"

current_records = json.loads(CURRENT_PATH.read_text(encoding="utf-8"))
if not isinstance(current_records, list):
    raise ValueError("content/moodboard.json must contain a list.")

if ARCHIVE_PATH.exists():
    archived_records = json.loads(ARCHIVE_PATH.read_text(encoding="utf-8"))
else:
    archived_records = []
if not isinstance(archived_records, list):
    raise ValueError("content/moodboard-archive.json must contain a list.")

known_images = {
    record.get("image")
    for record in archived_records
    if isinstance(record, dict) and record.get("image")
}
added_count = 0
added_on = datetime.now(timezone.utc).date().isoformat()

for record in current_records:
    if not isinstance(record, dict):
        continue
    sources = record.get("images")
    if not isinstance(sources, list):
        sources = [record.get("image")] if record.get("image") else []
    for source in sources:
        if isinstance(source, str):
            image_path = source.strip()
        elif isinstance(source, dict):
            image_path = str(source.get("src") or source.get("path") or "").strip()
        else:
            image_path = ""
        if not image_path or image_path in known_images:
            continue
        archived_records.append({
            "image": image_path,
            "alt": str(record.get("alt") or ""),
            "date": added_on,
        })
        known_images.add(image_path)
        added_count += 1

if added_count:
    ARCHIVE_PATH.write_text(
        json.dumps(archived_records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
print(f"Archived {added_count} new Mood Board image(s).")
