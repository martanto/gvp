# Global Volcanism Program (GVP)
Unofficial python package for Global Volcanism Program (GVP). Current database which is used in the package is Global Volcanism Program - Volcanoes of the World v5.3.2; 30 September 2025.

GVP Homepage: https://volcano.si.edu/

## Install

Using `pip`:
```python
pip install gvp
```

Using `uv`:
```python
uv add gvp
```

## Download Database
Available databases: holocene, pleistocene, and changelogs. Each database will be downloaded as an Excel file. The Excel files have also been fixed to prevent warnings when opened in Microsoft Excel.

### Import GVP module
```python
import gvp
from gvp.download import download

## Check GVP Module version
print(gvp.__version__)
```
`verbose` default parameter is set to `False`

### Download Holocone
```python
download(database="holocene", verbose=True)
```

### Download Pleistocene
```python
download(database="pleistocene", verbose=True)
```

### Download Changelogs in Markdown and Excel
```python
download(database="changelogs", verbose=True)
```

## Full code example
```python
import gvp
from gvp.download import download

download(database="holocene", verbose=True)
download(database="pleistocene", verbose=True)
download(database="changelogs", verbose=True)
```