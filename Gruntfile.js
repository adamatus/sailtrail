module.exports = function(grunt) {

	var jslist = ['activities/static/activities/js/*.js'],
			jsbundlelist = ['activities/static/activities/js/*.bundle.js'],
			sasslist = ['activities/static/activities/css/scss/*.scss'],
			csslist = ['activities/static/activities/css/*.css'],
			templatelist = ['activities/templates/**/*.html'];

  // Project configuration
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

		bump: {
			options: {
				files: ['package.json', 'bower.json'],
				commit: true,
				commitMessage: 'Release v%VERSION%',
			  commitFiles: ['package.json', 'bower.json'],
        createTag: true,
        tagName: 'v%VERSION%',
        tagMessage: 'Version %VERSION%',
        push: true,
        pushTo: '',
        gitDescribeOptions: '--tags --always --abbrev=1 --dirty=-d',
        globalReplace: false
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
					"activities/static/activities/js/activity_viewer.bundle.js": "activities/static/activities/js/activity_viewer.js"
				
				},
				options: {
					watch: true,
					transform: ['browserify-shim', 'debowerify']
				}
			}
		},
		
		"django-manage": {
			options: {
				app: 'sailstats',
				manage_path: 'django/'
			},

			test: {
				options: {
					command: 'test',
					args: [
						'activities sirf tests'
					]
				}
			},
			
			unittest: {
				options: {
					command: 'test',
					args: [
						'activities sirf'
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
					"activities/static/activities/css/plots.css": "activities/static/activities/css/scss/plots.scss"
				}
			}
		}
  });

  // Load plugins here
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-bump');
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

};
