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
"""Tests that dependency version constraints in pyproject.toml are consistent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomllib
from packaging.specifiers import SpecifierSet
from packaging.version import Version


def _get_pyproject() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with open(path, "rb") as f:
        return tomllib.load(f)


def _find_dep(deps: list[str], name: str) -> str | None:
    """Return the raw dependency string for *name* from a list of PEP 508 strings."""
    for dep in deps:
        # Strip extras, e.g. "pandas[excel]>=2.1.4, <2.2" -> "pandas"
        dep_name = (
            dep.split("[")[0]
            .split(">")[0]
            .split("<")[0]
            .split("=")[0]
            .split("!")[0]
            .strip()
        )
        if dep_name.lower() == name.lower():
            return dep
    return None


def _extract_specifier(raw: str) -> SpecifierSet:
    """Extract the PEP 440 specifier set from a raw dependency string."""
    # Remove package name (with possible extras)
    # e.g. "pandas[excel]>=2.1.4, <2.2" -> ">=2.1.4, <2.2"
    for i, ch in enumerate(raw):
        if ch in (">", "<", "=", "!", "~"):
            return SpecifierSet(raw[i:])
    return SpecifierSet()


def test_pandas_upper_bound_excludes_sqlalchemy2_requirement() -> None:
    """pandas >=2.2 requires SQLAlchemy >=2.0, but we pin SQLAlchemy <2.

    Verify the pandas upper bound stays below 2.2 so the resolver cannot
    pick a pandas version that is incompatible with our SQLAlchemy pin.
    """
    pyproject = _get_pyproject()
    deps = pyproject["project"]["dependencies"]

    pandas_raw = _find_dep(deps, "pandas")
    sqla_raw = _find_dep(deps, "sqlalchemy")

    assert pandas_raw is not None, "pandas not found in project.dependencies"
    assert sqla_raw is not None, "sqlalchemy not found in project.dependencies"

    pandas_spec = _extract_specifier(pandas_raw)
    sqla_spec = _extract_specifier(sqla_raw)

    # SQLAlchemy is capped below 2.0
    assert not sqla_spec.contains(Version("2.0.0")), (
        f"SQLAlchemy specifier {sqla_spec} unexpectedly allows 2.0; "
        "if SQLAlchemy 2.0 is adopted, this test can be removed."
    )

    # pandas 2.2.0 requires SQLAlchemy >=2.0, so it must be excluded
    assert not pandas_spec.contains(Version("2.2.0")), (
        f"pandas specifier {pandas_spec} allows 2.2.0, which requires "
        "SQLAlchemy >=2.0. Cap pandas at <2.2 while SQLAlchemy <2 is in effect."
    )

    # Sanity: the range should still allow the version we actually pin
    assert pandas_spec.contains(Version("2.1.4")), (
        f"pandas specifier {pandas_spec} excludes 2.1.4, the version in base.txt"
    )
