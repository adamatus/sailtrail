# sailtrail

A wind-sports focused activity tracker. Takes your GPS tracks from windpowered
activities (sailing, kiting, windsurfing) and provides a wealth of information
about the session.  Currently includes speed and polar plots.

Planned features include fastest 10s, fastest 500m, fastest alpha-500, upwind/downwind performance, tack angles, and more!

## Development

### Setup

The recommended setup relies on pyenv (and pyenv-virtualenv), brew, and npm.  From a new base
project directory (e.g., sailtrail), use the following to begin development.

    mkdir database
    mkdir static
    pyenv install 3.4.3
    pyenv virtualenv 3.4.3 sailtrail
    pyenv local sailtrail
    git clone ssh://repo source
    cd source
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    npm install
    brew install chromedriver
    ./node_modules/.bin/bower install

Test the installation by running the following:

    grunt test

If functional tests fail because something else is using the default port, use the following to
provide a range for the test runner to try:

    export DJANGO_LIVE_TEST_SERVER_ADDRESS="localhost:8000-8010,8080,9200-9300"

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

Run all integration tests with coverage and timing. Coverage will be printed
on the console and an html report will be placed in .cover/python/int/index.html

    grunt inttest

Run all functional tests with coverage and timing. Coverage will be printed
on the console and an html report will be placed in .cover/python/func/index.html

    grunt functest

### Live Site Preview

Run a watcher to automatically compile and bundle CSS and JS, and start a
livereload server to monitor changes to any of those files.


    grunt dev

Run a watcher to automatically restart the django development server on
any python changes, then (in conjunction with the above task) reload the
browser via a livereload call.

    ./django/manage.py runserver 8000

### Cut New Release

For a patch release:

    grunt bump-only
    grunt changelog
    # Verify CHANGELOG.md looks good
    grunt bump-commit

For a minor release:

    grunt bump-only:minor
    grunt changelog
    # Verify CHANGELOG.md looks good, add release name to release
    grunt bump-commit

## Deploy

Log in to instance via SSH.

Go to site directory (and activate virtualenv):

    cd /home/ubuntu/sites/www.sailtrail.net/source
    source ../virtualenv/bin/activate

Stash the temporary settings change, pull changes, apply stashed change,
and push a new tag to indicate what code in is prod:

    git stash
    git pull
    git stash apply
    git tag -f prod
    git push -f origin prod

Were there DB changes?

    ./django/manage.py migrate

Were the Javascript/CSS changs?

    grunt browserify
    grunt sass
    ./django/maange.py collectstatic

Restart the server

    sudo restart gunicorn

### New Deploy

Starting from a clean checkout (assuming up-to-date node on host):

    cd /home/ubuntu/sites/www.sailtrail.net
    rm -rf virtualenv/
    virtualenv -p python3.5 virtualenv
    source virtualenv/bin/activate
    cd source
    pip install --upgrade pip
    pip install -r requirements.txt
    npm install
    ./node_modules/.bin/bower install
    ./node_modules/.bin/grunt sass
    ./node_modules/.bin/grunt browserify
    python django/manage.py collectstatic
    python django/manage.py migrate
    sudo start gunicorn-www.sailtrail.net

## Fixing Borked DB

Log in to instance and get django shell running in virtual env:

    cd /home/ubuntu/sites/www.sailtrail.net
    source virtualenv/bin/activate
    cd source/django
    ./manage shell

From virtual env:

    from api.models import Activity
    Activity.objects.all()
    a = Activity.objects.first()
    [ ... etc ... ]
    a.delete()
