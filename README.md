# sailstats

A wind-sports focused activity tracker. Takes your GPS tracks from windpowered activities (sailing, kiting, windsurfing) and provides a wealth of information about the session.  Reports cover speeds (fastest 10s, fastest 500m, faster alpha-500m), upwind/downwind performance (polars, tack angles), and more!

# Development

## Running tests

### Python

From the django/ direction:

* To produce coverage report:
    * py.test --cov-config .coveragerc --cov-report term-missing --cov-report html --cov activities activities
* To continuously run tests on changes, and only run failed tests when they occur:
    * py.test -f --instafail --lf activities/tests/test_forms.py
* To get verbose output, and sumary of slow tests:
    * py.test -v --color=yes --durations=5 activities
* To run tests in parallel:
    * py.test --durations=5 -n 2 activities
