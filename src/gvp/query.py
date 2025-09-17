# Standard library imports
import functools
from typing import Literal

# Third party imports
import pandas as pd
from typing_extensions import Any, List, Self

# Project imports
from gvp.validator import validate_column_name, validate_comparator


class Query:
    def __init__(self, df: pd.DataFrame):
        """Query data

        Args:
            df (pd.DataFrame): data frame

        Attributes:
            pd.DataFrame: data frame
        """
        self.df_original: pd.DataFrame = df
        self.df: pd.DataFrame = df.copy(deep=True)
        self.columns: List[str] = df.columns.tolist()
        self.columns_selected: List[str] = []

    def refresh(self) -> Self:
        """Refresh dataframe with the original one."""
        df = self.df_original.copy(deep=True)
        self.df = df
        self.columns_selected = []
        return self

    def compare(self, column_name: str, comparator: str, value: Any) -> pd.DataFrame:
        """Translate comparator.

        Args:
            column_name (str): column name
            comparator (str): comparator
            value (Any): value

        Returns:
            pd.DataFrame: dataframe
        """
        validate_comparator(comparator)

        df = self.df.copy()

        if comparator in ["==", "like", "equal", "eq", "sama dengan"]:
            df = df[df[column_name] == value]
        if comparator in ["!=", "ne", "not equal", "tidak sama dengan"]:
            df = df[df[column_name] != value]
        if comparator in [">", "gt", "greater than", "lebih besar", "lebih besar dari"]:
            df = df[df[column_name] > value]
        if comparator in ["<", "lt", "less than", "kurang", "kurang dari"]:
            df = df[df[column_name] < value]
        if comparator in [">=", "gte", "greater than equal", "lebih besar sama dengan"]:
            df = df[df[column_name] >= value]
        if comparator in ["<=", "lte", "less than equal", "kurang dari sama dengan"]:
            df = df[df[column_name] <= value]

        self.df = pd.DataFrame(df)
        return self.df

    def count(self) -> int:
        """Count number of data

        Returns:
            int: number of data
        """
        return len(self.get())

    @functools.cache
    def select_columns(self, column_names: str | List[str] = None) -> Self:
        """Select columns

        Args:
            column_names (str | List(str)): column names

        Returns:
            self (Self)
        """
        skip_validating: bool = False

        if column_names is None:
            column_names = self.columns
            skip_validating = True

        if isinstance(column_names, str):
            column_names = [column_names]

        if not skip_validating:
            for column_name in column_names:
                validate_column_name(column_name, self.columns)

        self.columns_selected: List[str] = column_names

        return self

    @functools.cache
    def where(self, column_name: str, comparator: str, value: Any) -> Self:
        """Filter data based on column value

        Args:
            column_name (str): column name
            comparator (str): comparator
            value (Any): value

        Returns:
            self (Self)
        """
        column_list: List[str] = self.columns
        validate_column_name(column_name, column_list)

        self.df = self.compare(column_name, comparator, value)
        return self

    def unique(self, column_name: str, inplace: Literal[False] = False) -> pd.DataFrame:
        """Get ALL unique values from a column.

        Args:
            column_name (str): Column name of GVP table.
            inplace (bool, optional): Inplace current Dataframe

        Returns:
            pd.DataFrame: All unique values from a column.
        """
        assert len(self.df) > 0, ValueError("❌ DataFrame is empty")
        df = pd.DataFrame(self.df[column_name].unique(), columns=[column_name])
        df.dropna(inplace=inplace)
        return df

    def get(self, inplace: bool = True) -> pd.DataFrame:
        """Get filtered data

        Returns:
            pd.DataFrame: filtered data
        """
        if not inplace:
            df = self.df
            self.df = self.df_original.copy()
            return df

        if len(self.columns_selected) == 0:
            return self.df

        self.df = self.df[self.columns_selected]
        return self.df
