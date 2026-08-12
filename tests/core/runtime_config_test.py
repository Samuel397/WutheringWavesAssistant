from src.config.config import DailyConfig
from src.core.runtime import DailyRuntimeConfig


def test_weekly_activity_is_disabled_unless_explicitly_enabled():
    daily = DailyRuntimeConfig(DailyConfig(activityOpen=True))

    assert daily.activityOpen is True
    assert daily.activityWeeklyOpen is False


def test_weekly_activity_can_be_enabled_explicitly():
    daily = DailyRuntimeConfig(
        DailyConfig(activityOpen=True, activityWeeklyOpen=True)
    )

    assert daily.activityWeeklyOpen is True
