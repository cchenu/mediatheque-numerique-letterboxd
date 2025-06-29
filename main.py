"""Fetch and export film data from the Médiathèque numérique to a CSV file."""

import re
from typing import Any

import pandas as pd
import requests


def load_data() -> list[dict[str, Any]]:
    """
    Get all data in the Cinéma category from the Médiathèque numérique.

    Returns
    -------
    list[dict[str, Any]]
        Data for each film from the Médiathèque numérique.

    """
    url = "https://vod.mediatheque-numerique.com/api/proxy/api/product/search"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload: dict[str, Any] = {
        "withAggregations": True,
        "includedProductCategoriesUuids": [
            "5fcf8750-bada-442c-84b4-fe05b949fba2"
        ],
        "sortType": "PUBLICATION_DATE",
        "pageNumber": 0,
    }

    data: list[dict[str, Any]] = []

    response = requests.post(url, headers=headers, json=payload, timeout=5)

    code_success = 200
    while response.status_code == code_success:
        data.extend(response.json()["content"]["products"]["content"])
        payload["pageNumber"] += 1
        response = requests.post(url, headers=headers, json=payload, timeout=5)
    return data


def decompose(row: pd.Series) -> tuple[str, str, int | None]:
    """
    Decompose Title into Title, Directors, and Year when applicable.

    Parameters
    ----------
    row : pd.Series
        Series with Title, Directors and Year.

    Returns
    -------
    tuple[str, str, int | None]
        New data for Title, Directors and Year.

    """
    if not pd.isna(row["Year"]):
        if isinstance(row["Directors"], list):
            return (row["Title"], ",".join(row["Directors"]), row["Year"])
        return (row["Title"], "", row["Year"])
    title = row["Title"]
    pattern = r"\"(.*?)\" d(?:'|e )(.*?) \((\d*)\)"
    result = re.findall(pattern, title)
    if result:
        return (result[0][0], result[0][1], int(result[0][2]))
    pattern2 = r"\"(.*?)\" de "
    result = re.findall(pattern2, title)
    if result:
        return (result[0], "", None)
    return (title, "", None)


def create_csv() -> None:
    """Create all_films.csv with films from the Médiathèque numérique."""
    data = load_data()
    df_films = pd.DataFrame(data)[
        [
            "title",
            "directors",
            "productionYear",
            "productType",
            "seasonsCount",
            "duration",
        ]
    ]
    df_films = df_films[df_films["productType"] == "PROGRAM"].drop(
        "productType", axis="columns"
    )

    df_films = df_films[df_films["seasonsCount"] == 0].drop(
        "seasonsCount", axis="columns"
    )

    duration_mini = 3000
    df_films = df_films[df_films["duration"] > duration_mini].drop(
        "duration", axis="columns"
    )

    df_films.columns = ["Title", "Directors", "Year"]

    df_films[["Title", "Directors", "Year"]] = df_films.apply(
        decompose, axis=1, result_type="expand"
    )

    df_films["Year"] = df_films["Year"].astype("Int64")

    df_films = df_films[
        ~df_films["Title"].str.contains(r"[sS]aison \d", regex=True)
    ]

    pattern_version = r"\-*\(*\s*(?:V|v)ersion (?:restaurée|longue|cinéma)\)*"
    df_films["Title"] = df_films["Title"].str.replace(
        pattern_version, "", regex=True
    )

    df_films["Title"] = df_films["Title"].str.replace("' ", "'").str.strip()

    df_films = df_films.drop_duplicates()

    df_films.to_csv("all_films.csv", index=False)


if __name__ == "__main__":
    create_csv()
