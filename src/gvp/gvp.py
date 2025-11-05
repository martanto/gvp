# Standard library imports
import os
from functools import cached_property
from time import sleep

# Third party imports
import pandas as pd
import niquests as requests
from importlib_resources import files
from typing_extensions import Optional, Self

# Project imports
import gvp
from gvp.query import Query
from gvp.utils import fix_file, slugify


class GVP(Query):
    """Global Volcanism Program (GVP) class."""

    _url = "https://volcano.si.edu/database/list_volcano_holocene_excel.cfm"
    _database_version = "v5.3.1; 6 Aug 2025"
    _database_version_url = "https://volcano.si.edu/database/database_version.cfm"

    def __init__(self, output_dir: Optional[str] = None, verbose: bool = False):
        print(f"Current Version: {gvp.__version__}")
        print(f"Maintained by: {gvp.__author__}")

        self.output_dir = output_dir or os.path.join(os.getcwd(), "output")
        self.gvp_dir = os.path.join(self.output_dir, "gvp")
        self.download_dir = os.path.join(self.gvp_dir, "download")

        self.file: Optional[str] = None
        self.response = None
        self.verbose: bool = verbose
        self.database_version = self._database_version
        self.database_url = self._database_version_url

        print(f"GVP Database version: {self.database_version}")
        print(f"Total data: {len(self.df)}")

        # Private property
        self._url = GVP._url

        # Validate
        super().__init__(self.df)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    @cached_property
    def df(self) -> pd.DataFrame:
        return self._load_df()

    def _load_df(self) -> pd.DataFrame:
        """Initiate GVP dataframe from package.

        Returns:
            pd.DataFrame: GVP dataframe
        """
        self.file = str(files("gvp.resources").joinpath("gvp_202507041754.xlsx"))
        df = pd.read_excel(self.file)
        return df

    def load_df(self, file: Optional[str] = None) -> Self:
        """Load a Pandas DataFrame from a file.

        Args:
            file (str, optional): Path to the file to load. Defaults to None.

        Returns:
            self: GVP class
        """
        if file is None:
            file = self.file

        df = pd.read_excel(file, skiprows=1, engine="openpyxl")

        # Renaming column
        columns_list = df.columns.tolist()
        columns = {}
        for column in columns_list:
            columns[column] = slugify(str(column), "_")
        df.rename(columns=columns, inplace=True)

        # Save a new Data Frame
        writer = pd.ExcelWriter(file, engine="xlsxwriter")
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        worksheet = writer.sheets["Sheet1"]
        worksheet.autofit()
        writer.close()

        self.df = df
        return self

    def download(
        self,
        output_dir: Optional[str] = None,
        retries: int = 10,
        timeout: int = 3,
        fix: bool = False,
    ) -> Self | None:
        """Download Global Volcanism Program (GVP) database as an Excel file.

        Args:
            output_dir (str, optional): Output directory. Defaults to None.
            retries (int, optional): Number of times to retry download. Defaults to 10.
            timeout (int, optional): Timeout in seconds. Defaults to 3 seconds.
            fix (bool, optional): Fix corrupted file. Defaults to False.

        Returns:
            str | None: Path to downloaded file.
        """
        if output_dir is None:
            output_dir = self.output_dir
        download_dir = os.path.join(output_dir, self.gvp_dir, "download")
        os.makedirs(download_dir, exist_ok=True)

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
                            f"⌛ Connection error. Attempt no {attempt + 1}. Retrying in {timeout} seconds..."
                        )
                    sleep(timeout)
                    attempt += 1
                    continue
                raise ConnectionError(f"❌ Connection error: {e}")

        if response.ok:
            filename = response.headers["content-disposition"].split("filename=")[1]
            file_path = os.path.join(self.download_dir, str(filename))

            with open(file_path, mode="wb") as file:
                file.write(response.content)

            # Try to fix downloaded Excel file
            if fix:
                self.file = fix_file(file_path)
                self.load_df(self.file)

            self.response = response

            if self.verbose:
                print(f"✅ Downloaded file : {file_path}")

            return self

        raise ValueError(f"❌ Cannot download data: {response}")
