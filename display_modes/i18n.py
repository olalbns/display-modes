"""Internationalisation basée sur la locale de la session utilisateur."""
from __future__ import annotations

import gettext
from pathlib import Path

DOMAIN = "display-modes"
# /usr/share/locale est utilisé après l'installation du paquet Arch. Le chemin
# du projet permet aussi de tester une traduction compilée depuis les sources.
_LOCAL_DIRS = (Path(__file__).resolve().parent.parent / "locale", Path("/usr/share/locale"))
_translation: gettext.NullTranslations | gettext.GNUTranslations = gettext.NullTranslations()


def setup_i18n() -> None:
    """Charge la meilleure traduction disponible pour LANG/LC_MESSAGES."""
    global _translation
    _translation = gettext.NullTranslations()
    for localedir in _LOCAL_DIRS:
        candidate = gettext.translation(DOMAIN, localedir=str(localedir), fallback=True)
        if type(candidate) is not gettext.NullTranslations:
            _translation = candidate
            break


def _(message: str) -> str:
    """Traduit une chaîne au moment où elle est affichée."""
    return _translation.gettext(message)
