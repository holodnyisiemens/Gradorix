LEVEL_THRESHOLDS = [0, 200, 500, 900, 1400, 2000]
LEVEL_NAMES = ["Новичок", "Стажёр", "Специалист", "Профи", "Эксперт", "Мастер"]


def recalculate_level(total_points: int) -> tuple[int, str, int]:
    """Return (level, level_name, points_to_next_level) for given total_points."""
    level = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if total_points >= threshold:
            level = i
        else:
            break

    level_name = LEVEL_NAMES[level] if level < len(LEVEL_NAMES) else LEVEL_NAMES[-1]

    if level + 1 < len(LEVEL_THRESHOLDS):
        points_to_next = LEVEL_THRESHOLDS[level + 1] - total_points
    else:
        points_to_next = 0

    return level, level_name, max(0, points_to_next)
