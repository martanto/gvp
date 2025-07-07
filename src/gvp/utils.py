import os, re


def fix_file(filepath: str) -> str:
    """Fix broken downloaded Excel file format downloaded from GVP.

    Args:
        filepath (str): Path to the downloaded Excel file.

    Returns:
        str: Path to the downloaded Excel file.
    """
    try:
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
        separator (str): Separator between words. Defaults to "-".

    Returns:
        str: Slugified string.
    """
    slug = string.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", separator, slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug
