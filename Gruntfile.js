'use strict';

module.exports = function(grunt) {

    var jsbundlelist = ['django/activities/static/activities/js/*.bundle.js'],
        sasslist = ['django/activities/static/activities/css/scss/*.scss'],
        csslist = ['django/activities/static/activities/css/*.css'],
        templatelist = ['django/activities/templates/**/*.html'];

    // Project configuration
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        bump: {
            options: {
                files: ['package.json', 'bower.json', 'django/activities/templates/components/footer.html'],
                commit: true,
                commitMessage: 'chore: Release v%VERSION%',
                commitFiles: ['package.json', 'bower.json', 'CHANGELOG.md', 'django/activities/templates/components/footer.html'],
                createTag: true,
                tagName: 'v%VERSION%',
                tagMessage: 'Version %VERSION%',
                push: true,
                pushTo: 'origin',
                gitDescribeOptions: '--tags --always --abbrev=1 --dirty=-d',
                globalReplace: false,
            },
        },

        conventionalChangelog: {
            options: {
                changelogOpts: {
                    preset: 'angular',
                },
            },
            release: {
                src: 'CHANGELOG.md',
            },
        },

        eslint: {
            options: {
                configFile: 'eslint.json',
            },
            target: ['django/**/*.js', 'django/**/*.spec', '!**/*.bundle.js'],
        },

        flake8: {
            src: [
                'django/**/*.py',
                '!**/migrations/*.py',
            ],
        },

        pylint: {
            options: {
                externalPylint: true,
                rcfile: 'pylintrc',
            },

            apps: {
                src: [
                    'django/api',
                    'django/core',
                    'django/leaders',
                    'django/sirf',
                    'django/users',
                ],
                options: {
                    ignore: ['migrations', 'tests'],
                },
            },

            tests: {
                src: 'django/tests',
                options: {
                    force: true,
                    disable: 'missing-docstring',
                },
            },
        },

        watch: {
            sass: {
                files: sasslist,
                tasks: ['sass'],
            },
            livereload: {
                options: { livereload: true },
                files: csslist.concat(jsbundlelist, templatelist),
            },
        },

        browserify: {
            dev: {
                files: {
                    'django/activities/static/activities/activity_viewer.bundle.js': 'django/activities/static/activities/js/activity_viewer.js',
                },
                options: {
                    watch: true,
                    browserifyOptions: {
                        debug: true,
                    },
                },
            },
        },

        karma: {
            options: {
                configFile: 'karma.conf.js',
            },

            jstest: {
                options: {
                    reporters: ['mocha', 'coverage'],
                    browserify: {
                        transform: [
                            'debowerify',
                            ['browserify-istanbul', {'ignore': ['**/*.spec', '**/bower_components/**']}],
                        ],
                    },
                },
                singleRun: true,
            },

            jsdev: {
            },
        },

        sass: {
            dev: {
                files: {
                    'django/activities/static/activities/css/plots.css': sasslist,
                },
            },
        },

        shell: {
            options: {
                execOptions: {
                    cwd: 'django',
                },
            },
            pyfuncdev: {
                command: 'py.test -f --lf --color=yes . -m functional',
            },
            pyfunctest: {
                command: 'py.test -v --color=yes --durations=0 --cov-config .func-coveragerc --cov-report term-missing --cov-report html --cov . -m functional',
            },
            pyintdev: {
                command: 'py.test -f --lf --color=yes . -m integration',
            },
            pyinttest: {
                command: 'py.test -v --color=yes --durations=0 --cov-config .int-coveragerc --cov-report term-missing --cov-report html --cov . -m integration',
            },
            pydev: {
                command: 'py.test -f --lf --color=yes . -m "not functional and not integration"',
            },
            pytest: {
                command: 'py.test -v --color=yes --durations=0 --cov-config .coveragerc --cov-report term-missing --cov-report html --cov . -m "not functional and not integration"',
            },
        },
    });

    // Load plugins here
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-bump');
    grunt.loadNpmTasks('grunt-conventional-changelog');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-eslint');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-flake8');
    grunt.loadNpmTasks('grunt-pylint');
    grunt.loadNpmTasks('grunt-shell');

    // Register tasks here
    grunt.registerTask('default', []);

    // TDD-Cycle watcher test tasks
    grunt.registerTask('jsdev', ['karma:jsdev']);
    grunt.registerTask('pydev', ['shell:pydev']);
    grunt.registerTask('funcdev', ['shell:pyfuncdev']);

    // Full code analysis tasks
    grunt.registerTask('test', ['eslint', 'karma:jstest', 'flake8', 'pylint', 'shell:pytest', 'shell:pyinttest', 'shell:pyfunctest']);
    grunt.registerTask('unittest', ['karma:jstest', 'shell:pytest']);
    grunt.registerTask('functest', ['shell:pyfunctest']);
    grunt.registerTask('inttest', ['shell:pyinttest']);
    grunt.registerTask('jstest', ['eslint', 'karma:jstest']);
    grunt.registerTask('pytest', ['flake8', 'pylint', 'shell:pytest']);

    // Two tasks to run for interactive editing with livereload website
    grunt.registerTask('dev', ['browserify', 'watch']);
    grunt.registerTask('runserver', ['django-manage:runserver']);

    grunt.registerTask('changelog', ['conventionalChangelog']);
};
