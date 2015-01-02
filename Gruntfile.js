module.exports = function(grunt) {

	var jslist = ['activities/static/activities/js/*.js'],
			jsbundlelist = ['activities/static/activities/js/*.bundle.js'],
			sasslist = ['activities/static/activities/css/scss/*.scss'],
			csslist = ['activities/static/activities/css/*.css'],
			templatelist = ['activities/templates/**/*.html'];

  // Project configuration
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

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
				app: 'sailstats'
			},

			test: {
				options: {
					command: 'test'
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
  grunt.loadNpmTasks('grunt-contrib-django');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-karma');

  // Register tasks here
  grunt.registerTask('default', []);

	grunt.registerTask('test', ['karma:jstest', 'django-manage:test']);
	grunt.registerTask('unittest', ['karma:jstest', 'django-manage:unittest']);
	grunt.registerTask('functest', ['django-manage:functest']);
	
	grunt.registerTask('dev', ['browserify', 'watch']);
	grunt.registerTask('jsdev', ['karma:jstest-watch']);

};
