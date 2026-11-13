"""Cada invariante I01–I10 es ejecutable y puede fallar."""

from nre import invariants as inv

GOOD_INSTR = {"objective": "x", "intent_type": "analysis", "action_class": "read_only",
              "constraints": [], "evidence": [], "normalized_input": "x", "validated": True}
TRACE = ["RECEIVED", "INTERPRETING", "VALIDATING", "AWAITING_AUTH", "EXECUTING"]


def check(i, rec):
    return inv.CHECKS[i](rec)["passed"]


def test_I01():
    assert check("I01", {"execution_requested": True, "instruction": GOOD_INSTR})
    assert not check("I01", {"execution_requested": True, "instruction": {**GOOD_INSTR, "validated": False}})
    assert not check("I01", {"execution_requested": True, "instruction": {"validated": True}})


def test_I02():
    ok = {"result": {"facts": ["a"], "inferences": ["b"]}, "verification": {"evidence_sources": ["doc"]}}
    assert check("I02", ok)
    assert not check("I02", {"result": {"facts": ["a"], "inferences": ["a"]}})
    assert not check("I02", {"result": {"facts": [], "inferences": []}, "verification": {"evidence_sources": ["model"]}})


def test_I03():
    assert check("I03", {"instruction": {**GOOD_INSTR, "evidence": [{"source": "doc", "text": "y"}]}})
    assert not check("I03", {"instruction": {**GOOD_INSTR, "evidence": [{"source": "user_input", "text": "y"}]}})
    assert not check("I03", {"instruction": {**GOOD_INSTR, "evidence": [{"source": "doc", "text": "x"}]}})


def test_I04():
    good = {"execution_requested": True, "trace": TRACE, "firewall": {"allowed": True}, "authorization": {"authorized": True}}
    assert check("I04", good)
    assert not check("I04", {**good, "authorization": {"authorized": False}})
    assert not check("I04", {**good, "firewall": {"allowed": False}})
    assert not check("I04", {**good, "trace": ["RECEIVED", "AWAITING_AUTH", "VALIDATING", "EXECUTING"]})


def test_I05():
    assert check("I05", {"trace": ["A", "B"], "audited_transitions": 2})
    assert not check("I05", {"trace": ["A", "B"], "audited_transitions": 1})


def test_I06():
    assert check("I06", {"learning": {"written": True}, "verification": {"status": "VERIFIED"}})
    assert not check("I06", {"learning": {"written": True}, "verification": {"status": "UNVERIFIED"}})


def test_I07():
    base = {"reject_streak": 3, "max_reject_streak": 3, "cycles": 0, "max_cycles": 10}
    assert check("I07", {"engine": {**base, "status": "HALTED"}})
    assert not check("I07", {"engine": {**base, "status": "READY"}})


def test_I08():
    assert check("I08", {"outcome": "COMMITTED", "verification": {"status": "UNVERIFIED"}})
    assert not check("I08", {"outcome": "COMMITTED", "verification": {}})


def test_I09():
    assert check("I09", {"verification": {"status": "VERIFIED", "external_check": True, "verifier": "ref"}})
    assert not check("I09", {"verification": {"status": "VERIFIED", "external_check": False, "verifier": None}})


def test_I10():
    assert check("I10", {"state_hash_on_disk": "a", "last_audited_state_hash": "a"})
    assert not check("I10", {"state_hash_on_disk": "a", "last_audited_state_hash": "b"})


def test_silent_mutation_detected_by_engine(make_engine):
    eng = make_engine()
    eng.process("Explica qué es una máquina de estados")
    # mutación silenciosa del archivo de estado (sin auditar)
    import json
    data = json.loads(eng.storage.state_path.read_text())
    data["cycles"] = 999
    eng.storage.state_path.write_text(json.dumps(data))
    assert eng.storage.state_hash_on_disk() != eng.storage.last_audited_state_hash()


def test_enforce_report():
    rep = inv.enforce({"trace": [], "audited_transitions": 1}, ["I05"])
    assert rep["valid"] is False and rep["failed"] == ["I05"]
    assert len(inv.fingerprint()) == 64
