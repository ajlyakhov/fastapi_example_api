# Run tests

## Unit tests

Unit & integration tests implemented using pytest. Run it from the porject root:
```
pytest -v
```

There are two groups of tests:

1. Unit tests

**test_tracking.py** - check the main buisness logic of track api with mocked database and weather service.

2. Integration tests

**test_weatherbit_provider.py** - check the weather service internal logic, mock only network request to weatherbit api.

Expected report:

```
tests/test_tracking.py::test_track_shipment_success PASSED
tests/test_tracking.py::test_track_shipment_not_found PASSED
tests/test_tracking.py::test_database_exception PASSED
tests/test_tracking.py::test_weather_exception PASSED
tests/test_weatherbit_provider.py::test_parse_address_success PASSED
tests/test_weatherbit_provider.py::test_parse_address_invalid_format PASSED
tests/test_weatherbit_provider.py::test_get_weather_success PASSED
tests/test_weatherbit_provider.py::test_get_weather_no_data PASSED
tests/test_weatherbit_provider.py::test_get_weather_api_failure PASSED
```

## Code coverage

To run code coverage report use this command:
```
pytest --cov=.
```

Current report:

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/api/__init__.py                     0      0   100%
app/api/models.py                      27      0   100%
app/api/tracking.py                    35      0   100%
app/conf/__init__.py                    0      0   100%
app/conf/logging.py                    53     12    77%
app/conf/settings.py                   20      1    95%
app/db/__init__.py                      0      0   100%
app/db/base.py                          6      1    83%
app/db/dynamodb.py                     38     18    53%
app/db/factory.py                       9      1    89%
app/integrations/__init__.py            0      0   100%
app/integrations/cache.py              26      8    69%
app/integrations/weather.py            59      5    92%
app/main.py                             9      0   100%
tests/conftest.py                       6      0   100%
tests/test_tracking.py                 53      0   100%
tests/test_weatherbit_provider.py      45      0   100%
-------------------------------------------------------
TOTAL                                 386     46    88%
```
