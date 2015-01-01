module.exports = function(grunt) {

	var jslist = ['activities/static/activities/js/*.js'];

  // Project configuration
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

		watch: {
		
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
		}
  });

  // Load plugins here
  grunt.loadNpmTasks('grunt-browserify');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Register tasks here
  grunt.registerTask('default', []);
	
	grunt.registerTask('dev', ['browserify', 'watch']);

};
