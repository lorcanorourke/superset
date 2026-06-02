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


def _get_pyproject_dependencies() -> list[str]:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["dependencies"]


def _find_requirement(name: str) -> Requirement:
    deps = _get_pyproject_dependencies()
    for dep_str in deps:
        req = Requirement(dep_str)
        if req.name == name:
            return req
    raise ValueError(f"{name!r} not found in pyproject.toml dependencies")


def test_pandas_upper_bound_compatible_with_sqlalchemy_1x() -> None:
    """pandas >=2.2 requires SQLAlchemy >=2.0 and is incompatible with SA 1.4.

    While the project pins ``sqlalchemy>=1.4, <2``, the pandas upper bound
    must stay below 2.2 to prevent a resolver from choosing a broken
    combination.  See https://github.com/pandas-dev/pandas/issues/57049.
    """
    pandas_req = _find_requirement("pandas")
    sqlalchemy_req = _find_requirement("sqlalchemy")

    # Verify SQLAlchemy is pinned to 1.x (upper bound < 2)
    sa_allows_2 = sqlalchemy_req.specifier.contains(Version("2.0.0"))
    assert not sa_allows_2, (
        f"SQLAlchemy specifier {sqlalchemy_req.specifier} allows 2.0; "
        "update this test if the project migrates to SA 2"
    )

    # Verify pandas upper bound excludes 2.2+ (the first version that
    # dropped SA 1.x support)
    pandas_allows_2_2 = pandas_req.specifier.contains(Version("2.2.0"))
    assert not pandas_allows_2_2, (
        f"pandas specifier {pandas_req.specifier} allows 2.2.0, which is "
        "incompatible with SQLAlchemy <2. Tighten the upper bound to <2.2."
    )
