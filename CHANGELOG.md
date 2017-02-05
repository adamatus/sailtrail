<a name="0.2.2"></a>
## [0.2.2](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.2.1...v0.2.2) (2017-02-05)

### Features

* Update python dependencies, including Django to 1.10.5 ([4e7feed](https://bitbucket.org/adamatus/sailtrail.net/commits/4e7feed))

<a name="0.2.1"></a>
## [0.2.1](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.2.0...v0.2.1) (2017-01-22)

### Features

* Move from .net to .com ([1e8d600](https://bitbucket.org/adamatus/sailtrail.net/commits/1e8d600))

### Bug Fixes

* Show correct activity images on user list page ([5c59607](https://bitbucket.org/adamatus/sailtrail.net/commits/5c59607))

# [0.2.0](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.2.0%0Dv0.1.14) (2016-09-21) "Sunfish"

### Features

* Add option to only highlight last minute on track/speed plots ([31b8141](https://bitbucket.org/adamatus/sailtrail.net/commits/31b8141))
* Add summary image to activity list ([a3a722a](https://bitbucket.org/adamatus/sailtrail.net/commits/a3a722a))
* Improve track trimming and allow for adjustment ([bab9b31](https://bitbucket.org/adamatus/sailtrail.net/commits/bab9b31))

### Bug Fixes

* Mapquest integration works again ([74682e9](https://bitbucket.org/adamatus/sailtrail.net/commits/74682e9))

## [0.1.14](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.14%0Dv0.1.13) (2016-01-27)

### Features

* Major code cleanup, with some query optimizations ([97abe17](https://bitbucket.org/adamatus/sailtrail.net/commits/97abe17))

### Bug Fixes

* Fixed several small edges cases during refactor ([97abe17](https://bitbucket.org/adamatus/sailtrail.net/commits/97abe17))

## [0.1.13](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.13%0Dv0.1.12) (2015-12-31)

### Features

* Nice, theme-matching error pages ([ea36e76](https://bitbucket.org/adamatus/sailtrail.net/commits/ea36e76))

### Bug Fixes

* Deleting of last track for activity no longer breaks everything ([8a9d124](https://bitbucket.org/adamatus/sailtrail.net/commits/8a9d124))
* Download track file link now working again ([15c2f17](https://bitbucket.org/adamatus/sailtrail.net/commits/15c2f17))
* Track-related pages are now only visible to their owner ([c8dc404](https://bitbucket.org/adamatus/sailtrail.net/commits/c8dc404))

## [0.1.12](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.12%0Dv0.1.11) (2015-12-31)

### Features

* Add pagination for activity lists ([116130a](https://bitbucket.org/adamatus/sailtrail.net/commits/116130a))
* Add user settings page with email and password changes ([13d8b3d](https://bitbucket.org/adamatus/sailtrail.net/commits/13d8b3d))
* Use S3 for original file storage ([09382b3](https://bitbucket.org/adamatus/sailtrail.net/commits/09382b3))

### Bug Fixes

* Missing map on details/new activity page restored ([e66852f](https://bitbucket.org/adamatus/sailtrail.net/commits/e66852f))

## [0.1.11](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.11%0Dv0.1.10) (2015-12-20)

### Features

* Major refactor to split codebase into apps ([387cd1c](https://bitbucket.org/adamatus/sailtrail.net/commits/387cd1c))

### Bug Fixes

* Remove livereload.js in prod ([3b8b1d2](https://bitbucket.org/adamatus/sailtrail.net/commits/3b8b1d2))
* Fix handling of manual wind direction ([7745ae9](https://bitbucket.org/adamatus/sailtrail.net/commits/7745ae9))

## [0.1.10](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.10%0Dv0.1.9) (2015-12-01)

### Features

* Add sitemap.xml and robots.txt ([107184d](https://bitbucket.org/adamatus/sailtrail.net/commits/107184d))

## [0.1.9](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.9%0Dv0.1.8) (2015-12-01)

### Bug Fixes

* FIx gruntfile changelog settings ([c674416](https://bitbucket.org/adamatus/sailtrail.net/commits/c674416))

### Features

* Add version to homepage ([80265a5](https://bitbucket.org/adamatus/sailtrail.net/commits/80265a5))

## [0.1.8](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.8%0Dv0.1.7) (2015-11-29)

### Bug Fixes

* Fix bad form errors on upload page ([23d435f](https://bitbucket.org/adamatus/sailtrail.net/commits/23d435f))
* Don't include private activities in leaderboard ([d35cf06](https://bitbucket.org/adamatus/sailtrail.net/commits/d35cf06))

### Features

* Add proper email validation for new accounts ([4ba6e26](https://bitbucket.org/adamatus/sailtrail.net/commits/4ba6e26))
* Update dependencies, add python linting/static analysis ([5e6f2eb](https://bitbucket.org/adamatus/sailtrail.net/commits/5e6f2eb))

## [0.1.7](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.7%0Dv0.1.6) (2015-11-24)

### Bug Fixes

* Fix mapquest SSL tile source ([0ea62619](https://bitbucket.org/adamatus/sailtrail.net/commits/0ea62619))
* Fix handling of outside http/https refs ([ac2c96f1](https://bitbucket.org/adamatus/sailtrail.net/commits/ac2c96f1))
* Fix migrations to make postgres happy ([0914fccd](https://bitbucket.org/adamatus/sailtrail.net/commits/0914fccd))
* Fix migrations to make Postgres happy ([2a194fbc](https://bitbucket.org/adamatus/sailtrail.net/commits/2a194fbc))
* Fix ordering of trackpoints ([ac871aa5](https://bitbucket.org/adamatus/sailtrail.net/commits/ac871aa5))
* Fix login error/upload validation confusion ([7284dfa3](https://bitbucket.org/adamatus/sailtrail.net/commits/7284dfa3))
* Fix upload & delete modal behavior/validation ([5d89f040](https://bitbucket.org/adamatus/sailtrail.net/commits/5d89f040))

### Features

* Add google-analytics tracking ([67c03ec9](https://bitbucket.org/adamatus/sailtrail.net/commits/67c03ec9))
* Support upload of multiple files in one upload ([46239774](https://bitbucket.org/adamatus/sailtrail.net/commits/46239774))
* Add details to individual track pages ([fad19e1a](https://bitbucket.org/adamatus/sailtrail.net/commits/fad19e1a))
* Improve UX/UI + styling ([52319240](https://bitbucket.org/adamatus/sailtrail.net/commits/52319240))
* Save user-updated wind direction, improve polars ([6f3f82a7](https://bitbucket.org/adamatus/sailtrail.net/commits/6f3f82a7))
* Show activity map on details/upload page ([28d24970](https://bitbucket.org/adamatus/sailtrail.net/commits/28d24970))
* Homepage max speed leaderboard ([4238f31a](https://bitbucket.org/adamatus/sailtrail.net/commits/4238f31a))
* Add summary of activities on User page ([609b2079](https://bitbucket.org/adamatus/sailtrail.net/commits/609b2079))
* Add client-side upload validation ([45b8069e](https://bitbucket.org/adamatus/sailtrail.net/commits/45b8069e))
* Add UX for interacting with polar plots ([23a32fe7](https://bitbucket.org/adamatus/sailtrail.net/commits/23a32fe7))

## [0.1.6](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.6%0Dv0.1.5) (2015-05-21)

### Bug Fixes

* Fix computation and display of polars ([3c8777a6](https://bitbucket.org/adamatus/sailtrail.net/commits/3c8777a6))
* Re-compute stats after deleting track ([b6896291](https://bitbucket.org/adamatus/sailtrail.net/commits/b6896291))
* Stop delete track from deleting whole activity ([bfe92ac1](https://bitbucket.org/adamatus/sailtrail.net/commits/bfe92ac1))

### Features

* Allow manual adjustment of polar wind direction ([3a49a4b9](https://bitbucket.org/adamatus/sailtrail.net/commits/3a49a4b9))

## [0.1.5](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.5%0Dv0.1.4) (2015-04-15)

### Bug Fixes

* Update nginx config so it keeps track of port ([63b30f15](https://bitbucket.org/adamatus/sailtrail.net/commits/63b30f15))

## [0.1.4](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.4%0Dv0.1.3) (2015-02-26)

### Bug Fixes

* Remove trackpoints without a satellite fix on upload ([bb8fc89f](http://bitbucket.org/adamatus/sailtrail.net/commits/bb8fc89f615476f6d0085ae2e03ca5bd85fe864b))

### Features

* Add polar plots ([042b37a7](http://bitbucket.org/adamatus/sailtrail.net/commits/042b37a794fb722dcf7f33ba9e2e58f98c44f245))
* Add flag to mark activities as private ([4cd17cd8](http://bitbucket.org/adamatus/sailtrail.net/commits/4cd17cd887ef2f39d40a619adabd18ee28c2141b))

## [0.1.3](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.3%0Dv0.1.2) (2015-02-18)

### Bug Fixes

* Add server-side max speed to individual track pages ([39362b79](http://bitbucket.org/adamatus/sailtrail.net/commits/39362b790957c9232b0e6a3843122d00ca974780))

## [0.1.2](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.2%0Dv0.1.1) (2015-01-26)

### Features

* Add fabric-powered deployment to AWS ([fe343375](http://bitbucket.org/adamatus/sailtrail.net/commits/fe343375c1c22a4a03ea7605165cb30e4c0387cd))
* Add user-specific list pages and user list page ([3b458afc](http://bitbucket.org/adamatus/sailtrail.net/commits/3b458afcc46bc46af007b3916e6e46fd8308c20e))

## [0.1.1](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.1%0Dv0.1.0) (2015-01-20)

### Features

* Add GPX file import ([0fc94ae0](http://bitbucket.org/adamatus/sailtrail.net/commits/0fc94ae047013eb2908fd24bedd43a8dcc911c78))

## [0.1.0](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.1.0%0Dv0.0.4) (2015-01-19) "Optimist"

### Features

* Add user accounts ([c2a62bb1](http://bitbucket.org/adamatus/sailtrail.net/commits/c2a62bb1390acbf69fdc41f10fdea82126592c78))
* Add activity category field ([d53b97e0](http://bitbucket.org/adamatus/sailtrail.net/commits/d53b97e007f3b3d88efbbe49b758df4cc9cdd81e))

## [0.0.4](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.0.4%0Dv0.0.3) (2015-01-13)

### Bug Fixes

* Add error handling to trimming ([9d6f11e1](http://bitbucket.org/adamatus/sailtrail.net/commits/9d6f11e14811ee09b83593fff9577acbe9fec0ef))

### Features

* Add ability to have multiple tracks per activity ([bbba5cbc](http://bitbucket.org/adamatus/sailtrail.net/commits/bbba5cbcee5cdc955e8047930960e96d354c6ad7))
* Add speed color-gradient to track and speed plot ([bb2d1fee](http://bitbucket.org/adamatus/sailtrail.net/commits/bb2d1fee065ca2563e5a6d99f7499b9eb90954da))
* Add deletion confirmation dialog ([5efa56c8](http://bitbucket.org/adamatus/sailtrail.net/commits/5efa56c83e7dacae8164470ca321c1c6348fccda))

## [0.0.3](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.0.3%0Dv0.0.2) (2015-01-03)

* Internal build changes, including the ability to generate this nice changelog

## [0.0.2](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.0.2%0Dv0.0.1) (2015-01-03)

### Features

* Add activity distance ([f2f85f93](http://bitbucket.org/adamatus/sailtrail.net/commits/f2f85f93509cac8f50ec0e8d176fe644e2e7c36e))
* Implement rough track trimming ([9c282d32](http://bitbucket.org/adamatus/sailtrail.net/commits/9c282d32a2585e7a94fb9f33bea98cd912aa1eec))

## [0.0.1](https://bitbucket.org/adamatus/sailtrail.net/compare/v0.0.1) (2014-10-12)

### Bug Fixes

* Fix accidental delete of activity ([3bb7827c](http://bitbucket.org/adamatus/sailtrail.net/commits/3bb7827c3f9b07ccf08ebf94bf87a1ce4137c777))

### Features

* Add time slider to activity view ([56a0afc4](http://bitbucket.org/adamatus/sailtrail.net/commits/56a0afc431e32510c5a180f6a73a529bfcbb7278))
* Add rough speed plot to activity page ([5fbeaaf9](http://bitbucket.org/adamatus/sailtrail.net/commits/5fbeaaf91ec838e01013707c846c9b53af871822))
* Add basic max speed to activity page ([7eaa609e](http://bitbucket.org/adamatus/sailtrail.net/commits/7eaa609e3048034bfcfefac6e480a335adca6be5))
* Add leaflet powered track maps ([605d416c](http://bitbucket.org/adamatus/sailtrail.net/commits/605d416cd0c81c9d0d4eaccf9f70fcbb52764cfc))
* Add basic activity stats computed from file (time/date/dur) ([400a1821](http://bitbucket.org/adamatus/sailtrail.net/commits/400a18212a4ba17a223f1f58dbd77286850cabdb))
* Add basic styling (with bootstrap) ([ec99261a](http://bitbucket.org/adamatus/sailtrail.net/commits/ec99261a9fae8abf7cd8dfc68163812b2e708e16))
* Add activity details (name and description) ([fd22e0ba](http://bitbucket.org/adamatus/sailtrail.net/commits/fd22e0ba693a2ccc3d0cf8b3a6cdfb28139ccece))
* Add ability to delete activity from activity page ([4e4e465c](http://bitbucket.org/adamatus/sailtrail.net/commits/4e4e465c35abb3ae396b21d462b3bdea7e57e33b))
* Add file uploads ([dcec7c3b](http://bitbucket.org/adamatus/sailtrail.net/commits/dcec7c3b81063e159ee52e4c6055a8a2dd22d842))
* Add new module to handle SBN/SiRF binary GPS files ([9efb14fd](http://bitbucket.org/adamatus/sailtrail.net/commits/9efb14fd5e988638b735f928c0e75c384618b85e))
