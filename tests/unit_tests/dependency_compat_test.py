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
from __future__ import annotations

from pathlib import Path

import tomllib
from packaging.requirements import Requirement
from packaging.version import Version

_PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"


def _get_dependencies() -> list[str]:
    with open(_PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    project = data["project"]
    assert isinstance(project, dict)
    deps = project["dependencies"]
    assert isinstance(deps, list)
    return deps


def _find_req(name: str, deps: list[str]) -> Requirement:
    for dep in deps:
        req = Requirement(dep)
        if req.name == name:
            return req
    raise AssertionError(f"{name} not found in dependencies")


def test_pandas_upper_bound_compatible_with_sqlalchemy_pin() -> None:
    """pandas >=2.2 requires sqlalchemy >=2.0.

    While sqlalchemy is capped at <2, pandas must stay below 2.2 so that
    a resolver cannot pick an incompatible combination.
    """
    deps = _get_dependencies()

    pandas_req = _find_req("pandas", deps)
    sqla_req = _find_req("sqlalchemy", deps)

    # Determine the pandas upper-bound from its specifiers
    pandas_upper: Version | None = None
    for spec in pandas_req.specifier:
        if spec.operator in ("<", "<="):
            pandas_upper = Version(spec.version)
            break

    assert pandas_upper is not None, "pandas must have an upper-bound specifier"

    # Determine the sqlalchemy upper-bound
    sqla_upper: Version | None = None
    for spec in sqla_req.specifier:
        if spec.operator in ("<", "<="):
            sqla_upper = Version(spec.version)
            break

    assert sqla_upper is not None, "sqlalchemy must have an upper-bound specifier"

    # If sqlalchemy is capped below 2.0, pandas must be capped below 2.2
    if sqla_upper <= Version("2.0"):
        assert pandas_upper <= Version("2.2"), (
            f"pandas upper bound ({pandas_upper}) is too high for "
            f"sqlalchemy <{sqla_upper}. pandas >=2.2 requires sqlalchemy >=2.0. "
            f"Cap pandas at <2.2 or upgrade sqlalchemy."
        )
