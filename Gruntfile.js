module.exports = function(grunt) {

    var jslist = ['django/activities/static/activities/js/*.js'],
        jsbundlelist = ['django/activities/static/activities/js/*.bundle.js'],
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
                globalReplace: false
            }
        },

        changelog: {
            options: {
            }
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
                    "django/activities/static/activities/activity_viewer.bundle.js": "django/activities/static/activities/js/activity_viewer.js"
                },
                options: {
                    watch: true,
                    browserifyOptions: {
                        debug: true,
                    },
                }
            }
        },

        "django-manage": {
            options: {
                app: 'sailstats',
                manage_path: './django/'
            },

            test: {
                options: {
                    command: 'test',
                    args: [
                        'activities',
                        'sirf',
                        'tests'
                    ]
                }
            },

            unittest: {
                options: {
                    command: 'test',
                    args: [
                        'activities',
                        'sirf'
                    ]
                }
            },

            functest: {
                options: {
                    command: 'test',
                    args: [
                        'tests'
                    ]
                }
            },

            runserver: {
                options: {
                    command: 'runlivereloadserver',
                }
            },
        },

        karma: {
            options: {
                configFile: 'karma.conf.js'
            },

            jstest: {
                singleRun: true,
            },

            "jstest-watch": {
            },
        },

        sass: {
            dev: {
                files: {
                    "django/activities/static/activities/css/plots.css": "django/activities/static/activities/css/scss/plots.scss"
                }
            }
        }
    });

    // Load plugins here
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-bump');
    grunt.loadNpmTasks('grunt-conventional-changelog');
    grunt.loadNpmTasks('grunt-contrib-django');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-karma');

    // Register tasks here
    grunt.registerTask('default', []);

    grunt.registerTask('test', ['karma:jstest', 'django-manage:test']);
    grunt.registerTask('unittest', ['karma:jstest', 'django-manage:unittest']);
    grunt.registerTask('functest', ['django-manage:functest']);
    grunt.registerTask('jstest', ['karma:jstest']);
    grunt.registerTask('pytest', ['django-manage:unittest']);

    grunt.registerTask('dev', ['browserify', 'watch']);
    grunt.registerTask('jsdev', ['karma:jstest-watch']);
    grunt.registerTask('runserver', ['django-manage:runserver']);

};
