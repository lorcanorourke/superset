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
"""Tests that declared dependency ranges are mutually compatible."""

from __future__ import annotations

import pathlib

from packaging.requirements import Requirement
from packaging.version import Version

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _get_pyproject_deps() -> list[Requirement]:
    """Parse dependencies from pyproject.toml [project] section."""
    # Use configparser on the TOML-compatible ini subset for the fields we need.
    # This avoids a hard dependency on a TOML library in the test suite.
    import tomllib

    with open(ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return [Requirement(dep) for dep in data["project"]["dependencies"]]


def _find_req(deps: list[Requirement], name: str) -> Requirement | None:
    for req in deps:
        if req.name == name:
            return req
    return None


def test_pandas_upper_bound_excludes_sqlalchemy2_requirement() -> None:
    """pandas >=2.2 requires SQLAlchemy >=2.0.

    The project pins SQLAlchemy <2, so the pandas upper bound must stay
    below 2.2 to prevent a resolver from picking an incompatible pair.
    See: https://github.com/pandas-dev/pandas/issues/57049
    """
    deps = _get_pyproject_deps()
    pandas_req = _find_req(deps, "pandas")
    sqlalchemy_req = _find_req(deps, "sqlalchemy")

    assert pandas_req is not None, "pandas dependency not found in pyproject.toml"
    assert sqlalchemy_req is not None, (
        "sqlalchemy dependency not found in pyproject.toml"
    )

    # pandas 2.2.0 must NOT satisfy the pandas specifier while sqlalchemy <2
    pandas_220 = Version("2.2.0")
    assert not pandas_req.specifier.contains(pandas_220), (
        f"pandas specifier {pandas_req.specifier} allows 2.2.0, which is "
        f"incompatible with the SQLAlchemy pin ({sqlalchemy_req.specifier}). "
        "pandas >=2.2 requires SQLAlchemy >=2.0."
    )

    # pandas 2.1.4 (the lock-file version) must still be allowed
    pandas_214 = Version("2.1.4")
    assert pandas_req.specifier.contains(pandas_214), (
        f"pandas specifier {pandas_req.specifier} no longer allows 2.1.4"
    )
