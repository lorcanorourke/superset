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
"""Tests that declared dependency ranges in pyproject.toml are mutually
compatible.  In particular, the pandas upper bound must stay below the
first pandas release that requires sqlalchemy >= 2.0 for as long as
Superset pins sqlalchemy < 2.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version


def _parse_pyproject_dep(name: str) -> SpecifierSet:
    """Return the ``SpecifierSet`` for *name* from ``pyproject.toml``."""
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    text = pyproject.read_text()

    # Match lines like:  "pandas[excel]>=2.1.4, <2.2",
    pattern = re.compile(
        rf'^\s*"{re.escape(name)}(?:\[.*?\])?((?:[><=!~]+[\d.*]+,?\s*)+)"',
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        pytest.fail(f"Could not find dependency '{name}' in pyproject.toml")
        raise SystemExit  # unreachable; helps mypy see NoReturn
    return SpecifierSet(match.group(1).strip().rstrip(","))


# pandas 2.2.0 is the first release that requires sqlalchemy >= 2.0.
PANDAS_SQLA2_BOUNDARY = Version("2.2.0")


def test_pandas_upper_bound_excludes_sqlalchemy2_requirement() -> None:
    """The pandas range must not admit versions that require sqlalchemy >= 2.0
    while the sqlalchemy range still allows 1.x."""
    pandas_spec = _parse_pyproject_dep("pandas")
    sqla_spec = _parse_pyproject_dep("sqlalchemy")

    # Guard: only relevant while sqlalchemy 1.x is in the allowed range
    if Version("1.4.54") not in sqla_spec:
        pytest.skip("sqlalchemy range no longer includes 1.x; test not applicable")

    assert PANDAS_SQLA2_BOUNDARY not in pandas_spec, (
        f"pyproject.toml allows pandas {PANDAS_SQLA2_BOUNDARY} which requires "
        f"sqlalchemy>=2.0, but sqlalchemy is constrained to {sqla_spec}. "
        f"Tighten the pandas upper bound to <2.2."
    )
