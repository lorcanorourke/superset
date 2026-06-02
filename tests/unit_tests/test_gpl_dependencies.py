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
"""Guard against GPL-licensed packages in project dependencies.

Apache 2.0 is incompatible with GPL.  This module ensures that known
GPL packages do not creep back into the declared dependency tree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[2]

GPL_BANNED_PACKAGES = {
    "pyxlsb",
}


def _read_pyproject() -> dict[str, Any]:
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def test_pyxlsb_not_in_dependencies() -> None:
    """pyxlsb is GPL-licensed and must not appear in project dependencies."""
    pyproject = _read_pyproject()
    deps = pyproject.get("project", {}).get("dependencies", [])
    dep_names = {
        d.split("[")[0]
        .split(">")[0]
        .split("<")[0]
        .split("=")[0]
        .split("!")[0]
        .strip()
        .lower()
        for d in deps
    }
    for banned in GPL_BANNED_PACKAGES:
        assert banned not in dep_names, (
            f"GPL-licensed package '{banned}' found in [project.dependencies]. "
            "Use explicit non-GPL alternatives instead."
        )


def test_pyxlsb_not_in_requirements_base() -> None:
    """pyxlsb must not appear in the pinned base requirements."""
    base_req = (REPO_ROOT / "requirements" / "base.txt").read_text()
    for banned in GPL_BANNED_PACKAGES:
        assert f"{banned}==" not in base_req, (
            f"GPL-licensed package '{banned}' found in requirements/base.txt."
        )


def test_pandas_excel_extra_not_used() -> None:
    """pandas[excel] pulls in pyxlsb (GPL);
    plain pandas + explicit deps should be used.
    """
    pyproject = _read_pyproject()
    deps = pyproject.get("project", {}).get("dependencies", [])
    for dep in deps:
        normalized = dep.lower().replace(" ", "")
        assert "pandas[excel]" not in normalized, (
            "pandas[excel] bundles pyxlsb (GPL). "
            "Use plain 'pandas' and list non-GPL Excel deps explicitly."
        )
