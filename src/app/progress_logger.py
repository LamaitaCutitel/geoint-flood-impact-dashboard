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

    def log(self, percent: int, message: str, status: str = "info") -> None:
        self.entries.append(
            {
                "time": datetime.utcnow().isoformat() + "Z",
                "percent": percent,
                "message": message,
                "status": status,
            }
        )

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        self.log(self.current_percent(), f"AVERTISMENT: {message}", "warning")

    def error(self, message: str) -> None:
        self.log(self.current_percent(), f"EROARE: {message}", "error")

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
    streamlit_module.subheader("Jurnal live de initializare si procesare")
    with streamlit_module.status("Stare aplicatie", expanded=True):
        streamlit_module.progress(percent / 100, text=f"{percent}%")
        if logger.entries:
            last = logger.entries[-1]
            status = last.get("status", "info")
            if status == "success":
                streamlit_module.success(last["message"])
            elif status == "warning":
                streamlit_module.warning(last["message"])
            elif status == "error":
                streamlit_module.error(last["message"])
            else:
                streamlit_module.info(last["message"])
    with streamlit_module.expander("Detalii jurnal", expanded=True):
        log_box = streamlit_module.empty()
        log_box.code(logger.as_text())
        col_txt, col_json = streamlit_module.columns(2)
        col_txt.download_button(
            "Descarca jurnalul procesarii TXT",
            data=logger.as_text(),
            file_name="processing_log.txt",
            mime="text/plain",
        )
        col_json.download_button(
            "Descarca jurnalul procesarii JSON",
            data=logger.as_json(),
            file_name="processing_log.json",
            mime="application/json",
        )


def bootstrap_startup_logger(st, county_count: int, warnings: list[str], gee_available: bool, project_configured: bool) -> ProgressLogger:
    if "startup_logger" not in st.session_state:
        logger = ProgressLogger()
        logger.log(5, "Pornire interfata Streamlit.")
        logger.log(12, "Se verifica structura proiectului.")
        logger.log(25, "Se incarca limitele administrative ale Romaniei.")
        if county_count:
            logger.log(38, f"Au fost incarcate {county_count} judete.", "success")
        else:
            logger.warn("Limitele administrative ale Romaniei nu sunt disponibile.")
        logger.log(50, "Se verifica fisierul .env.")
        if project_configured:
            logger.log(62, "Se verifica GEE_PROJECT_ID: configurat.", "success")
        else:
            logger.warn("GEE_PROJECT_ID lipseste.")
        logger.log(75, "Se verifica initializarea Google Earth Engine.")
        if gee_available:
            logger.log(82, "Google Earth Engine este initializat.", "success")
        else:
            logger.warn(
                "Google Earth Engine nu este initializat. Harta administrativa este "
                "disponibila, dar analiza SAR este dezactivata temporar."
            )
        for warning in warnings:
            logger.warn(warning)
        logger.log(92, "Harta initiala a Romaniei este pregatita.")
        logger.log(100, "Aplicatia este gata pentru selectarea judetului.", "success")
        st.session_state.startup_logger = logger
    return st.session_state.startup_logger
