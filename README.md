# sailtrail

A wind-sports focused activity tracker. Takes your GPS tracks from windpowered
activities (sailing, kiting, windsurfing) and provides a wealth of information
about the session.  Currently includes speed and polar plots.

Planned features include fastest 10s, fastest 500m, fastest
alpha-500, upwind/downwind performance, tack angles, and more!

## Development

### Setup

    mkdir source
    mkdir database
    mkdir static
    git clone ssh://repo source
    cd source
    npm install
    ./node_modules/.bin/bower install

### TDD Cycle

#### Javascript

Watcher to run unit tests with summary and no details, unless a test fails.

    grunt jsdev

#### Python

Watcher to run unit tests.

    grunt pydev

Watcher to run functional tests.

    grunt funcdev

### Full Code Analysis

#### Javascript

Run eslint and all units tests with coverage. Coverage will be printed
on the console and an html report will be placed in .cover/js/{browser}/index.html

    grunt jstest

#### Python

Run flake8, pylint, and all unit tests with coverage and timing. Coverage will be printed
on the console and an html report will be placed in .cover/python/unit/index.html

    grunt pytest

Run all functional tests with coverage and timing. Coverage will be printed
on the console and an html report will be placed in .cover/python/func/index.html

    grunt functest

### Live Site Preview

Run a watcher to automatically compile and bundle CSS and JS.

    grunt dev

Run a watcher to automatically reload live server on python changes (use in
conjunction with the above task.)

    grunt runserver

### Cut New Release

For a patch release:

    grunt bump-only
    grunt conventionalChangelog
    # Verify CHANGELOG.md looks good
    grunt bump-commit

For a minor release:

    grunt bump-only:minor
    grunt conventionalChangelog
    # Verify CHANGELOG.md looks good, add release name to release
    grunt bump-commit
