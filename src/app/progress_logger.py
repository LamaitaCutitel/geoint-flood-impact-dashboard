from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import time


PROCESSING_STEPS = [
    (0, "initializare"),
    (10, "incarcare AOI"),
    (20, "cautare scene Sentinel-1"),
    (35, "creare compozite mediane"),
    (50, "change detection SAR"),
    (60, "eliminare apa permanenta"),
    (70, "calcul suprafata"),
    (80, "analiza Dynamic World"),
    (90, "generare harta"),
    (97, "raport"),
    (100, "finalizat"),
]


@dataclass
class ProgressLogger:
    entries: list[dict[str, object]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.perf_counter)

    def log(self, percent: int, message: str) -> None:
        self.entries.append(
            {
                "time": datetime.utcnow().isoformat() + "Z",
                "percent": percent,
                "message": message,
            }
        )

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        self.log(self.current_percent(), f"WARNING: {message}")

    def current_percent(self) -> int:
        if not self.entries:
            return 0
        return int(self.entries[-1]["percent"])

    def duration_seconds(self) -> float:
        return round(time.perf_counter() - self.started_at, 2)

    def as_text(self) -> str:
        lines = [
            f"{entry['percent']}% - {entry['time']} - {entry['message']}"
            for entry in self.entries
        ]
        lines.append(f"Durata totala: {self.duration_seconds()} secunde")
        return "\n".join(lines)

    def as_json(self) -> str:
        return json.dumps(
            {
                "entries": self.entries,
                "warnings": self.warnings,
                "duration_seconds": self.duration_seconds(),
            },
            indent=2,
            ensure_ascii=False,
        )


def render_progress(streamlit_module, logger: ProgressLogger) -> None:
    percent = logger.current_percent()
    streamlit_module.progress(percent / 100, text=f"{percent}%")
    if logger.entries:
        streamlit_module.info(logger.entries[-1]["message"])
    with streamlit_module.expander("Jurnal live de procesare", expanded=True):
        streamlit_module.code(logger.as_text())
        col_txt, col_json = streamlit_module.columns(2)
        col_txt.download_button(
            "Descarca jurnal TXT",
            data=logger.as_text(),
            file_name="processing_log.txt",
            mime="text/plain",
        )
        col_json.download_button(
            "Descarca jurnal JSON",
            data=logger.as_json(),
            file_name="processing_log.json",
            mime="application/json",
        )
