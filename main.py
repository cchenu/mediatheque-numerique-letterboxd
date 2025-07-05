"""Fetch and export film data from the Mediatheque numerique to a CSV file."""

import logging
import os
import re
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("import.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def load_raw_data(
    sort_by: Literal["PUBLICATION_DATE", "TITLE"],
) -> list[dict[str, Any]]:
    """
    Get all data in the Cinema category from the Mediatheque numerique.

    Returns
    -------
    list[dict[str, Any]]
        Data for each film from the Mediatheque numerique.
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
        "sortType": sort_by,
        "pageNumber": 0,
        "pageSize": 1000,
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


def create_csv(sort_by: Literal["PUBLICATION_DATE", "TITLE"]) -> pd.DataFrame:
    """Create all_films.csv with films from the Mediatheque numerique."""
    logger.info("Fetching data from the Mediatheque numerique...")
    data = load_raw_data(sort_by)
    df_films = pd.DataFrame(data)[
        [
            "id",
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

    df_films.columns = ["ID", "Title", "Directors", "Year"]

    df_films[["Title", "Directors", "Year"]] = df_films.apply(
        decompose, axis=1, result_type="expand"
    )

    df_films["ID"] = df_films["ID"].astype("Int64")
    df_films["Year"] = df_films["Year"].astype("Int64")

    df_films = df_films[
        ~df_films["Title"].str.contains(r"[sS]aison \d", regex=True)
    ]

    pattern_version = r"\-*\(*\s*(?:V|v)ersion (?:restaurée|longue|cinéma)\)*"
    df_films["Title"] = df_films["Title"].str.replace(
        pattern_version, "", regex=True
    )

    df_films["Title"] = df_films["Title"].str.replace("' ", "'").str.strip()

    df_films = df_films.drop_duplicates(subset=["Title", "Directors", "Year"])

    df_films.to_csv(Path(__file__).parent / "all_films.csv", index=False)

    logger.info("Data fetched and saved to all_films.csv")

    return df_films


def import_list(change_all: bool) -> None:
    """
    Import `temp_films_import.csv` to a letterboxd list defined in .env.

    Parameters
    ----------
    change_all : bool
        True to overwrite the letterboxd list. False to add new films on the
        letterboxd list.

    Raises
    ------
    ValueError
        Raise if credientials are not set in .env file.
    """
    driver = webdriver.Chrome()

    driver.get("https://letterboxd.com/sign-in")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "field-username"))
    )
    load_dotenv(override=True)
    username = os.getenv("LETTERBOXD_USERNAME")
    password = os.getenv("LETTERBOXD_PASSWORD")
    if username is None or password is None:
        msg = "Please set your credentials in your .env file."
        raise ValueError(msg)

    field_username = driver.find_element(By.ID, "field-username")
    field_username.send_keys(username)
    field_password = driver.find_element(By.ID, "field-password")
    field_password.send_keys(password)
    field_password.submit()

    WebDriverWait(driver, 10).until(
        EC.url_changes("https://letterboxd.com/sign-in/")
    )

    list_name = os.getenv("LETTERBOXD_LIST")
    driver.get(f"https://letterboxd.com/{username}/list/{list_name}/edit/")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "fc-cta-consent"))
    ).click()

    upload_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    upload_input.send_keys(str(Path("temp_films_import.csv").resolve()))

    WebDriverWait(driver, 2 * 60 * 60).until(
        lambda d: "import-button-disabled"
        not in (
            d.find_element(
                By.CLASS_NAME, "add-import-films-to-list"
            ).get_attribute("class")
            or ""
        )
    )

    if change_all:
        driver.find_element(
            By.CSS_SELECTOR, "label[for='replace-original'] .substitute"
        ).click()

    button_match = driver.find_element(By.CLASS_NAME, "submit-matched-films")
    driver.execute_script("arguments[0].click();", button_match)

    button_save = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "list-edit-save"))
    )
    driver.execute_script("arguments[0].click();", button_save)

    WebDriverWait(driver, 60).until(
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, "jnotify-message"), "list was saved"
        )
    )

    driver.quit()

    Path("temp_films_import.csv").unlink()


def main() -> None:
    """Create the CSV file and import it to Letterboxd."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
    except requests.ConnectionError:
        response = requests.get("https://ipinfo.io/json", timeout=5)
    data = response.json()
    if data["country"] != "FR":
        logger.warning(
            "This script must be run in France. You are currently in %s",
            data["country"],
        )
        return

    old_data = pd.read_csv(Path(__file__).parent / "all_films.csv")

    new_data_complete = create_csv("TITLE")
    while True:
        new_data_sorted = create_csv("PUBLICATION_DATE")
        if len(new_data_sorted) == len(new_data_complete):
            break

    added_films = new_data_sorted[~new_data_sorted["ID"].isin(old_data["ID"])]
    removed_films = old_data[~old_data["ID"].isin(new_data_sorted["ID"])]

    if len(added_films) == 0:
        logger.info("No new films: no import performed.")
        return

    max_deleted_films = 100
    if len(removed_films) > 0:
        change_all = True
        new_data_sorted.drop("ID", axis="columns").to_csv(
            "temp_films_import.csv", index=False
        )
        logger.info(
            "%d films have been deleted, %d new films added; the whole list "
            "will be imported.",
            len(removed_films),
            len(added_films),
        )
    elif len(removed_films) > max_deleted_films:
        logger.warning(
            "%d films have been deleted, it is suspicious. Script will stop.",
            len(removed_films),
        )
        return
    else:
        change_all = False
        added_films.drop("ID", axis="columns").to_csv(
            "temp_films_import.csv", index=False
        )
        logger.info("%d new films will be imported.", len(added_films))

    try:
        import_list(change_all)
        logger.info("List imported successfully.")
    except Exception:
        old_data.to_csv(Path(__file__).parent / "all_films.csv", index=False)
        logger.exception("An error occurred while importing the list: ")


if __name__ == "__main__":
    main()
