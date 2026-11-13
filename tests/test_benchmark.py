import benchmark


def test_benchmark_runs_and_is_reproducible():
    a, b = benchmark.run(), benchmark.run()
    assert len(benchmark.CASES) == 33
    assert a["nre"] == b["nre"]
    assert a["raw"]["correct"] < a["nre"]["correct"]
    assert a["nre"]["wrong_answers_delivered"] == 0
