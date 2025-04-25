import pytest
from dotenv import load_dotenv

load_dotenv(".env.test")


@pytest.fixture(autouse=True)
def load_env_variables():
    load_dotenv()
