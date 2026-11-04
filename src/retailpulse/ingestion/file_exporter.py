import csv
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path


def build_export_filename(table_name: str, now: datetime | None = None) -> str:
    timestamp = (now or datetime.now(UTC)).strftime("%Y%m%d_%H%M%S")
    return f"{table_name}_{timestamp}.csv"


def export_rows(
    table_name: str,
    rows: Iterable[Mapping[str, object]],
    output_dir: Path,
    now: datetime | None = None,
    columns: list[str] | None = None,
) -> Path:
    """Stream dictionaries to a UTF-8 CSV without retaining all rows in memory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    iterator = iter(rows)
    path = output_dir / build_export_filename(table_name, now)

    try:
        first = next(iterator)
    except StopIteration:
        # Empty rows: write header if column list provided, otherwise handle gracefully
        fieldnames = columns if columns else []
        with path.open("w", newline="", encoding="utf-8") as file:
            if fieldnames:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
        return path

    fieldnames = columns if columns else list(first.keys())
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)
    return path
