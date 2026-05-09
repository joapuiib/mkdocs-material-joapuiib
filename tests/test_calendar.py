"""Tests for the calendar pymdownx Blocks extension."""
from __future__ import annotations

from datetime import date
from textwrap import dedent

import markdown
import pytest

from material_joapuiib.extensions.calendar import (
    CalendarConfig,
    CalendarError,
    DateRange,
    DayAnnotation,
    Locale,
    available_locales,
    get_locale,
    parse_calendar,
    register_locale,
)
from material_joapuiib.extensions.calendar.dates import iter_months


def render(src: str, **ext_config) -> str:
    md = markdown.Markdown(
        extensions=["material_joapuiib.extensions.calendar"],
        extension_configs={"material_joapuiib.extensions.calendar": ext_config},
    )
    return md.convert(dedent(src))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class TestParser:
    def test_minimal_config(self):
        cfg = parse_calendar("start = 2026-01-01\nend = 2026-01-31\n")
        assert cfg.start == date(2026, 1, 1)
        assert cfg.end == date(2026, 1, 31)
        assert cfg.weekends == "show"
        assert cfg.holidays == frozenset()
        assert cfg.ranges == ()

    def test_full_config(self):
        cfg = parse_calendar(
            "start = 2026-01-01\n"
            "end = 2026-02-28\n"
            'weekends = "hide"\n'
            "[holiday]\n"
            "dates = [2026-01-06, 2026-02-14]\n"
            "[[ranges]]\n"
            "from = 2026-01-10\n"
            "to = 2026-01-15\n"
            'class = "vacation"\n'
        )
        assert cfg.weekends == "hide"
        assert cfg.holidays == frozenset({date(2026, 1, 6), date(2026, 2, 14)})
        assert cfg.ranges == (
            DateRange(date(2026, 1, 10), date(2026, 1, 15), "vacation"),
        )

    def test_missing_required(self):
        with pytest.raises(CalendarError, match="missing required field 'start'"):
            parse_calendar("end = 2026-01-31\n")

    def test_invalid_toml(self):
        with pytest.raises(CalendarError, match="invalid TOML"):
            parse_calendar("start = ::not toml::")

    def test_invalid_toml_includes_line_number(self):
        # Line 3 has an unclosed string.
        bad = (
            'start = 2026-01-01\n'
            'end = 2026-01-31\n'
            'view = "unterminated\n'
        )
        with pytest.raises(CalendarError, match=r"invalid TOML at line \d+"):
            parse_calendar(bad)

    def test_end_before_start(self):
        with pytest.raises(CalendarError, match="must be on or after"):
            parse_calendar("start = 2026-02-01\nend = 2026-01-01\n")

    def test_invalid_weekends(self):
        with pytest.raises(CalendarError, match="'weekends' must be one of"):
            parse_calendar('start = 2026-01-01\nend = 2026-01-31\nweekends = "blur"\n')

    def test_dim_no_longer_valid(self):
        with pytest.raises(CalendarError, match="'weekends' must be one of"):
            parse_calendar('start = 2026-01-01\nend = 2026-01-31\nweekends = "dim"\n')

    def test_plain_weekend_mode_accepted(self):
        cfg = parse_calendar(
            'start = 2026-01-01\nend = 2026-01-31\nweekends = "plain"\n'
        )
        assert cfg.weekends == "plain"

    def test_holiday_section_plain_and_tooltip(self):
        cfg = parse_calendar(
            "start = 2026-01-01\nend = 2026-01-31\n"
            "[holiday]\n"
            "plain = true\n"
            'tooltip = "Festiu nacional"\n'
            "dates = [2026-01-06]\n"
        )
        assert cfg.holidays_plain is True
        assert cfg.holiday_tooltip == "Festiu nacional"
        assert cfg.holidays == frozenset({date(2026, 1, 6)})

    def test_holiday_section_plain_invalid(self):
        with pytest.raises(CalendarError, match="'holiday.plain' must be a boolean"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[holiday]\n"
                'plain = "yes"\n'
            )

    def test_holiday_section_tooltip_invalid(self):
        with pytest.raises(CalendarError, match="'holiday.tooltip' must be a string"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[holiday]\n"
                "tooltip = 42\n"
            )

    def test_holiday_section_unknown_field(self):
        with pytest.raises(CalendarError, match="'holiday' has unknown fields"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[holiday]\n"
                'note = "x"\n'
            )

    def test_invalid_holiday_type(self):
        with pytest.raises(CalendarError, match="must be a TOML local-date"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[holiday]\n"
                'dates = ["2026-01-06"]\n'
            )

    def test_holiday_range_pair(self):
        cfg = parse_calendar(
            "start = 2026-01-01\nend = 2026-04-30\n"
            "[holiday]\n"
            "dates = [\n"
            "  2026-01-06,\n"
            "  [2026-04-06, 2026-04-10],\n"
            "]\n"
        )
        assert date(2026, 1, 6) in cfg.holidays
        for day in range(6, 11):
            assert date(2026, 4, day) in cfg.holidays
        assert date(2026, 4, 11) not in cfg.holidays

    def test_holiday_range_inverted(self):
        with pytest.raises(CalendarError, match="must be on or after"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-12-31\n"
                "[holiday]\n"
                "dates = [[2026-04-10, 2026-04-06]]\n"
            )

    def test_holiday_range_wrong_length(self):
        with pytest.raises(CalendarError, match="exactly 2 elements"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-12-31\n"
                "[holiday]\n"
                "dates = [[2026-04-06, 2026-04-10, 2026-04-15]]\n"
            )

    def test_range_tooltip(self):
        cfg = parse_calendar(
            "start = 2026-01-01\nend = 2026-01-31\n"
            "[[ranges]]\n"
            "from = 2026-01-10\n"
            "to = 2026-01-12\n"
            'class = "vacation"\n'
            'tooltip = "Family trip"\n'
        )
        assert cfg.ranges[0].tooltip == "Family trip"

    def test_range_tooltip_invalid_type(self):
        with pytest.raises(CalendarError, match="'tooltip' must be a string"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[[ranges]]\n"
                "from = 2026-01-10\n"
                "to = 2026-01-12\n"
                'class = "vacation"\n'
                "tooltip = 42\n"
            )

    def test_day_annotation_full(self):
        cfg = parse_calendar(
            "start = 2026-01-01\nend = 2026-01-31\n"
            "[[days]]\n"
            "date = 2026-01-15\n"
            'class = "milestone"\n'
            'tooltip = "Release candidate"\n'
        )
        assert len(cfg.days) == 1
        ann = cfg.days[0]
        assert ann.day == date(2026, 1, 15)
        assert ann.css_class == "milestone"
        assert ann.tooltip == "Release candidate"

    def test_day_annotation_tooltip_only(self):
        cfg = parse_calendar(
            "start = 2026-01-01\nend = 2026-01-31\n"
            "[[days]]\n"
            "date = 2026-01-15\n"
            'tooltip = "Note"\n'
        )
        assert cfg.days[0].css_class == ""
        assert cfg.days[0].tooltip == "Note"

    def test_day_annotation_missing_date(self):
        with pytest.raises(CalendarError, match="missing field 'date'"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[[days]]\n"
                'tooltip = "x"\n'
            )

    def test_day_annotation_unknown_field(self):
        with pytest.raises(CalendarError, match="unknown fields"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[[days]]\n"
                "date = 2026-01-15\n"
                'note = "bad"\n'
            )

    def test_holiday_range_non_date(self):
        with pytest.raises(CalendarError, match="must be TOML local-dates"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-12-31\n"
                "[holiday]\n"
                'dates = [["2026-04-06", "2026-04-10"]]\n'
            )

    def test_range_missing_field(self):
        with pytest.raises(CalendarError, match="missing field 'class'"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[[ranges]]\nfrom = 2026-01-01\nto = 2026-01-05\n"
            )

    def test_range_inverted(self):
        with pytest.raises(CalendarError, match="must be on or after"):
            parse_calendar(
                "start = 2026-01-01\nend = 2026-01-31\n"
                "[[ranges]]\nfrom = 2026-01-10\nto = 2026-01-05\n"
                'class = "x"\n'
            )

    def test_datetime_rejected(self):
        with pytest.raises(CalendarError, match="must be a TOML local-date"):
            parse_calendar("start = 2026-01-01T00:00:00\nend = 2026-01-31\n")


# ---------------------------------------------------------------------------
# Config behaviour
# ---------------------------------------------------------------------------

class TestConfigBehaviour:
    def make(self, **kw) -> CalendarConfig:
        defaults = dict(start=date(2026, 1, 1), end=date(2026, 12, 31))
        defaults.update(kw)
        return CalendarConfig(**defaults)

    def test_classes_holiday(self):
        cfg = self.make(holidays=frozenset({date(2026, 1, 6)}))
        assert "holiday" in cfg.classes_for(date(2026, 1, 6))
        assert "holiday" not in cfg.classes_for(date(2026, 1, 7))

    def test_classes_weekend_show(self):
        cfg = self.make(weekends="show")
        # Saturday
        assert "weekend" in cfg.classes_for(date(2026, 1, 3))
        # Tuesday
        assert "weekend" not in cfg.classes_for(date(2026, 1, 6))

    def test_plain_skips_range_classes_on_weekends(self):
        cfg = self.make(
            weekends="plain",
            ranges=(DateRange(date(2026, 1, 1), date(2026, 1, 31), "sprint"),),
        )
        # Saturday — sprint class suppressed, weekend class present
        sat_classes = cfg.classes_for(date(2026, 1, 3))
        assert "sprint" not in sat_classes
        assert "weekend" in sat_classes
        # Tuesday — sprint class applies normally
        tue_classes = cfg.classes_for(date(2026, 1, 6))
        assert "sprint" in tue_classes

    def test_holidays_plain_skips_range_classes(self):
        cfg = self.make(
            holidays=frozenset({date(2026, 1, 6)}),
            holidays_plain=True,
            ranges=(DateRange(date(2026, 1, 1), date(2026, 1, 31), "sprint", "Sprint"),),
        )
        # Holiday day — sprint suppressed, holiday class kept
        cls = cfg.classes_for(date(2026, 1, 6))
        assert "sprint" not in cls
        assert "holiday" in cls
        assert "Sprint" not in cfg.tooltips_for(date(2026, 1, 6))
        # Non-holiday weekday — sprint applies
        assert "sprint" in cfg.classes_for(date(2026, 1, 7))

    def test_holidays_plain_off_by_default(self):
        cfg = self.make(
            holidays=frozenset({date(2026, 1, 6)}),
            ranges=(DateRange(date(2026, 1, 1), date(2026, 1, 31), "sprint"),),
        )
        # Default behaviour: sprint class still applied on holiday
        assert "sprint" in cfg.classes_for(date(2026, 1, 6))

    def test_plain_skips_range_tooltips_on_weekends(self):
        cfg = self.make(
            weekends="plain",
            ranges=(DateRange(date(2026, 1, 1), date(2026, 1, 31), "sprint", "Sprint"),),
            days=(DayAnnotation(date(2026, 1, 3), tooltip="Manual note"),),
        )
        # Saturday — range tooltip suppressed, day annotation tooltip kept.
        sat_tips = [text for _, text in cfg.tooltips_for(date(2026, 1, 3))]
        assert "Sprint" not in sat_tips
        assert "Manual note" in sat_tips
        # Tuesday — range tooltip applies.
        tue_tips = [text for _, text in cfg.tooltips_for(date(2026, 1, 6))]
        assert "Sprint" in tue_tips

    def test_classes_overlap_ranges(self):
        cfg = self.make(
            ranges=(
                DateRange(date(2026, 1, 1), date(2026, 1, 10), "a"),
                DateRange(date(2026, 1, 5), date(2026, 1, 15), "b"),
            ),
        )
        cls = cfg.classes_for(date(2026, 1, 7))
        assert "a" in cls and "b" in cls

    def test_is_visible_hide(self):
        cfg = self.make(weekends="hide")
        assert cfg.is_visible(date(2026, 1, 1))  # Thursday
        assert not cfg.is_visible(date(2026, 1, 3))  # Saturday


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

class TestLocaleRegistry:
    def test_bundled_includes_common(self):
        codes = available_locales()
        for c in ("en", "ca", "es", "fr", "de"):
            assert c in codes

    def test_normalize_variants(self):
        assert get_locale("en_US.UTF-8") is get_locale("en")
        assert get_locale("ca-ES") is get_locale("ca")

    def test_unknown_returns_none(self):
        assert get_locale("zz") is None

    def test_register_custom_locale(self):
        custom = Locale(
            code="tlh",  # Klingon — unlikely to collide with bundled or babel data
            month_names=tuple(f"M{i}" for i in range(1, 13)),
            weekday_labels=("a", "b", "c", "d", "e", "f", "g"),
        )
        register_locale(custom)
        assert get_locale("tlh") is custom


class TestDateHelpers:
    def test_iter_months_same_year(self):
        months = list(iter_months(date(2026, 1, 15), date(2026, 3, 5)))
        assert months == [(2026, 1), (2026, 2), (2026, 3)]

    def test_iter_months_year_boundary(self):
        months = list(iter_months(date(2026, 11, 1), date(2027, 2, 1)))
        assert months == [(2026, 11), (2026, 12), (2027, 1), (2027, 2)]



# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

class TestRender:
    def test_basic_month(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            ///
            """
        )
        assert 'class="md-calendar"' in html
        assert "January 2026" in html
        assert 'data-date="2026-01-01"' in html
        assert 'data-date="2026-01-31"' in html

    def test_holiday_class(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            [holiday]
            dates = [2026-01-06]
            ///
            """
        )
        assert 'class="md-calendar-day holiday" data-date="2026-01-06"' in html

    def test_range_class(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-10
            to = 2026-01-12
            class = "vacation"
            ///
            """
        )
        for d in ("2026-01-10", "2026-01-11", "2026-01-12"):
            assert f'vacation" data-date="{d}"' in html
        assert 'data-date="2026-01-13"' in html
        assert 'class="md-calendar-day vacation" data-date="2026-01-13"' not in html

    def test_range_tooltip_in_html(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-10
            to = 2026-01-12
            class = "vacation"
            tooltip = "Family trip"
            ///
            """
        )
        assert html.count('data-cal-tip="md-cal-tip-') == 3
        assert html.count('class="md-calendar-tooltip"') == 3
        assert "Family trip" in html
        # Tooltip body wraps each entry as a colour-bulleted <li>
        assert '<div class="md-calendar-tooltip-item vacation">Family trip</div>' in html

    def test_tooltip_renders_markdown(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-10
            to = 2026-01-10
            class = "vacation"
            tooltip = "Sprint **12** with [link](https://example.org)"
            ///
            """
        )
        assert "<strong>12</strong>" in html
        assert '<a href="https://example.org">link</a>' in html

    def test_day_annotation_in_html(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[days]]
            date = 2026-01-15
            class = "milestone"
            tooltip = "Release candidate"
            ///
            """
        )
        assert 'data-date="2026-01-15"' in html
        block = html.split('data-date="2026-01-15"')[0].rsplit("<div", 1)[1]
        assert "milestone" in block
        # Tooltip emitted as rich-content node + data-cal-tip on the cell
        assert "Release candidate" in html
        assert 'class="md-calendar-tooltip"' in html

    def test_day_annotation_class_combines_with_range(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-10
            to = 2026-01-20
            class = "sprint"

            [[days]]
            date = 2026-01-15
            class = "milestone"
            tooltip = "Demo"
            ///
            """
        )
        # 2026-01-15 should carry both classes
        assert 'class="md-calendar-day sprint milestone"' in html
        assert "Demo" in html
        assert 'class="md-calendar-tooltip"' in html

    def test_overlapping_tooltips_joined(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-05
            to = 2026-01-10
            class = "a"
            tooltip = "Sprint A"

            [[ranges]]
            from = 2026-01-08
            to = 2026-01-12
            class = "b"
            tooltip = "Sprint B"
            ///
            """
        )
        # 2026-01-08 covered by both ranges → both tooltip strings rendered
        # as separate <li> entries inside one tooltip popover.
        assert '<div class="md-calendar-tooltip-item a">Sprint A</div>' in html
        assert '<div class="md-calendar-tooltip-item b">Sprint B</div>' in html

    def test_overlapping_range_classes(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-05
            to = 2026-01-10
            class = "a"

            [[ranges]]
            from = 2026-01-08
            to = 2026-01-12
            class = "b"
            ///
            """
        )
        assert 'class="md-calendar-day a b" data-date="2026-01-08"' in html

    def test_weekends_show_adds_weekend_class(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            weekends = "show"
            ///
            """
        )
        # 2026-01-03 is Saturday
        assert 'class="md-calendar-day weekend" data-date="2026-01-03"' in html

    def test_weekends_hide(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            weekends = "hide"
            ///
            """
        )
        assert "md-calendar-no-weekends" in html
        assert 'data-date="2026-01-03"' not in html  # Saturday hidden
        assert 'data-date="2026-01-02"' in html  # Friday rendered
        # Weekday header drops Sat/Sun
        assert html.count('"md-calendar-weekday">Sat') == 0
        assert html.count('"md-calendar-weekday">Sun') == 0

    def test_outside_window(self):
        html = render(
            """
            /// calendar
            start = 2026-01-15
            end = 2026-01-20
            ///
            """
        )
        # 2026-01-01 is in same month but outside window.
        assert 'md-calendar-day-outside" data-date="2026-01-01"' in html
        assert 'class="md-calendar-day" data-date="2026-01-15"' in html

    def test_day_label_in_html(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[days]]
            date = 2026-01-15
            class = "purple"
            label = "M"
            tooltip = "Milestone"
            ///
            """
        )
        # Label rendered as nested span with the source class
        assert '<span class="md-calendar-day-label purple">M</span>' in html

    def test_range_label_repeats(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-12
            to = 2026-01-14
            class = "blue"
            label = "S1"
            ///
            """
        )
        # Label appears on every day of the range
        assert html.count('<span class="md-calendar-day-label blue">S1</span>') == 3

    def test_today_class(self):
        from datetime import date as _date, timedelta
        today = _date.today()
        start = today.replace(day=1)
        if today.month == 12:
            end = _date(today.year, 12, 31)
        else:
            end = _date(today.year, today.month + 1, 1) - timedelta(days=1)
        html = render(
            f"""
            /// calendar
            start = {start.isoformat()}
            end = {end.isoformat()}
            ///
            """
        )
        import re
        # Match the day cell's class list and assert `today` appears, regardless
        # of order (weekends/today/etc. can pile on for the same date).
        m = re.search(
            rf'<div class="([^"]+)" data-date="{today.isoformat()}"',
            html,
        )
        assert m, "today's cell not rendered"
        assert "today" in m.group(1).split()

    def test_tooltip_role_and_aria_describedby(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31

            [[ranges]]
            from = 2026-01-10
            to = 2026-01-10
            class = "blue"
            tooltip = "Note"
            ///
            """
        )
        assert 'role="tooltip"' in html
        # Host carries aria-describedby pointing at the tooltip id
        assert 'aria-describedby="md-cal-tip-0"' in html
        assert 'id="md-cal-tip-0"' in html

    def test_invalid_renders_error(self):
        html = render(
            """
            /// calendar
            start = 2026-02-01
            end = 2026-01-01
            ///
            """
        )
        assert "md-calendar-error" in html
        assert "must be on or after" in html

    def test_malformed_toml_renders_error(self):
        html = render(
            """
            /// calendar
            this is not toml === at all
            ///
            """
        )
        assert "md-calendar-error" in html

    def test_locale_inline(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            locale = "ca"
            ///
            """
        )
        assert "Gener 2026" in html
        assert ">Dl.</div>" in html
        assert 'lang="ca"' in html

    def test_locale_extension_default(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            ///
            """,
            locale="es",
        )
        assert "Enero 2026" in html
        assert ">Lun</div>" in html

    def test_locale_inline_overrides_default(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            locale = "fr"
            ///
            """,
            locale="es",
        )
        assert "Janvier 2026" in html

    def test_locale_unknown(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            locale = "xx"
            ///
            """
        )
        assert "md-calendar-error" in html
        assert "unsupported locale" in html

    def test_locale_inline_overrides_strings(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            locale = "ca"
            month_names = ["Gen","Feb","Mar","Abr","Mai","Jun","Jul","Ago","Set","Oct","Nov","Des"]
            weekday_labels = ["L","M","X","J","V","S","D"]
            ///
            """
        )
        assert "Gen 2026" in html
        assert ">L</div>" in html

    def test_locale_invalid_override_length(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            weekday_labels = ["L","M","X"]
            ///
            """
        )
        assert "md-calendar-error" in html
        assert "weekday_labels" in html

    def test_leading_and_trailing_padding(self):
        html = render(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            ///
            """
        )
        # 2026-01-01 is Thursday => 3 leading empty cells (Mon, Tue, Wed).
        first_block = html.split("January 2026")[1].split("</section>")[0]
        assert first_block.count("md-calendar-day-empty") >= 3


# ---------------------------------------------------------------------------
# !include directive
# ---------------------------------------------------------------------------

class TestInclude:
    def test_include_inlines_external_file(self, tmp_path):
        (tmp_path / "holidays.toml").write_text(
            "[holiday]\ndates = [2026-01-01, 2026-01-06]\n"
        )
        body = (
            "start = 2026-01-01\n"
            "end = 2026-01-31\n"
            '!include "holidays.toml"\n'
        )
        cfg = parse_calendar(body, base_path=tmp_path / "doc.md")
        assert cfg.holidays == frozenset({date(2026, 1, 1), date(2026, 1, 6)})

    def test_include_resolves_relative_to_source_file(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "ranges.toml").write_text(
            "ranges = [{from = 2026-02-02, to = 2026-02-06, class = \"blue\"}]\n"
        )
        body = (
            "start = 2026-02-01\n"
            "end = 2026-02-28\n"
            '!include "ranges.toml"\n'
        )
        cfg = parse_calendar(body, base_path=sub / "page.md")
        assert cfg.ranges and cfg.ranges[0].css_class == "blue"

    def test_include_nested(self, tmp_path):
        (tmp_path / "leaf.toml").write_text("[holiday]\ndates = [2026-03-19]\n")
        (tmp_path / "wrap.toml").write_text('!include "leaf.toml"\n')
        body = (
            "start = 2026-03-01\nend = 2026-03-31\n"
            '!include "wrap.toml"\n'
        )
        cfg = parse_calendar(body, base_path=tmp_path / "doc.md")
        assert date(2026, 3, 19) in cfg.holidays

    def test_include_cycle_detected(self, tmp_path):
        (tmp_path / "a.toml").write_text('!include "b.toml"\n')
        (tmp_path / "b.toml").write_text('!include "a.toml"\n')
        body = (
            "start = 2026-01-01\nend = 2026-01-31\n"
            '!include "a.toml"\n'
        )
        with pytest.raises(CalendarError, match="cycle"):
            parse_calendar(body, base_path=tmp_path / "doc.md")

    def test_include_missing_file(self, tmp_path):
        body = (
            "start = 2026-01-01\nend = 2026-01-31\n"
            '!include "nope.toml"\n'
        )
        with pytest.raises(CalendarError, match="!include cannot read"):
            parse_calendar(body, base_path=tmp_path / "doc.md")

    def test_include_ignored_when_not_on_own_line(self, tmp_path):
        # `!include` embedded mid-line stays as raw text and trips TOML parser
        # (we don't pretend to parse it). This documents the behaviour.
        body = (
            "start = 2026-01-01\nend = 2026-01-31\n"
            'note = "see !include \\"x.toml\\" docs"\n'
        )
        cfg = parse_calendar(body, base_path=tmp_path / "doc.md")
        # Body parses fine; note isn't a recognised field but TOML accepts it
        # and CalendarConfig builder ignores unknown root keys.
        assert cfg.start == date(2026, 1, 1)


# ---------------------------------------------------------------------------
# locale = "auto"
# ---------------------------------------------------------------------------

class TestLocaleAuto:
    def _render_with_page(self, src: str, *, page_locale: str | None, ext_locale: str = "auto") -> str:
        md = markdown.Markdown(
            extensions=["material_joapuiib.extensions.calendar"],
            extension_configs={
                "material_joapuiib.extensions.calendar": {"locale": ext_locale}
            },
        )
        if page_locale is not None:
            file_obj = type("File", (), {"locale": page_locale, "abs_src_path": None})()
            md.page = type("Page", (), {"file": file_obj})()
        return md.convert(dedent(src))

    def test_auto_picks_page_locale(self):
        html = self._render_with_page(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            ///
            """,
            page_locale="ca",
        )
        assert 'lang="ca"' in html
        assert "Gener 2026" in html

    def test_auto_falls_back_to_english_without_page(self):
        html = self._render_with_page(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            ///
            """,
            page_locale=None,
        )
        assert 'lang="en"' in html
        assert "January 2026" in html

    def test_inline_locale_overrides_auto(self):
        html = self._render_with_page(
            """
            /// calendar
            start = 2026-01-01
            end = 2026-01-31
            locale = "es"
            ///
            """,
            page_locale="ca",
        )
        assert 'lang="es"' in html
        assert "Enero 2026" in html
