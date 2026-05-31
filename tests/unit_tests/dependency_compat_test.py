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
"""Tests that dependency version bounds in pyproject.toml remain compatible.

pandas >=2.2 requires SQLAlchemy >=2.0 for DataFrame.to_sql().  Because this
project pins SQLAlchemy <2, the pandas upper bound must stay below 2.2 to
prevent an incompatible resolution.
"""

from __future__ import annotations

from pathlib import Path

import tomllib
from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]


def _get_requirement(name: str, deps: list[str]) -> Requirement:
    """Return the Requirement whose project-name matches *name*."""
    for dep in deps:
        req = Requirement(dep)
        if req.name == name:
            return req
    raise ValueError(f"{name!r} not found in dependencies")


def test_pandas_upper_bound_compatible_with_sqlalchemy_pin() -> None:
    """pandas must be capped below 2.2 while SQLAlchemy is pinned <2.

    pandas 2.2+ requires SQLAlchemy >=2.0 for ``DataFrame.to_sql()``.
    Allowing the resolver to pick pandas >=2.2 together with SQLAlchemy 1.4
    would cause ``AttributeError: 'Engine' object has no attribute 'cursor'``
    at runtime.
    """
    pyproject = ROOT / "pyproject.toml"
    with open(pyproject, "rb") as fh:
        data = tomllib.load(fh)

    deps: list[str] = data["project"]["dependencies"]

    pandas_req = _get_requirement("pandas", deps)
    sqla_req = _get_requirement("sqlalchemy", deps)

    # SQLAlchemy is still pinned below 2.0
    sqla_allows_2 = sqla_req.specifier.contains(Version("2.0.0"))

    if not sqla_allows_2:
        # pandas 2.2.0 must NOT be installable
        assert not pandas_req.specifier.contains(Version("2.2.0")), (
            f"pandas specifier {pandas_req.specifier} allows 2.2.0, but "
            f"sqlalchemy specifier {sqla_req.specifier} excludes 2.0. "
            "pandas >=2.2 requires sqlalchemy >=2.0 for DataFrame.to_sql()."
        )
