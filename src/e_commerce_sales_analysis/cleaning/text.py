"""Text standardization and cleaning utilities."""


import pandas as pd
from unidecode import unidecode


def clean_city(column: pd.Series) -> pd.Series:
    """Clean and standardize Brazilian city names.
    - Replaces accented characters with ASCII equivalents (São Paulo -> Sao Paulo)
    - Strips trailing state suffixes (- SP, /RJ)
    - Replaces hyphens and slashes with spaces (Belo-Horizonte -> Belo Horizonte)
    - Removes non-alphabetical characters and normalizes whitespace
    """
    return (
        column.apply(lambda x: unidecode(x) if isinstance(x, str) else x)
        .str.title()
        .str.replace(r"[/\-,\s]+[A-Za-z]{2}$", "", regex=True)
        .str.replace(r"[-/]", " ", regex=True)
        .str.replace(r"[^A-Za-z\s]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
