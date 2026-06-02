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
"""
Guard against GPL-licensed packages being added to the dependency tree.

Apache-licensed projects cannot distribute GPL-licensed dependencies.
This test fails if any known GPL package appears in pyproject.toml or
the pinned requirements files, preventing accidental re-introduction.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Packages that must never appear as dependencies due to GPL licensing.
GPL_BLOCKED_PACKAGES: set[str] = {
    "pyxlsb",
}


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text()


def test_pyproject_toml_excludes_gpl_packages() -> None:
    """pyproject.toml must not declare any GPL-blocked dependency."""
    content = _read_text("pyproject.toml")
    for pkg in GPL_BLOCKED_PACKAGES:
        assert pkg not in content, (
            f"GPL-licensed package '{pkg}' found in pyproject.toml. "
            f"Remove it to comply with the Apache-2.0 license."
        )


@pytest.mark.parametrize(
    "req_file",
    [
        "requirements/base.txt",
        "requirements/development.txt",
    ],
)
def test_requirements_exclude_gpl_packages(req_file: str) -> None:
    """Pinned requirements files must not contain GPL-blocked packages."""
    content = _read_text(req_file)
    for pkg in GPL_BLOCKED_PACKAGES:
        assert pkg not in content, (
            f"GPL-licensed package '{pkg}' found in {req_file}. "
            f"Remove it to comply with the Apache-2.0 license."
        )
