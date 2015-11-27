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
                files: ['package.json', 'bower.json'],
                commit: true,
                commitMessage: 'chore: Release v%VERSION%',
                commitFiles: ['package.json', 'bower.json', 'CHANGELOG.md'],
                createTag: true,
                tagName: 'v%VERSION%',
                tagMessage: 'Version %VERSION%',
                push: true,
                pushTo: '',
                gitDescribeOptions: '--tags --always --abbrev=1 --dirty=-d',
                globalReplace: false,
            },
        },

        changelog: {
            options: {
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

        'django-manage': {
            options: {
                app: 'sailtrail',
                manage_path: './django/',
            },

            test: {
                options: {
                    command: 'test',
                    args: [
                        'activities',
                        'sirf',
                        'tests',
                    ],
                },
            },

            unittest: {
                options: {
                    command: 'test',
                    args: [
                        'activities',
                        'sirf',
                    ],
                },
            },

            functest: {
                options: {
                    command: 'test',
                    args: [
                        'tests',
                    ],
                },
            },

            runserver: {
                options: {
                    command: 'runlivereloadserver',
                },
            },
        },

        karma: {
            options: {
                configFile: 'karma.conf.js',
            },

            jstest: {
                singleRun: true,
            },

            'jstest-watch': {
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
            pytest: {
                command: 'py.test -n 2 --color=yes --durations=5 --cov-config .coveragerc --cov-report term-missing --cov-report html --cov . activities sirf',
            },
            pyfunc: {
                command: 'py.test --color=yes --durations=5 --cov-config .func-coveragerc --cov-report term-missing --cov-report html --cov . tests',
            },
            pywatch: {
                command: 'py.test -f --lf --color=yes --durations=5 activities',
            },
            'pytest-verbose': {
                command: 'py.test -v --color=yes --durations=0 --cov-config .coveragerc --cov-report term-missing --cov-report html --cov . activities sirf',
            },
        },
    });

    // Load plugins here
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-bump');
    grunt.loadNpmTasks('grunt-conventional-changelog');
    grunt.loadNpmTasks('grunt-contrib-django');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-eslint');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-flake8');
    grunt.loadNpmTasks('grunt-shell');

    // Register tasks here
    grunt.registerTask('default', []);

    grunt.registerTask('test', ['eslint', 'karma:jstest', 'shell:pytest', 'shell:pyfunc']);
    grunt.registerTask('unittest', ['karma:jstest', 'shell:pytest']);
    grunt.registerTask('functest', ['shell:pyfunc']);
    grunt.registerTask('jstest', ['eslint', 'karma:jstest']);
    grunt.registerTask('pytest', ['shell:pytest']);

    grunt.registerTask('dev', ['browserify', 'watch']);
    grunt.registerTask('jsdev', ['karma:jstest-watch']);
    grunt.registerTask('pydev', ['shell:pywatch']);
    grunt.registerTask('runserver', ['django-manage:runserver']);
};
