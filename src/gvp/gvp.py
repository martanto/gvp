import requests
import pandas as pd
import os
from time import sleep
from typing_extensions import Self
from .utils import fix_file, slugify


class GVP:
    """Global Volcanism Program (GVP) class."""

    _url = "https://volcano.si.edu/database/list_volcano_holocene_excel.cfm"

    def __init__(self, output_dir: str = None, verbose: bool = False):
        self.response = None

        self.output_dir = output_dir
        if output_dir is None:
            self.output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(self.output_dir, exist_ok=True)

        self.gvp_dir = os.path.join(self.output_dir, "gvp")
        os.makedirs(self.gvp_dir, exist_ok=True)

        self.download_dir = os.path.join(self.gvp_dir, "download")
        os.makedirs(self.download_dir, exist_ok=True)

        self.file: str | None = None

        self.verbose: bool = verbose

        # Private property
        self._url = GVP._url
        self.df: pd.DataFrame = pd.DataFrame()

        # Validate

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    def load_df(self, file: str = None) -> Self:
        """Load a Pandas DataFrame from a file.

        Args:
            file (str): Path to the file to load. Defaults to None.

        Returns:
            self: GVP class
        """
        if file is None:
            file = self.file

        df = pd.read_excel(file, skiprows=1)

        # Renaming column
        columns_list = df.columns.tolist()
        columns = {}
        for column in columns_list:
            columns[column] = slugify(column, "_")
        df.rename(columns=columns, inplace=True)

        # Save a new Data Frame
        writer = pd.ExcelWriter(file, engine="xlsxwriter")
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        worksheet = writer.sheets["Sheet1"]
        worksheet.autofit()
        writer.close()

        self.df = df
        return self

    def download(self, retries: int = 10, timeout: int = 3) -> Self | None:
        """Download Global Volcanism Program (GVP) database as an Excel file.

        Args:
            retries (int, optional): Number of times to retry download. Defaults to 10.
            timeout (int, optional): Timeout in seconds. Defaults to 3 seconds.

        Returns:
            str | None: Path to downloaded file.
        """
        response = self.response

        # Attempting to download file
        attempt = 0
        while attempt < retries:
            try:
                if response is None:
                    if self.verbose:
                        print(f"⌛ Downloading from: {self.url} ", end="")
                    response = requests.get(self.url)
                    if self.verbose:
                        print("✅")
                attempt = retries
            except ConnectionError as e:
                if attempt < retries:
                    if self.verbose:
                        print(
                            f"⌛ Connection error. Attempt no {attempt+1}. Retrying in {timeout} seconds..."
                        )
                    sleep(timeout)
                    attempt += 1
                    continue
                raise ConnectionError(f"❌ Connection error: {e}")

        if response.ok:
            filename = response.headers["content-disposition"].split("filename=")[1]
            file_path = os.path.join(self.download_dir, filename)

            with open(file_path, mode="wb") as file:
                file.write(response.content)

            self.file = fix_file(file_path)
            self.response = response

            if self.verbose:
                print(f"✅ Downloaded file : {self.file}")

            self.load_df(self.file)
            return self

        raise ValueError(f"❌ Response error: {response}")
