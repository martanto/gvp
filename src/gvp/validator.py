from .const import COMPARATORS


def validate_comparator(comparator: str) -> bool | Exception:
    """Validating comparator.

    Args:
        comparator (str): Comparator.

    Returns:
        True or raise an Exception.
    """
    if comparator not in COMPARATORS:
        raise ValueError(
            f"⛔ Invalid comparator: {comparator}. Valid comparators are {COMPARATORS}"
        )
    return True


def validate_column_name(column_name: str, column_list: list[str]) -> bool | Exception:
    """Validating column name.

    Args:
        column_name (str): Column name.
        column_list (list): List of column names.

    Returns:
        True or raise an Exception.
    """
    if column_name not in column_list:
        raise ValueError(f"⛔ Column {column_name} is not found in {column_list}")
    return True
