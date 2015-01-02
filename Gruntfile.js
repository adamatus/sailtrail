module.exports = function(grunt) {

	var jslist = ['activities/static/activities/js/*.js'],
			jsbundlelist = ['activities/static/activities/js/*.bundle.js'],
			sasslist = ['activities/static/activities/css/scss/*.scss'];
			csslist = ['activities/static/activities/css/*.css'];

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
				files: csslist.concat(jsbundlelist),
			},
		},

		browserify: {
			dev: {
				files: {
					"activities/static/activities/js/activity_viewer.bundle.js": "activities/static/activities/js/activity_viewer.js"
				
				},
				options: {
					watch: true
				}
			}
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
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Register tasks here
  grunt.registerTask('default', []);
	
	grunt.registerTask('dev', ['browserify', 'watch']);

};
