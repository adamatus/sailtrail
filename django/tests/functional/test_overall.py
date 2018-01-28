"""Functional (selenium) tests of overall site interactions (cross app)

Notes:

Any test that uploads files should mixin the FileDeleter mixin, and
then use a with self.settings to alter the upload root.

Any tests that need to create images should use both the FileDeleter and
and self.settings to alter the upload root and the STATIC_MAP_TYPE to fake.
"""
import pytest
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail

from tests.functional.pages import (
    HomePage, ActivityPage, ActivityDetailsPage, RegistrationPage,
    LoginPage
)
from tests.utils import FileDeleter


@pytest.mark.functional
class OverallSiteTest(FileDeleter, StaticLiveServerTestCase):
    fixtures = ['two-users-no-data.json']

    def setUp(self):
        super(OverallSiteTest, self).setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

        # Initialize page-specific helpers
        self.home_page = HomePage(self)
        self.registration_page = RegistrationPage(self)
        self.details_page = ActivityDetailsPage(self)
        self.activity_page = ActivityPage(self)
        self.login_page = LoginPage(self)

    def tearDown(self):
        super(OverallSiteTest, self).tearDown()
        self.browser.quit()

    def test_basic_look_and_feel(self):
        # Visitor comes to homepage and notices title is SailTrail
        self.home_page.go_to_homepage()
        self.assertIn('SailTrail', self.browser.title)

    def test_new_user_flow(self):
        # Visitor comes to homepage
        with self.settings(MEDIA_ROOT=self.temp_dir,
                           REMOTE_MAP_SOURCE='fake'):
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
            self.assertIn('July 15, 2014',
                          self.details_page.get_page_content())
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
            self.assertFalse(
                self.home_page.is_user_dropdown_present('testuser'))

            # They decide to log back in, and can again see their name
            self.home_page.login()
            self.login_page.login_as_user('testuser', 'password')
            self.assertTrue(self.home_page.is_current_url())
            self.assertTrue(
                self.home_page.is_user_dropdown_present('testuser'))
