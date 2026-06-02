# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype

from superset.utils.core import GenericDataType
from superset.utils.excel import apply_column_types, df_to_excel

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_timezone_conversion() -> None:
    """
    Test that columns with timezones are converted to a string.
    """
    df = pd.DataFrame({"dt": [datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc)]})
    apply_column_types(df, [GenericDataType.TEMPORAL])
    contents = df_to_excel(df)
    assert pd.read_excel(contents)["dt"][0] == "2023-01-01 00:00:00+00:00"


def test_quote_formulas() -> None:
    """
    Test that formulas are quoted in Excel.
    """
    df = pd.DataFrame({"formula": ["=SUM(A1:A2)", "normal", "@SUM(A1:A2)"]})
    contents = df_to_excel(df)
    assert pd.read_excel(contents)["formula"].tolist() == [
        "'=SUM(A1:A2)",
        "normal",
        "'@SUM(A1:A2)",
    ]


def test_column_data_types_with_one_numeric_column():
    df = pd.DataFrame(
        {
            "col0": ["123", "1", "2", "3"],
            "col1": ["456", "5.67", "0", ".45"],
            "col2": [
                datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 2, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 3, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 4, 0, 0, tzinfo=timezone.utc),
            ],
            "col3": ["True", "False", "True", "False"],
        }
    )
    coltypes: list[GenericDataType] = [
        GenericDataType.STRING,
        GenericDataType.NUMERIC,
        GenericDataType.TEMPORAL,
        GenericDataType.BOOLEAN,
    ]

    # only col1 should be converted to numeric, according to coltypes definition
    assert not is_numeric_dtype(df["col1"])
    apply_column_types(df, coltypes)
    assert not is_numeric_dtype(df["col0"])
    assert is_numeric_dtype(df["col1"])
    assert not is_numeric_dtype(df["col2"])
    assert not is_numeric_dtype(df["col3"])


def test_column_data_types_with_failing_conversion():
    df = pd.DataFrame(
        {
            "col0": ["123", "1", "2", "3"],
            "col1": ["456", "non_numeric_value", "0", ".45"],
            "col2": [
                datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 2, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 3, 0, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 4, 0, 0, tzinfo=timezone.utc),
            ],
            "col3": ["True", "False", "True", "False"],
        }
    )
    coltypes: list[GenericDataType] = [
        GenericDataType.STRING,
        GenericDataType.NUMERIC,
        GenericDataType.TEMPORAL,
        GenericDataType.BOOLEAN,
    ]

    # should not fail neither convert
    assert not is_numeric_dtype(df["col1"])
    apply_column_types(df, coltypes)
    assert not is_numeric_dtype(df["col0"])
    assert not is_numeric_dtype(df["col1"])
    assert not is_numeric_dtype(df["col2"])
    assert not is_numeric_dtype(df["col3"])


def test_column_data_types_with_large_numeric_values():
    df = pd.DataFrame(
        {
            "big_number": [
                10**14,
                999999999999999,
                10**15 + 1,
                10**16,
                1100108628127863,
                2**54,
            ],
        }
    )
    apply_column_types(df, [GenericDataType.NUMERIC])
    assert df["big_number"].tolist() == [
        100000000000000,
        999999999999999,
        "1000000000000001",
        "10000000000000000",
        "1100108628127863",
        "18014398509481984",
    ]


def test_pyxlsb_not_in_declared_dependencies() -> None:
    """Guard against re-introducing the GPL-licensed pyxlsb package.

    pyxlsb is GPL-licensed and must not be a declared dependency of
    Superset (Apache-2.0).  It previously entered the tree via
    ``pandas[excel]``; we pin plain ``pandas`` instead and list only
    the permissively-licensed Excel I/O libraries we need.
    """
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    pyproject = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())

    deps = data.get("project", {}).get("dependencies", [])
    for dep in deps:
        normalized = dep.lower().replace("-", "_").replace(" ", "")
        assert "pyxlsb" not in normalized, (
            f"pyxlsb (GPL) must not be a declared dependency: {dep}"
        )
        assert "pandas[excel]" not in dep.lower().replace(" ", ""), (
            f"pandas[excel] pulls in GPL-licensed pyxlsb: {dep}"
        )

    override_section = data.get("tool", {}).get("uv", {}).get("override", [])
    for entry in override_section:
        assert "pyxlsb" not in str(entry).lower(), (
            f"pyxlsb (GPL) found in [tool.uv.override]: {entry}"
        )
