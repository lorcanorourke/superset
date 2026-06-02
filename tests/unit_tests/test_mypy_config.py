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

import re
from pathlib import Path


def test_no_cryptography_mypy_override() -> None:
    """The cryptography mypy override was a workaround for broken type stubs in
    cryptography 44.0.3. Since the project now requires cryptography>=46.0.7,
    which ships correct stubs, the override should not be present."""
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    content = pyproject.read_text()
    pattern = re.compile(
        r'\[\[tool\.mypy\.overrides\]\]\s*\n\s*module\s*=\s*"cryptography\.\*"'
    )
    assert not pattern.search(content), (
        "Found a mypy override for 'cryptography.*' in pyproject.toml. "
        "This override is no longer needed with cryptography>=46.0.7."
    )
