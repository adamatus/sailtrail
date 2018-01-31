"""Functional (selenium) tests of overall site interactions (cross app)

Notes:

Any test that uploads files should mixin the FileDeleter mixin, and
then use a with self.settings to alter the upload root.

Any tests that need to create images should use both the FileDeleter and
and self.settings to alter the upload root and the STATIC_MAP_TYPE to fake.
"""
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tests.functional.pages import (
    HomePage, BoatPage, LoginPage
)
from tests.utils import FileDeleter

LOGGER.setLevel(logging.WARNING)


@pytest.mark.functional
class BoatsTest(FileDeleter, StaticLiveServerTestCase):
    fixtures = ['two-users-no-data.json']

    def setUp(self):
        super(BoatsTest, self).setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

        # Initialize page-specific helpers
        self.home_page = HomePage(self)
        self.boat_page = BoatPage(self)
        self.login_page = LoginPage(self)

    def tearDown(self):
        super(BoatsTest, self).tearDown()
        self.browser.quit()

    def test_add_and_remove_new_boat(self):
        # Registered user comes to home page and logs in
        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(
            self.home_page.is_user_dropdown_present('registered'))

        # The click on the their user name, see a My Boats link, and click it
        self.home_page.click_username_dropdown()
        self.assertIn('My boats', self.home_page.get_page_content())

        boats_button = self.browser.find_element_by_link_text("My boats")
        self.home_page.click_through_to_new_page(boats_button)

        # They land on the boats page and see no entries
        self.boat_page.assert_on_users_boat_page("registered")
        self.assertTrue(self.boat_page.boat_list_is_empty())

        # The click on the button to add a new boat
        self.boat_page.click_add_boat()

        # The see a form to fill out for a new boat, fill it out, and submit
        self.boat_page.add_boat("Test Boat", "Prototype Boat")

        # They see the details of their new boat
        self.assertIn('Test Boat', self.boat_page.get_page_content())

        # They click back on the My Boats link through the nav
        self.home_page.click_username_dropdown()
        self.assertIn('My boats', self.home_page.get_page_content())
        boats_button = self.browser.find_element_by_link_text("My boats")
        self.home_page.click_through_to_new_page(boats_button)

        # They land on the boats page and see their new entry in the now
        # non-empty list
        self.boat_page.assert_on_users_boat_page("registered")
        self.assertFalse(self.boat_page.boat_list_is_empty())
        self.boat_page.assert_boat_list_contains_boat("Test Boat")

        # They click on boat name in the list and are taken to the boat listing
        self.boat_page.click_boat_link("Test Boat")
        self.boat_page.assert_boat_page_title_has_boat_name("Test Boat")

        # They click the delete button, but decide not to delete yet
        self.boat_page.click_delete_boat()
        self.assertTrue(self.boat_page.delete_modal_is_visible())
        self.boat_page.click_cancel_delete()
        self.assertFalse(self.boat_page.delete_modal_is_visible())

        # They click delete again, confirm, and are taken back to users boat
        # list, where they see the boat they delete no longer in list
        self.boat_page.click_delete_boat()
        self.assertTrue(self.boat_page.delete_modal_is_visible())
        self.boat_page.click_confirm_delete()
        self.boat_page.assert_on_users_boat_page("registered")
        self.assertTrue(self.boat_page.boat_list_is_empty())

    @pytest.mark.skip(reason="Not yet implemented!")
    def test_boat_detail_page_contains_interesting_things(self):
        pass
        # List of activites on boat page
        # Summary stats on boat page
        # Only shows delete/edit on boats managed by user

    @pytest.mark.skip(reason="Not yet implemented!")
    def test_boat_edit(self):
        pass
        # Managing user should be able to edit a boat and immediately see
        # the changes

    @pytest.mark.skip(reason="Not yet implemented!")
    def test_boat_list_page_shows_boats_across_managers(self):
        pass

    @pytest.mark.skip(reason="Not yet implemented!")
    def test_boats_that_are_private_should_only_show_for_manager(self):
        pass

    @pytest.mark.skip(reason="Not yet implemented!")
    def test_boats_should_have_crew_that_allow_for_good_stuff(self):
        pass
