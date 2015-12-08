import pytest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail

from selenium import webdriver

from activities.forms import ERROR_ACTIVITY_NAME_MISSING
from core.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                        ERROR_UNSUPPORTED_FILE_TYPE)
from .pages import (HomePage, ActivityPage, ActivityDetailsPage,
                    RegistrationPage, LoginPage, ActivityTrackPage)


@pytest.mark.functional
class ActivitiesTest(StaticLiveServerTestCase):
    fixtures = ['two-users-no-data.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

        # Initialize page-specific helpers
        self.home_page = HomePage(self)
        self.registration_page = RegistrationPage(self)
        self.details_page = ActivityDetailsPage(self)
        self.activity_page = ActivityPage(self)
        self.track_page = ActivityTrackPage(self)
        self.login_page = LoginPage(self)

    def tearDown(self):
        self.browser.quit()

    def test_basic_look_and_feel(self):
        # Visitor comes to homepage and notices title is SailTrail
        self.home_page.go_to_homepage()
        self.assertIn('SailTrail', self.browser.title)

    def test_registration(self):
        # Visitor comes to homepage
        self.home_page.go_to_homepage()

        # The notice the register link and click it, then try to immediatly
        # click register
        self.home_page.go_to_registration()
        self.registration_page.click_register()

        # They are warned that fields cannot be empty
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(4, len(alerts))
        self.assertIn('This field is required.', alerts[0].text)

        # They enter just a username, and are still warned
        self.registration_page.enter_username('testuser')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(3, len(alerts))
        self.assertIn('This field is required.', alerts[0].text)

        # They enter a username and valid email, and are still warned
        self.registration_page.enter_username('testuser')
        self.registration_page.enter_email('testuser@example.com')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(2, len(alerts))
        self.assertIn('This field is required.', alerts[0].text)

        # They enter a username, valid email, and first password, and
        # are still warned
        self.registration_page.enter_username('testuser')
        self.registration_page.enter_email('testuser@example.com')
        self.registration_page.enter_password1('password')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn('This field is required.', alerts[0].text)

        # They enter a username, valid email, and two passwords
        # that don't match, and are warned
        self.registration_page.enter_username('testuser')
        self.registration_page.enter_email('testuser@example.com')
        self.registration_page.enter_password1('password')
        self.registration_page.enter_password2('other')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn("You must type the same password each time.",
                      alerts[0].text)

        # They enter a username, invalid email, and matching passwords
        # and are warned about the email address
        self.registration_page.enter_username('testuser')
        self.registration_page.enter_email('testuser')
        self.registration_page.enter_password('password')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn("Enter a valid email address.", alerts[0].text)

        # They enter an existing username, valid email, and matching passwords
        # and are warned about the email address
        self.registration_page.enter_username('registered')
        self.registration_page.enter_email('testuser@example.com')
        self.registration_page.enter_password('password')
        self.registration_page.click_register()
        alerts = self.registration_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn("This username is already taken. Please choose another.",
                      alerts[0].text)

        # Finally, the fill in good info, submit, and
        # are taken to a page telling them that they need to confirm their
        # email address.
        self.home_page.go_to_registration()
        self.registration_page.register('testuser')

        # They see a message about how they will be recieving an email
        self.assertIn('Verify Your E-mail Address',
                      self.home_page.get_page_content())

        # Internally, an email is sent, with registration confirmation details
        self.assertEqual(1, len(mail.outbox))
        message = mail.outbox[0]
        self.assertEqual('signup@sailtrail.net', message.from_email)
        self.assertIn('Please Confirm Your E-mail Address', message.subject)

        for line in message.body.split('\n'):
            if 'localhost' in line:
                url = line.split(' ')[-1][8:]

        # The user follows the link in the email, and is asked
        # to confirm that they entered this info
        self.browser.get(url)
        self.assertIn('Confirm E-mail Address',
                      self.home_page.get_page_content())

        # They click confirm and are taken to the login page
        submit_btn = self.browser.find_element_by_id('submit-btn')
        self.home_page.click_through_to_new_page(submit_btn)

        # They login and are taken home
        self.login_page.login_as_user('testuser', 'password')
        self.assertTrue(self.home_page.is_current_url())

    def test_new_user_flow(self):
        # Visitor comes to homepage
        self.home_page.go_to_homepage()

        # The notice the register link and click it, fill in their info,
        # submit, and are taken back to the homepage
        self.home_page.go_to_registration()
        self.registration_page.register('testuser')

        message = mail.outbox[0]
        for line in message.body.split('\n'):
            if 'localhost' in line:
                url = line.split(' ')[-1][8:]
        self.browser.get(url)
        submit_btn = self.browser.find_element_by_id('submit-btn')
        self.home_page.click_through_to_new_page(submit_btn)
        self.login_page.login_as_user('testuser', 'password')

        self.assertTrue(self.home_page.is_current_url())

        # They notice a file upload box and are prompted to upload a file
        self.home_page.upload_file('tiny.SBN')

        # They are taken to the new details page, where they notice
        # the date and time and duration of the session listed
        self.assertIn('July 15, 2014', self.details_page.get_page_content())
        self.assertIn('10:37 p.m.', self.details_page.get_page_content())
        self.assertIn('0:00:03', self.details_page.get_page_content())

        # They are taken to the new activity page, where they are
        # prompted to enter details about the uploaded file
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        self.details_page.enter_details(name, desc)

        # They hit 'OK' and are redirected to the activity page,
        # where they notice that their name and description are shown
        self.details_page.click_ok()
        self.assertIn(name, self.activity_page.get_page_content())

        # They return to the homepage and see the activity listed
        self.home_page.go_to_homepage()
        self.assertIn(name, self.home_page.get_page_content())

        # The visitor decides to logout, and when the homepage refreshes
        # they notice that they are no longer logged in
        self.home_page.logout()
        self.assertTrue(self.home_page.is_current_url())
        self.assertFalse(self.home_page.is_user_dropdown_present('testuser'))

        # They decide to log back in, and can again see their name
        self.home_page.login()
        self.login_page.login_as_user('testuser', 'password')
        self.assertTrue(self.home_page.is_current_url())
        self.assertTrue(self.home_page.is_user_dropdown_present('testuser'))

    def test_login_logout(self):
        # Visit goes to homepage and clicks Login
        self.home_page.go_to_homepage()
        self.home_page.login()

        # They try to click the login button without entering, and see
        # errors
        self.login_page.click_login()
        self.assertIn('This field is required', self.login_page.get_alerts())

        # They enter a username, but forget a password, and are warned
        self.login_page.login_as_user('testuser', '')
        self.assertIn('This field is required', self.login_page.get_alerts())

        # They enter a password, but forget a username, and are warned
        self.login_page.login_as_user('', 'password')
        self.assertIn('This field is required', self.login_page.get_alerts())

        # They enter a bad username and password and are warned
        self.login_page.login_as_user('testuser', 'password')
        self.assertIn('The login and/or password you specified are ' +
                      'not correct', self.login_page.get_alerts())

        # They enter a good, existing username and are taken back to the
        # homepage where they can see they are logged in
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_current_url())
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # They click logout and are logged out
        self.home_page.logout()
        self.assertTrue(self.home_page.is_current_url())
        self.assertFalse(self.home_page.is_user_dropdown_present('registered'))

    def test_uploading(self):
        # Known user comes to homepage and logs in
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # They upload an SBN file
        self.home_page.upload_file('tiny.SBN')

        # They are taken to the new details page, where they notice
        # the date and time and duration of the session listed
        self.assertIn('July 15, 2014', self.details_page.get_page_content())
        self.assertIn('10:37 p.m.', self.details_page.get_page_content())
        self.assertIn('0:00:03', self.details_page.get_page_content())

        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        self.details_page.enter_details(name, desc)

        # They hit 'OK' and are redirected to the activity page,
        # where they notice that their name and description are shown
        self.details_page.click_ok()
        self.assertIn(name, self.activity_page.get_page_content())
        self.assertIn(desc, self.activity_page.get_page_content())

        # They return to the homepage and click upload without
        # choosing a file!
        self.home_page.go_to_homepage()
        self.home_page.upload_without_file()

        # They get a helpful error message telling them this
        # is not okay! They decide to cancel
        self.assertIn(ERROR_NO_UPLOAD_FILE_SELECTED,
                      self.home_page.get_alerts())
        self.home_page.cancel_upload()

        # They upload another file (choosing a GPX file this time),
        # but this time on the details screen they click cancel
        self.home_page.upload_file('tiny-run.gpx')
        name = 'A short GPX-based activity'
        desc = 'Very short'
        self.details_page.enter_details(name, desc)
        self.details_page.select_activity_type("Windsurfing")

        # They hit 'OK' and are redirected to the activity page,
        # where they see the usual details, as well as a notice that
        # the activity is marked as private.
        self.details_page.click_ok()
        content = self.activity_page.get_page_content()
        self.assertIn(name, content)
        self.assertIn(desc, content)
        self.assertIn("Windsurfing", content)
        self.assertIn("March 16, 2011", content)
        self.assertIn("0:03:01", content)
        self.assertIn("0.27 nmi", content)
        self.assertIn("5.6 knots", content)

        # They try the upload again (with a non-supported text-file)
        # and see an error warning them not to do that, so they hit cancel
        self.home_page.go_to_homepage()
        self.home_page.upload_file('bad.txt')
        self.assertIn(ERROR_UNSUPPORTED_FILE_TYPE, self.home_page.get_alerts())
        self.home_page.cancel_upload()

    def test_private_activity(self):
        # Registered user comes in and logs in
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # They successfully upload a GPX file and
        # fill in the revelant details, including the category. They notice
        # the Private checkbox and check it
        self.home_page.upload_file('tiny-run.gpx')
        name = 'A short GPX-based activity'
        desc = 'Very short'
        self.details_page.enter_details(name, desc)
        self.details_page.select_activity_type("Windsurfing")
        self.details_page.enable_private()

        # They hit 'OK' and are redirected to the activity page,
        # where they see the usual details, as well as a notice that
        # the activity is marked as private.
        self.details_page.click_ok()
        content = self.activity_page.get_page_content()
        self.assertIn(name, content)
        self.assertIn(desc, content)
        self.assertIn("Windsurfing", content)
        self.assertIn("March 16, 2011", content)
        self.assertIn("0:03:01", content)
        self.assertIn("0.27 nmi", content)
        self.assertIn("5.6 knots", content)
        self.assertIn("This activity is currently private", content)
        private_url = self.browser.current_url

        # The visitor returns to the home page and sees their new
        # activity (marked as private)
        self.home_page.go_to_homepage()
        content = self.home_page.get_page_content()
        self.assertIn(name, content)
        self.assertIn("Sailed by registered", content)
        self.assertIn("Private", content)

        # The visitor decides to logout, and when the homepage refreshes
        # they notice that their private activity is not longer visible
        self.home_page.logout()
        content = self.home_page.get_page_content()
        self.assertNotIn(name, content)
        self.assertNotIn("Private", content)

        # They decide to log back in, and can again see their activity
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        content = self.home_page.get_page_content()
        self.assertIn(name, content)
        self.assertIn("Sailed by registered", content)
        self.assertIn("Private", content)

        # The visitor logouts, and when the homepage refreshes
        # they notice that their private activity is not longer visible
        self.home_page.logout()
        content = self.home_page.get_page_content()
        self.assertNotIn(name, content)
        self.assertNotIn("Private", content)

        # Another user comes along and logs in, and they don't see the other
        # users private activity
        self.home_page.login()
        self.login_page.login_as_user('another', 'password')
        content = self.home_page.get_page_content()
        self.assertNotIn(name, content)
        self.assertNotIn("Private", content)

        # Somehow the second user guesses the url of the other users private
        # activity and tries to visit it.
        self.browser.get(private_url)
        content = self.home_page.get_page_content()
        self.assertIn("403 Forbidden", content)

    def test_edit_activity_details(self):
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # They upload a file with some details
        self.home_page.upload_file('tiny.SBN')
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        self.details_page.enter_details(name, desc)

        # They hit 'OK' and are redirected to the activity page,
        # where they notice that their name and description are shown
        self.details_page.click_ok()
        self.assertIn(name, self.activity_page.get_page_content())
        self.assertIn(desc, self.activity_page.get_page_content())

        # They notice an 'edit' link, and click it
        self.activity_page.click_edit()

        # They are taken to a page where they can edit their page.
        # They make a change to the description and hit ok
        new_desc = 'Updated description'
        self.details_page.enter_description(new_desc)
        self.details_page.click_ok()

        # They are redirected to the activity page,
        # where they can see that the description has been updated
        self.assertIn(name, self.activity_page.get_page_content())
        self.assertIn(new_desc, self.activity_page.get_page_content())
        self.assertNotIn(desc, self.activity_page.get_page_content())

        # They click the edit button again, update the name, then
        # change their mind and hit 'cancel'
        self.activity_page.click_edit()
        new_name = 'Updated activity name'
        self.details_page.enter_name(new_name)
        self.details_page.click_cancel()

        # They are taken back to the activity page and the details
        # are as they were before
        self.assertIn(name, self.activity_page.get_page_content())
        self.assertNotIn(new_name, self.activity_page.get_page_content())
        self.assertIn(new_desc, self.activity_page.get_page_content())
        self.assertNotIn(desc, self.activity_page.get_page_content())

        # They click the edit button again, blank out the name, try to
        # save, and are warned that that's not okay,
        self.activity_page.click_edit()
        new_name = ''
        self.details_page.enter_name(new_name)
        self.details_page.click_ok()
        self.assertIn(ERROR_ACTIVITY_NAME_MISSING,
                      self.details_page.get_alerts())

        # They then change their mind and hit 'cancel'
        self.details_page.click_cancel()

        # They are taken back to the activity page and the details
        # are as they were before
        self.assertIn(name, self.activity_page.get_page_content())
        self.assertIn(new_desc, self.activity_page.get_page_content())

    def test_deleting_activity(self):
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # They upload a file with some details
        self.home_page.upload_file('tiny.SBN')
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        self.details_page.enter_details(name, desc)
        self.details_page.click_ok()

        # They head over to the home page, where they see the activity
        self.home_page.go_to_homepage()
        self.assertIn(name, self.home_page.get_page_content())

        # They return to the activity page, and click delete.
        self.home_page.go_to_activity(name)
        self.activity_page.click_delete()
        self.assertTrue(self.activity_page.delete_modal_is_visible())
        self.activity_page.click_cancel_delete()
        self.assertFalse(self.activity_page.delete_modal_is_visible())

        # They head over to the home page, where they see the activity
        self.home_page.go_to_homepage()
        self.assertIn(name, self.home_page.get_page_content())

        # They return to the activity page, and click delete.
        # decide to confirm, and are returned to the homepage,
        self.home_page.go_to_activity(name)
        self.activity_page.click_delete()
        self.assertTrue(self.activity_page.delete_modal_is_visible())
        self.activity_page.click_confirm_delete()
        self.assertTrue(self.home_page.is_current_url())

        # They notice that their activity is no longer listed
        self.assertNotIn(name, self.home_page.get_page_content())

    def test_adding_and_deleting_tracks(self):
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # Third times the charm, they successful upload a GPX file and
        # fill in the revelant details, including the category. They notice
        # the Private checkbox and check it
        self.home_page.upload_file('tiny-run.gpx')
        name = 'A short GPX-based activity'
        self.details_page.enter_details(name, '')
        self.details_page.click_ok()

        # They return to their activity, and click "Add Track"
        self.activity_page.click_add_track()
        self.assertTrue(self.activity_page.add_track_modal_is_visible())

        # The visitor uploads a new track
        self.activity_page.upload_track('tiny-run-2.gpx')
        content = self.activity_page.get_page_content()
        self.assertIn("tiny-run.gpx", content)
        self.assertIn("tiny-run-2.gpx", content)
        self.assertIn("0:05:31", content)
        self.assertIn("0.54 nmi", content)
        self.assertIn("11.89 knots", content)

        # They click "Add Track" again and try to upload
        # without choosing a file, and are warned not to do that
        self.activity_page.click_add_track()
        self.activity_page.click_upload()
        self.assertIn(ERROR_NO_UPLOAD_FILE_SELECTED,
                      self.activity_page.get_alerts())
        self.activity_page.cancel_upload()

        # They next try to upload a non-supported text-file as a new track
        # and see an error warning them not to do that, so they hit cancel
        self.activity_page.upload_track('bad.txt')
        self.assertIn(ERROR_UNSUPPORTED_FILE_TYPE,
                      self.activity_page.get_alerts())
        self.activity_page.cancel_upload()

        # They click on the link to get to first track segment and
        # notice the trim activity section
        self.activity_page.go_to_track("tiny-run.gpx")
        content = self.track_page.get_page_content()
        self.assertIn("Trim Activity", content)

        # They notice the delete button and click it,
        # and the model pops up
        self.track_page.click_delete()
        self.assertTrue(self.track_page.delete_modal_is_visible())

        # They click cancel and the modal disappears
        self.track_page.click_cancel()
        self.assertFalse(self.track_page.delete_modal_is_visible())

        # They change their mind, click delete again and confirm
        self.track_page.click_delete()
        self.track_page.click_delete_it()

        # The visitor is taken back to the activity page, where
        # the track is no longer listed
        content = self.activity_page.get_page_content()
        self.assertIn("tiny-run-2.gpx", content)
        self.assertNotIn("tiny-run.gpx", content)
        self.assertIn("0:02:00", content)
        self.assertIn("0.27 nmi", content)
        self.assertIn("11.89 knots", content)

    def test_track_trimming(self):
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # Third times the charm, they successful upload a GPX file and
        # fill in the revelant details, including the category. They notice
        # the Private checkbox and check it
        self.home_page.upload_file('tiny-run-2.gpx')
        name = 'A short GPX-based activity'
        self.details_page.enter_details(name, '')
        self.details_page.click_ok()

        # The activity page contains details about their activity
        content = self.activity_page.get_page_content()
        self.assertIn("0:02:00", content)
        self.assertIn("0.27 nmi", content)
        self.assertIn("11.89 knots", content)

        # They return to the individual track page, and decide to try
        # trimming it
        self.activity_page.go_to_track("tiny-run-2.gpx")
        self.track_page.press_right_arrow()
        self.track_page.click_trim_start()
        self.track_page.press_right_arrow()
        self.track_page.press_right_arrow()
        self.track_page.click_trim_end()
        self.track_page.click_trim_activity()

        # The visitor is taken back to the activity page, where
        # the track is now trimmed
        content = self.activity_page.get_page_content()
        self.assertIn("0:01:00", content)
        self.assertIn("0.19 nmi", content)
        self.assertIn("11.89 knots", content)
        self.assertIn("tiny-run-2.gpx (trimmed)", content)

        # They return to the track page, and click untrim
        self.activity_page.go_to_track("tiny-run-2.gpx (trimmed)")
        self.track_page.click_untrim()

        # The activity details are untrimmed
        content = self.activity_page.get_page_content()
        self.assertIn("0:02:00", content)
        self.assertIn("0.27 nmi", content)
        self.assertIn("11.89 knots", content)
        self.assertNotIn("(trimmed)", content)
