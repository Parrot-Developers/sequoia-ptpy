from .context import ptpy


def pytest_addoption(parser):
    parser.addoption(
        "--ideal", action="store_true",
        help="Check also for problems that are beyond ISO 15740:2013(EN)"
    )
    parser.addoption(
        "--expect-camera", action="store_true",
        help="FAIL on missing camera."
    )
