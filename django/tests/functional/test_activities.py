from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from activities.forms import (ERROR_NO_UPLOAD_FILE_SELECTED,
                              ERROR_ACTIVITY_NAME_MISSING)
from .pages import (HomePage, ActivityPage, ActivityDetailsPage,
                    RegistrationPage)


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

        # Visitor comes to homepage and notices title is SailStats
        homepage.go_to_homepage()
        self.assertIn('SailStats', self.browser.title)

        # The notice the register link and click it, fill in their info,
        # submit, and are taken back to the homepage
        homepage.go_to_registration()
        registration.register('testuser')
        self.assertTrue(homepage.is_current_url())

        # They notice a file upload box and are prompted to upload a file
        homepage.upload_file('kite-session1.sbn')

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

        # The user clicks on the link for their uploaded sessions and
        # are taken to back to a page which shows the details
        homepage.go_to_activity(name)
        self.assertIn(name, activity_page.get_page_content())

        # They return to the homepage and click upload without
        # choosing a file!
        homepage.go_to_homepage()
        homepage.upload_without_file()

        # They get a helpful error message telling them this
        # is not okay!
        self.assertIn(ERROR_NO_UPLOAD_FILE_SELECTED, homepage.get_alerts())

        # They return to their uploaded page and notice an 'edit' link
        # and click it
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

        # They click the edit button again, blank out the name, get
        # warned that it's not okay,
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

        # They upload another file, but this time on the details screen
        # they click cancel
        homepage.upload_file('kite-session2.sbn')
        details_page.click_cancel()

        # They are taken back to the homepage, and their session is
        # not shown in the list
        self.assertTrue(homepage.is_current_url())
        self.assertTrue(homepage.activity_list_is_empty())

        # They upload another file, but this time on the details screen
        # they navigate back to the homepage!
        homepage.upload_file('kite-session2.sbn')
        homepage.go_to_homepage()

        # Again, they don't see the item in the list
        self.assertTrue(homepage.activity_list_is_empty())

    def test_activity_stats(self):
        homepage = HomePage(self)
        registration = RegistrationPage(self)
        details_page = ActivityDetailsPage(self)
        activity_page = ActivityPage(self)

        # Logged in visitor uploads file
        homepage.go_to_homepage()
        homepage.go_to_registration()
        registration.register('testuser')
        homepage.upload_file('kite-session1.sbn')

        # They are taken to the new details page, where they notice
        # the date and time and duration of the session listed
        self.assertIn('Jan. 19, 2014', details_page.get_page_content())
        self.assertIn('4:45 p.m.', details_page.get_page_content())
        self.assertIn('1:29:07', details_page.get_page_content())

        # They enter some session details and click ok
        name = 'First winter kite session!'
        desc = 'The very first session of the year'
        details_page.enter_details(name, desc)
        details_page.click_ok()

        # They notice the same details on the activity page
        self.assertIn('Jan. 19, 2014', activity_page.get_page_content())
        self.assertIn('4:45 p.m.', activity_page.get_page_content())
        self.assertIn('1:29:07', activity_page.get_page_content())
