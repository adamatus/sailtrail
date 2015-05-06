from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from activities.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                              ERROR_ACTIVITY_NAME_MISSING)
from .pages import (HomePage, ActivityPage, ActivityDetailsPage,
                    RegistrationPage, LoginPage, ActivityTrackPage)


class ActivitiesTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()

    def test_visit_homepage_and_upload_activity(self):
        homepage = HomePage(self)
        registration = RegistrationPage(self)
        details_page = ActivityDetailsPage(self)
        activity_page = ActivityPage(self)
        login_page = LoginPage(self)
        track_page = ActivityTrackPage(self)

        # Visitor comes to homepage and notices title is SailStats
        homepage.go_to_homepage()
        self.assertIn('SailStats', self.browser.title)

        # The notice the register link and click it, fill in their info,
        # submit, and are taken back to the homepage
        homepage.go_to_registration()
        registration.register('testuser')
        self.assertTrue(homepage.is_current_url())

        # They notice a file upload box and are prompted to upload a file
        homepage.upload_file('tiny.SBN')

        # They are taken to the new activity page, where they are
        # prompted to enter details about the uploaded file
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        details_page.enter_details(name, desc)

        # They hit 'OK' and are redirected to the activity page,
        # where they notice that their name and description are shown
        details_page.click_ok()
        self.assertIn(name, activity_page.get_page_content())
        self.assertIn(desc, activity_page.get_page_content())

        # They return to the homepage and see the activity listed
        homepage.go_to_homepage()
        self.assertIn(name, homepage.get_page_content())

        # The user clicks on the link for their uploaded session and
        # are taken to back to a page which shows the details
        homepage.go_to_activity(name)
        self.assertIn(name, activity_page.get_page_content())
        self.assertIn(desc, activity_page.get_page_content())

        # They return to the homepage and click upload without
        # choosing a file!
        homepage.go_to_homepage()
        homepage.upload_without_file()

        # They get a helpful error message telling them this
        # is not okay!
        self.assertIn(ERROR_NO_UPLOAD_FILE_SELECTED, homepage.get_alerts())

        # They return to their previously uploaded activity, notice
        # an 'edit' link, and click it
        homepage.go_to_activity(name)
        activity_page.click_edit()

        # They are taken to a page where they can edit their page.
        # They make a change to the description
        new_desc = 'Updated description'
        details_page.enter_description(new_desc)

        # They hit 'OK' and are redirected to the activity page,
        # where they can see that the description has been updated
        details_page.click_ok()
        self.assertIn(name, activity_page.get_page_content())
        self.assertIn(new_desc, activity_page.get_page_content())
        self.assertNotIn(desc, activity_page.get_page_content())

        # They click the edit button again, update the name, then
        # change their mind and hit 'cancel'
        activity_page.click_edit()
        new_name = 'Updated activity name'
        details_page.enter_name(new_name)
        details_page.click_cancel()

        # They are taken back to the activity page and the details
        # are as they were before
        self.assertIn(name, activity_page.get_page_content())
        self.assertNotIn(new_name, activity_page.get_page_content())
        self.assertIn(new_desc, activity_page.get_page_content())
        self.assertNotIn(desc, activity_page.get_page_content())

        # They click the edit button again, blank out the name, try to
        # save, and are warned that that's not okay,
        activity_page.click_edit()
        new_name = ''
        details_page.enter_name(new_name)
        details_page.click_ok()
        self.assertIn(ERROR_ACTIVITY_NAME_MISSING,
                      details_page.get_alerts())

        # They then change their mind and hit 'cancel'
        details_page.click_cancel()

        # They are taken back to the activity page and the details
        # are as they were before
        self.assertIn(name, activity_page.get_page_content())
        self.assertIn(new_desc, activity_page.get_page_content())

        # The click the 'delete' link and are prompted to confirm
        activity_page.click_delete()
        self.assertTrue(activity_page.delete_modal_is_visible())

        # They decide not to click cancel and the modal goes away
        activity_page.click_cancel_delete()
        self.assertFalse(activity_page.delete_modal_is_visible())

        # The click the 'delete' link again, decide to confirm,
        # and are returned to the homepage,
        activity_page.click_delete()
        self.assertTrue(activity_page.delete_modal_is_visible())
        activity_page.click_confirm_delete()
        self.assertTrue(homepage.is_current_url())

        # They notice that their activity is no longer listed
        self.assertNotIn(name, homepage.get_page_content())

        # They upload another file (choosing a GPX file this time),
        # but this time on the details screen they click cancel
        homepage.upload_file('tiny-run.gpx')
        details_page.click_cancel()

        # They are taken back to the homepage, and their session is
        # not shown in the list
        self.assertTrue(homepage.is_current_url())
        self.assertTrue(homepage.activity_list_is_empty())

        # They try the upload again (with the gpx file), but this time on the
        # details screen they navigate back to the homepage!
        homepage.upload_file('tiny-run.gpx')
        homepage.go_to_homepage()

        # Again, they don't see the item in the list
        self.assertTrue(homepage.activity_list_is_empty())

        # Third times the charm, they successful upload a GPX file and
        # fill in the revelant details
        homepage.upload_file('tiny-run.gpx')

        # They are taken to the new activity page, where they are
        # prompted to enter details about the uploaded file, including
        # changing the category. They also notice the Private checkbox
        # and check it.
        name = 'A short GPX-based activity'
        desc = 'Very short'
        details_page.enter_details(name, desc)
        details_page.select_activity_type("Windsurfing")
        details_page.enable_private()

        # They hit 'OK' and are redirected to the activity page,
        # where they see the usual details, as well as a notice that
        # the activity is marked as private.
        details_page.click_ok()
        content = activity_page.get_page_content()
        self.assertIn(name, content)
        self.assertIn(desc, content)
        self.assertIn("Windsurfing", content)
        self.assertIn("This activity is currently private", content)

        # The visitor returns to the home page and sees their new
        # activity (marked as private)
        homepage.go_to_homepage()
        content = homepage.get_page_content()
        self.assertIn(name, content)
        self.assertIn("Sailed by testuser", content)
        self.assertIn("Private", content)

        # The visitor decides to logout, and when the homepage refreshes
        # they notice that their private activity is not longer visible
        homepage.logout()
        content = homepage.get_page_content()
        self.assertNotIn(name, content)
        self.assertNotIn("Private", content)

        # They decide to log back in, and can again see their activity
        homepage.login()
        login_page.login('testuser', 'password')
        content = homepage.get_page_content()
        self.assertIn(name, content)
        self.assertIn("Sailed by testuser", content)
        self.assertIn("Private", content)

        # They return to their activity, and click "Add Track"
        homepage.go_to_activity(name)
        activity_page.click_add_track()
        self.assertTrue(activity_page.add_track_modal_is_visible())

        # The visitor uploads a new track
        activity_page.upload_track('tiny-run-2.gpx')
        content = activity_page.get_page_content()
        self.assertIn("tiny-run.gpx", content)
        self.assertIn("tiny-run-2.gpx", content)

        # They click on the link to get to first track segment and
        # notice the trim activity section
        activity_page.go_to_track("tiny-run.gpx")
        content = track_page.get_page_content()
        self.assertIn("Trim Activity", content)

        # They notice the delete button and click it,
        # and the model pops up
        track_page.click_delete()
        self.assertTrue(track_page.delete_modal_is_visible())

        # They click cancel and the modal disappears
        track_page.click_cancel()
        self.assertFalse(track_page.delete_modal_is_visible())

        # They change their mind, click delete again and confirm
        track_page.click_delete()
        track_page.click_delete_it()

        # # The visitor is taken back to the activity page, where
        # # the track is no longer listed
        # content = activity_page.get_page_content()
        # self.assertIn("tiny-run.gpx", content)
        # self.assertNotIn("tiny-run-2.gpx", content)

    def test_activity_stats(self):
        homepage = HomePage(self)
        registration = RegistrationPage(self)
        details_page = ActivityDetailsPage(self)
        activity_page = ActivityPage(self)

        # Logged in visitor uploads file
        homepage.go_to_homepage()
        homepage.go_to_registration()
        registration.register('testuser')
        homepage.upload_file('tiny.SBN')

        # They are taken to the new details page, where they notice
        # the date and time and duration of the session listed
        self.assertIn('July 15, 2014', details_page.get_page_content())
        self.assertIn('10:37 p.m.', details_page.get_page_content())
        self.assertIn('0:00:03', details_page.get_page_content())

        # They enter some session details and click ok
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        details_page.enter_details(name, desc)
        details_page.click_ok()

        # They notice the same details on the activity page
        self.assertIn('July 15, 2014', activity_page.get_page_content())
        self.assertIn('10:37 p.m.', activity_page.get_page_content())
        self.assertIn('0:00:03', activity_page.get_page_content())
