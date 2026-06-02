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
from importlib.util import find_spec
from pathlib import Path


def test_pyxlsb_not_installed() -> None:
    """pyxlsb is GPL-licensed and must not be in the dependency tree."""
    assert find_spec("pyxlsb") is None


def test_pyxlsb_not_in_requirements() -> None:
    """pyxlsb must not appear as a pinned dependency in the lockfiles."""
    repo_root = Path(__file__).resolve().parents[3]
    for lockfile in ("requirements/base.txt", "requirements/development.txt"):
        contents = (repo_root / lockfile).read_text()
        assert "pyxlsb" not in contents, f"pyxlsb found in {lockfile}"


def test_excel_engines_available_without_pyxlsb() -> None:
    """openpyxl and xlsxwriter remain available for Excel I/O."""
    assert find_spec("openpyxl") is not None
    assert find_spec("xlsxwriter") is not None
