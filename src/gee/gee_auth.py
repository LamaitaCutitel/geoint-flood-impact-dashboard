from __future__ import annotations

from dataclasses import dataclass

from config.settings import load_settings


AUTH_COMMANDS = [
    "copy .env.example .env",
    "Set-Content .env 'GEE_PROJECT_ID=your-google-cloud-project-id'",
    "python -m src.gee.gee_auth",
    "streamlit run app.py",
]


@dataclass
class GeeInitialization:
    available: bool
    message: str
    ee: object | None = None


def initialize_earth_engine(interactive: bool = False) -> GeeInitialization:
    settings = load_settings()
    if not settings.gee_project_id:
        return GeeInitialization(
            available=False,
            message=(
                "GEE_PROJECT_ID lipseste. Copiaza .env.example in .env si seteaza "
                "ID-ul proiectului Google Earth Engine."
            ),
        )

    try:
        import ee
    except Exception as exc:  # pragma: no cover - depends on optional package
        return GeeInitialization(
            available=False,
            message=f"earthengine-api nu este disponibil: {exc}",
        )

    try:
        ee.Initialize(project=settings.gee_project_id)
        return GeeInitialization(
            available=True,
            message="Google Earth Engine este initializat.",
            ee=ee,
        )
    except Exception as exc:
        if interactive:
            try:
                ee.Authenticate()
                ee.Initialize(project=settings.gee_project_id)
                return GeeInitialization(
                    available=True,
                    message="Autentificarea Google Earth Engine a fost finalizata.",
                    ee=ee,
                )
            except Exception as auth_exc:  # pragma: no cover - external auth
                return GeeInitialization(
                    available=False,
                    message=f"Autentificarea Earth Engine a esuat: {auth_exc}",
                )
        return GeeInitialization(
            available=False,
            message=(
                "Google Earth Engine nu este initializat pe acest PC sau VM. "
                f"Ruleaza o singura data: python -m src.gee.gee_auth. Detalii: {exc}"
            ),
        )


def main() -> None:
    result = initialize_earth_engine(interactive=True)
    print(result.message)
    if not result.available:
        print("Comenzi utile:")
        for command in AUTH_COMMANDS:
            print(f"  {command}")


if __name__ == "__main__":
    main()
