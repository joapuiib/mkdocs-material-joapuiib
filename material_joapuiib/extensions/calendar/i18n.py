"""Localization for the calendar extension.

Supplies localized month names and weekday labels. The implementation is
deliberately small and self-contained:

1. A registry of bundled locales covers the common cases without adding any
   runtime dependency.
2. If `babel` is installed, unknown locale codes are resolved through it.
3. Calendars may also override the strings inline via the TOML body, which
   bypasses the registry entirely.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Locale:
    """A resolved set of month names and weekday labels (Monday-first)."""

    code: str
    month_names: tuple[str, ...]  # length 12, index 0 = January
    weekday_labels: tuple[str, ...]  # length 7, Monday..Sunday

    def month_name(self, month: int) -> str:
        return self.month_names[month - 1]

    def weekday_label(self, weekday: int) -> str:
        return self.weekday_labels[weekday]


# ---------------------------------------------------------------------------
# Bundled locale registry
# ---------------------------------------------------------------------------

def _locale(
    code: str,
    months: tuple[str, ...],
    weekdays: tuple[str, ...],
) -> Locale:
    if len(months) != 12:
        raise ValueError(f"locale '{code}' must have 12 month names")
    if len(weekdays) != 7:
        raise ValueError(f"locale '{code}' must have 7 weekday labels")
    return Locale(code=code, month_names=months, weekday_labels=weekdays)


_BUNDLED: dict[str, Locale] = {
    loc.code: loc
    for loc in (
        _locale(
            "en",
            ("January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"),
            ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
        ),
        _locale(
            "ca",
            ("Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
             "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"),
            ("Dl.", "Dt.", "Dc.", "Dj.", "Dv.", "Ds.", "Dg."),
        ),
        _locale(
            "es",
            ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"),
            ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"),
        ),
        _locale(
            "fr",
            ("Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
             "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"),
            ("Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"),
        ),
        _locale(
            "de",
            ("Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"),
            ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"),
        ),
        _locale(
            "pt",
            ("Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"),
            ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"),
        ),
        _locale(
            "it",
            ("Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
             "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"),
            ("Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"),
        ),
        _locale(
            "gl",
            ("Xaneiro", "Febreiro", "Marzo", "Abril", "Maio", "Xuño",
             "Xullo", "Agosto", "Setembro", "Outubro", "Novembro", "Decembro"),
            ("Lun", "Mar", "Mér", "Xov", "Ven", "Sáb", "Dom"),
        ),
        _locale(
            "eu",
            ("Urtarrila", "Otsaila", "Martxoa", "Apirila", "Maiatza", "Ekaina",
             "Uztaila", "Abuztua", "Iraila", "Urria", "Azaroa", "Abendua"),
            ("Al.", "Ar.", "Az.", "Og.", "Or.", "Lr.", "Ig."),
        ),
    )
}


DEFAULT_LOCALE: Locale = _BUNDLED["en"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_code(code: str) -> str:
    """Normalize locale codes such as ``en_US.UTF-8`` -> ``en``."""
    base = code.replace("-", "_").split(".", 1)[0]
    return base.split("_", 1)[0].lower()


def get_locale(code: str) -> Optional[Locale]:
    """Look up a bundled locale, optionally falling back to babel."""
    if not code:
        return None

    short = normalize_code(code)
    if short in _BUNDLED:
        return _BUNDLED[short]

    return _from_babel(code)


def _from_babel(code: str) -> Optional[Locale]:
    try:
        from babel import Locale as BabelLocale  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        babel_locale = BabelLocale.parse(code.replace("-", "_"))
    except Exception:
        return None
    months = tuple(babel_locale.months["format"]["wide"][i] for i in range(1, 13))
    weekdays = tuple(babel_locale.days["format"]["abbreviated"][i] for i in range(7))
    return Locale(code=babel_locale.language, month_names=months, weekday_labels=weekdays)


def register_locale(loc: Locale) -> None:
    """Register or override a bundled locale at runtime."""
    if len(loc.month_names) != 12 or len(loc.weekday_labels) != 7:
        raise ValueError("locale must define 12 month names and 7 weekday labels")
    _BUNDLED[normalize_code(loc.code)] = loc


def available_locales() -> tuple[str, ...]:
    return tuple(sorted(_BUNDLED))
