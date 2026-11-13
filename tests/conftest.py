import json
import time

import pytest

from nre import AuthorizationPolicy, MockProvider, OmegaContextEngine


@pytest.fixture
def make_engine(tmp_path):
    def _make(**kw):
        kw.setdefault("runtime_dir", tmp_path / "rt")
        return OmegaContextEngine(**kw)
    return _make


@pytest.fixture
def audit(tmp_path):
    def _read(engine):
        return engine.storage.read_audit()
    return _read


class SlowProvider:
    name = "slow"

    def generate(self, instruction, plan):
        time.sleep(1.0)
        return {}


class BrokenProvider:
    name = "broken"

    def __init__(self, payload):
        self.payload = payload

    def generate(self, instruction, plan):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload
