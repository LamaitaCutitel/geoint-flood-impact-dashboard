from pathlib import Path


LAYOUT_SOURCE = Path("src/app/layout.py").read_text(encoding="utf-8")


def test_sidebar_uses_romanian_parameter_labels():
    assert "Prag schimbare SAR" in LAYOUT_SOURCE
    assert "Prag apa SAR" in LAYOUT_SOURCE
    assert "Raza netezire speckle" in LAYOUT_SOURCE
    assert "Numar minim pixeli conectati" in LAYOUT_SOURCE
    assert "Masca apa permanenta" in LAYOUT_SOURCE
    assert "Profil de performanta" in LAYOUT_SOURCE


def test_required_parameter_controls_have_tooltips():
    for label in [
        "Polarizare",
        "Directia orbitei",
        "Data evenimentului",
        "Prag schimbare SAR",
        "Prag apa SAR",
        "Raza netezire speckle",
        "Numar minim pixeli conectati",
        "Buffer OSM metri",
        "Limita elemente OSM",
        "Incarca layere suplimentare",
    ]:
        start = LAYOUT_SOURCE.index(label)
        snippet = LAYOUT_SOURCE[start : start + 700]
        assert "help=" in snippet, label
