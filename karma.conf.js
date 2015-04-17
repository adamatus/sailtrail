// Karma configuration
// Generated on Fri Jan 02 2015 11:35:54 GMT-0800 (PST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['browserify', 'mocha'],


    // list of files / patterns to load in the browser
    files: [
			'django/activities/static/activities/js/*.js.spec'
    ],


    // list of files to exclude
    exclude: [
      '**/*.bundle.js'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
			'django/activities/static/activities/js/*.js.spec': ['browserify']
    },


		// settings for browserify
		browserify: {
			debug: true,
			transform: [
				"debowerify",
				["browserify-istanbul", {"ignore": ["**/*.spec", "**/bower_components/**"]}]
			]
		},


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['mocha', 'coverage'],


    // coverage reporter configuration
    coverageReporter: {
      dir: '.cover/js',
      reporters: [
        // reporters not supporting the `file` property
        { type: 'html' },
        { type: 'text' },
      ]
    },


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
