from typing import Optional
from time import sleep
import pandas as pd
import os
import niquests as requests
from niquests.exceptions import RequestException
from gvp.utils import fix_file


def validate_database(database: str) -> None:
    """Validate database value.

    Args:
        database (str, optional): Database name.

    Returns:
        None
    """
    assert database in (
        "holocene",
        "pleistocene",
        "changelogs",
    ), (
        f"{database} is not supported. "
        f"Please choose from {('holocene', 'pleistocene', 'changelogs')}"
    )


def get_url(database: str = "holocene") -> str:
    """Get URL to download.

    Args:
        database (str, optional): Database name. Select between "holocene" or "pleistocene". Defaults to "holocene".

    Returns:
        str: URL to download.
    """
    validate_database(database)

    if database == "pleistocene":
        return "https://volcano.si.edu/database/list_volcano_pleistocene_excel.cfm"

    if database == "changelogs":
        return "https://volcano.si.edu/gvp_votw.cfm"

    return "https://volcano.si.edu/database/list_volcano_holocene_excel.cfm"


def download(
    url: Optional[str] = None,
    output_dir: Optional[str] = None,
    database: str = "holocene",
    retries: int = 10,
    timeout: int = 3,
    fix: bool = True,
    verbose: bool = False,
) -> str:
    """Download Volcano Database.

    Args:
        url (str, optional): URL to download. Defaults to https://volcano.si.edu/database/list_volcano_holocene_excel.cfm.
        output_dir (str, optional): Directory to download to. Defaults to current directory.
        database (str, optional): Database name. Select between "holocene" or "pleistocene". Defaults to "holocene".
        retries (int, optional): Number of retries. Defaults to 10.
        timeout (int, optional): Timeout in seconds. Defaults to 3.
        fix (bool, optional): Whether to fix the file. Defaults to True.
        verbose (bool, optional): Whether to display the download progress. Defaults to False.

    Returns:
        str: Path to the downloaded file.
    """
    if database == "changelogs":
        return download_changelogs(retries=retries, timeout=timeout)

    url = url or get_url(database)

    output_dir = output_dir or os.path.join(os.getcwd(), "output")
    download_dir = os.path.join(output_dir, "download")
    os.makedirs(download_dir, exist_ok=True)

    # Attempting download file
    response = None
    attempt = 0

    if verbose:
        print(f"⌛ Downloading from: {url} ", end="")

    while attempt < retries:
        try:
            response = requests.get(url)
            if verbose:
                print("✅")
                print(f"Response: {response}")
            attempt = retries
        except RequestException as e:
            if attempt < retries:
                if verbose:
                    print(
                        f"⌛ Connection error. Attempt no {attempt + 1}. "
                        f"Retrying in {timeout} seconds..."
                    )
                sleep(timeout)
                attempt += 1
                continue
            raise ConnectionError(f"❌ Connection error: {e}")

    if (response is not None) and response.ok:
        filename = response.oheaders["content-disposition"].filename
        file_path = os.path.join(download_dir, filename)
        with open(file_path, mode="wb") as file:
            file.write(response.content)

        if fix:
            file_path = fix_file(file_path)

        return file_path

    raise ValueError(f"❌ Cannot download data: {response}")


def download_holocene(url: Optional[str] = None) -> str:
    """Download holocene database.

    Args:
        url (str, optional): URL to download. Defaults to https://volcano.si.edu/database/list_volcano_holocene_excel.cfm.

    Returns:
        str: Path to the downloaded file.
    """
    return download(url, database="holocene")


def download_pleistocene(url: Optional[str] = None) -> str:
    """Download pleistocene database.

    Args:
        url (str, optional): URL to download. Defaults to https://volcano.si.edu/database/list_volcano_pleistocene_excel.cfm.

    Returns:
        str: Path to the downloaded file.
    """
    return download(url, database="pleistocene")


def download_changelogs(
    url: Optional[str] = None,
    retries: int = 10,
    timeout: int = 3,
    verbose: bool = False,
) -> str:
    """Download changelogs database.

    Args:
        url (str, optional): URL to download. Defaults to https://volcano.si.edu/gvp_votw.cfm.
        retries (int, optional): Number of retries. Defaults to 10.
        timeout (int, optional): Timeout in seconds. Defaults to 3.
        verbose (bool, optional): Whether to display the download progress. Defaults to False.

    Returns:
        str: Path to the downloaded file.
    """
    url = url or get_url(database="changelogs")
    changelogs_dir = os.path.join(os.getcwd(), "output", "changelogs")
    os.makedirs(changelogs_dir, exist_ok=True)

    changelogs_basename = "changelogs"

    excel_filepath = None
    attempt = 0

    if verbose:
        print(f"⌛ Downloading from: {url} ", end="")

    while attempt < retries:
        try:
            dfs = pd.read_html(url)
            dfs = pd.concat(dfs)
            dfs.dropna(inplace=True)

            version = dfs.iloc[0]["Version"]
            filename_md = f"{version}_{changelogs_basename}.md"
            filename_excel = f"{version}_{changelogs_basename}.xlsx"
            excel_filepath = os.path.join(changelogs_dir, filename_excel)

            dfs.to_excel(excel_filepath, index=False)
            dfs.to_markdown(os.path.join(changelogs_dir, filename_md))

            if verbose:
                print("✅")

            attempt = retries
        except ValueError:
            if attempt < retries:
                if verbose:
                    print(
                        f"⌛ Connection error. Attempt no {attempt + 1}. "
                        f"Retrying in {timeout} seconds..."
                    )
                sleep(timeout)
                attempt += 1
                continue

    if excel_filepath is not None:
        return excel_filepath

    raise ValueError(f"❌ Cannot get changelogs from {url}")
