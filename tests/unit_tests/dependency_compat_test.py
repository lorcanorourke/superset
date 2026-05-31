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
"""Tests that declared dependency ranges in pyproject.toml are mutually compatible."""

from __future__ import annotations

from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet
from packaging.version import Version


def _get_pyproject_dependencies() -> list[str]:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["dependencies"]


def _find_specifier(deps: list[str], name: str) -> SpecifierSet | None:
    for dep in deps:
        # Normalise extras syntax: "pandas[excel]>=2.1.4, <2.2" → "pandas"
        dep_name = dep.split("[")[0].split(">")[0].split("<")[0].split("=")[0]
        dep_name = dep_name.strip().lower().replace("-", "_")
        if dep_name == name.lower().replace("-", "_"):
            spec_str = dep[
                len(dep.split("[")[0].split(">")[0].split("<")[0].split("=")[0]) :
            ]
            # Strip extras bracket if present: "[excel]>=2.1.4, <2.2" → ">=2.1.4, <2.2"
            if spec_str.startswith("["):
                spec_str = spec_str.split("]", 1)[1]
            return SpecifierSet(spec_str.strip())
    return None


def test_pandas_upper_bound_compatible_with_sqlalchemy_pin() -> None:
    """pandas >=2.2 requires SQLAlchemy >=2.0 for df.to_sql() / read_sql().

    Since we pin SQLAlchemy <2, we must cap pandas <2.2 to avoid a runtime
    ``AttributeError: 'Engine' object has no attribute 'cursor'``.

    See: https://github.com/pandas-dev/pandas/pull/57049
    """
    deps = _get_pyproject_dependencies()

    sqlalchemy_spec = _find_specifier(deps, "sqlalchemy")
    pandas_spec = _find_specifier(deps, "pandas")

    assert sqlalchemy_spec is not None, (
        "sqlalchemy not found in pyproject.toml dependencies"
    )
    assert pandas_spec is not None, "pandas not found in pyproject.toml dependencies"

    # As long as SQLAlchemy is capped below 2.0, pandas must be capped below 2.2.
    sqla_allows_2 = Version("2.0.0") in sqlalchemy_spec
    pandas_allows_2_2 = Version("2.2.0") in pandas_spec

    if not sqla_allows_2:
        assert not pandas_allows_2_2, (
            f"pandas specifier {pandas_spec} allows 2.2+, but sqlalchemy specifier "
            f"{sqlalchemy_spec} excludes 2.0+. pandas >=2.2 requires sqlalchemy >=2.0 "
            "for SQL I/O (to_sql / read_sql). Cap pandas at <2.2 or upgrade sqlalchemy."
        )
