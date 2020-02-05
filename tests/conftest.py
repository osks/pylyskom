import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-smoketests", action="store_true", default=False, help="run smoke tests against real LysKOM server"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "smoketest: mark test as smoke test")


def pytest_collection_modifyitems(config, items):
    smoke = []
    non_smoke = []
    for item in items:
        if "smoketest" in item.keywords:
            smoke.append(item)
        else:
            non_smoke.append(item)

    if config.getoption("--run-smoketests"):
        config.hook.pytest_deselected(items=non_smoke)
        items[:] = smoke
    else:
        skip_smoketest = pytest.mark.skip(reason="need --run-smoketests option to run")
        for item in smoke:
            item.add_marker(skip_smoketest)
