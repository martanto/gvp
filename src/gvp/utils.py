# Standard library imports
import os
import re
import pandas as pd
import xml.etree.ElementTree as ET


def extract_version(text: str) -> str | None:
    """Extract databaase version from first row.

    Args:
        text (str): The text to extract version from.

    Returns:
        str | None: The extracted version or None.
    """
    match = re.search(r"\d+(?:\.\d+)+", text)
    if match:
        version_flexible = match.group()
        return version_flexible
    return None


def xml_spreadsheet_to_dataframe(
    excel_path: str, worksheet: str = None
) -> pd.DataFrame:
    """
    Convert XML spreadsheet format to pandas DataFrame

    Args:
        excel_path: Excel spreadsheet path
        worksheet: Excel worksheet name. Default to 'Holocene Volcano List'

    Returns:
        pandas DataFrame with the spreadsheet data
    """
    worksheet_name = worksheet

    with open(excel_path, "r", encoding="utf-8") as file:
        xml_content = file.read().replace("(< ", "(&lt; ")

    root = ET.fromstring(xml_content)
    namespaces = {
        "ss": "urn:schemas-microsoft-com:office:spreadsheet",
    }

    worksheet = (
        ".//ss:Worksheet"
        if worksheet is None
        else f'.//ss:Worksheet[@ss:Name="{worksheet}"]'
    )

    # Find the worksheet and table
    worksheet = root.find(worksheet, namespaces)

    if worksheet is None:
        raise AttributeError(f'Worksheet "{worksheet_name}" not found.')

    table = worksheet.find(".//ss:Table", namespaces)
    rows = table.findall(".//ss:Row", namespaces)

    data = []
    headers = None

    for row_idx, row in enumerate(rows):
        cells = row.findall(".//ss:Cell", namespaces)
        row_data = []

        for cell in cells:
            data_elem = cell.find(".//ss:Data", namespaces)
            if data_elem is not None:
                # Get the data type and value
                data_type = data_elem.get(f'{{{namespaces["ss"]}}}Type')
                value = data_elem.text

                # Convert based on data type
                if data_type == "Number":
                    try:
                        # Try integer first, then float
                        if "." in str(value):
                            value = float(value)
                        else:
                            value = int(value)
                    except (ValueError, TypeError):
                        pass  # Keep as string if conversion fails
                elif data_type == "String":
                    value = str(value) if value is not None else ""

                row_data.append(value)
            else:
                row_data.append("")

        # Skip the first row (title row)
        if row_idx == 0:
            version = extract_version(row_data[0])
            if version is not None:
                print(f"Database version: {version}")
            continue

        # Second row contains headers
        elif row_idx == 1:
            headers = row_data

        # Data rows
        else:
            if len(row_data) > 0:
                data.append(row_data)

    # Create DataFrame
    if headers and data:
        # Ensure all rows have the same number of columns as headers
        max_cols = len(headers)
        for i, row in enumerate(data):
            if len(row) < max_cols:
                data[i].extend([""] * (max_cols - len(row)))
            elif len(row) > max_cols:
                data[i] = row[:max_cols]

        df = pd.DataFrame(data, columns=headers)
        return df
    else:
        return pd.DataFrame()


def fix_file(filepath: str) -> str:
    """Only for Windows.
    Fix broken downloaded Excel file format downloaded from GVP.

    Args:
        filepath (str): Path to the downloaded Excel file.

    Returns:
        str: Path to the downloaded Excel file.
    """
    try:
        # Third party imports
        import win32com.client as win32

        new_filename = filepath + "x"
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        workbook = excel.Workbooks.Open(filepath)
        workbook.SaveAs(new_filename, FileFormat=51)
        workbook.Close()
        excel.Application.Quit()
        os.remove(filepath)
        return new_filename
    except ImportError as e:
        print(
            f"⚠️ Cannot fix broken Excel file. Please fix it manually using MS Excel. {e}"
        )
        return filepath


def slugify(string: str, separator: str = "-") -> str:
    """Slugify a string.

    Args:
        string (str): String to slugify.
        separator (str, optional): Separator between words. Defaults to "-".

    Returns:
        str: Slugified string.
    """
    slug = string.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", separator, slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug
