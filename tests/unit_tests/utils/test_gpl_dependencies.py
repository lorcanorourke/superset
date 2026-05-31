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


def test_pyxlsb_not_in_base_requirements() -> None:
    """pyxlsb is GPL-licensed and must not appear in the base requirements."""
    base_txt = Path(__file__).parents[3] / "requirements" / "base.txt"
    content = base_txt.read_text()
    assert "pyxlsb" not in content


def test_pyxlsb_not_in_project_dependencies() -> None:
    """pyxlsb must not be listed as a direct or extra-bundled dependency."""
    pyproject = Path(__file__).parents[3] / "pyproject.toml"
    lines = pyproject.read_text().splitlines()
    non_comment_lines = [line for line in lines if not line.strip().startswith("#")]
    joined = "\n".join(non_comment_lines)
    # pandas[excel] pulls in pyxlsb; ensure we use plain pandas instead
    assert "pandas[excel]" not in joined
    assert "pyxlsb" not in joined
