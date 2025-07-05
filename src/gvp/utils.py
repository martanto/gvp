import os, re
import win32com.client as win32


def fix_file(filepath: str) -> str:
    """Fix broken downloaded Excel file format downloaded from GVP.

    Args:
        filepath (str): Path to the downloaded Excel file.

    Returns:
        str: Path to the downloaded Excel file.
    """
    excel = win32.gencache.EnsureDispatch("Excel.Application")
    workbook = excel.Workbooks.Open(filepath)
    new_filename = filepath + "x"
    workbook.SaveAs(new_filename, FileFormat=51)
    workbook.Close()
    excel.Application.Quit()
    os.remove(filepath)
    return new_filename


def slugify(string: str, separator: str = "-") -> str:
    """Slugify a string.

    Args:
        string (str): String to slugify.
        separator (str): Separator between words. Defaults to "-".

    Returns:
        str: Slugified string.
    """
    slug = string.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", separator, slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug
