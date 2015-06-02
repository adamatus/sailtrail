from fabric.contrib.files import append, comment, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'git@github.com:adamatus/sailtrail.git'


def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _node_setup(source_folder)
    _bower_setup(source_folder)
    _update_settings(source_folder, env.host)
    _update_configs(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _node_setup(source_folder):
    run('cd %s; npm install' % source_folder)


def _bower_setup(source_folder):
    run('cd %s; ./node_modules/.bin/bower install' % source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('virtualenv', 'source', 'database'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/django/sailtrail/settings/'
    secret_key_file = settings_path + 'secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))

    settings_file = settings_path + '__init__.py'
    comment(settings_file, r'from')
    append(settings_file, '\nfrom .common import *')
    append(settings_file, '\nfrom .secret_key import SECRET_KEY')


def _update_configs(source_folder, site_name):
    config_path = source_folder + '/deploy_tools/'
    sed(config_path + 'nginx.template.conf', r'SITENAME', site_name)
    sed(config_path + 'gunicorn-upstart.template.conf', r'SITENAME', site_name)


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, source_folder
        ))


def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python3 django/manage.py collectstatic --noinput' % (
        source_folder,
        ))


def _update_database(source_folder):
    run('cd %s && ../virtualenv/bin/python3 django/manage.py migrate --noinput' % (
        source_folder,
        ))
