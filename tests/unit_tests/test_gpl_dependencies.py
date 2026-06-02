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
from pathlib import Path

import tomllib


def test_pyxlsb_not_in_dependencies() -> None:
    """Verify pyxlsb (GPL) is not declared as a project dependency."""
    pyproject = Path(__file__).parents[2] / "pyproject.toml"
    with open(pyproject, "rb") as f:
        config = tomllib.load(f)

    deps = config["project"]["dependencies"]
    for dep in deps:
        assert "pyxlsb" not in dep.lower(), (
            f"GPL-licensed pyxlsb found in [project.dependencies]: {dep}"
        )


def test_pyxlsb_not_in_requirements() -> None:
    """Verify pyxlsb (GPL) is absent from the pinned requirements files."""
    reqs_dir = Path(__file__).parents[2] / "requirements"
    for req_file in reqs_dir.glob("*.txt"):
        content = req_file.read_text()
        assert "pyxlsb" not in content, (
            f"GPL-licensed pyxlsb found in {req_file.name}"
        )
