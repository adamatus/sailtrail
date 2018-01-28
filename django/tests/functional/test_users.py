"""Functional (selenium) tests of user related site interactions """
import pytest

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail

from tests.functional.pages import (
    HomePage, RegistrationPage, LoginPage, SettingsPage, ChangePasswordPage,
    ChangeEmailPage
)


@pytest.mark.functional
class UsersTest(StaticLiveServerTestCase):
    fixtures = ['two-users-no-data.json']

    def setUp(self):
        super(UsersTest, self).setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

        # Initialize page-specific helpers
        self.home_page = HomePage(self)
        self.registration_page = RegistrationPage(self)
        self.login_page = LoginPage(self)
        self.settings_page = SettingsPage(self)

    def tearDown(self):
        super(UsersTest, self).tearDown()
        self.browser.quit()

    def test_registration(self):
        # Visitor comes to homepage
        self.home_page.go_to_homepage()

        # The notice the register link and click it, then try to immediately
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
        self.assertIn("A user with that username already exists",
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
        self.assertEqual('signup@sailtrail.com', message.from_email)
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
        self.assertIn('The username and/or password you specified are ' +
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

    def test_change_user_password(self):
        settings_page = SettingsPage(self)
        change_password_page = ChangePasswordPage(self)

        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # User goes to their settings page
        self.home_page.goto_user_settings()
        content = settings_page.get_page_content()
        self.assertIn("Settings for registered", content)

        # Click link to change password and are taken to the password page
        settings_page.click_change_password()
        self.assertIn('Change Password', self.browser.title)

        # They try to click change password without entering anything and
        # are warned not to do that
        change_password_page.submit_password_change()
        alerts = change_password_page.get_all_alerts()
        self.assertEqual(3, len(alerts))
        self.assertIn("This field is required", alerts[0].text)
        self.assertIn("This field is required", alerts[1].text)
        self.assertIn("This field is required", alerts[2].text)

        # They then enter the wrong current password, but a matching new
        # password
        change_password_page.change_password('badpassword', 'newpassword',
                                             'newpassword')
        alerts = change_password_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn("Please type your current password", alerts[0].text)

        # They then enter the current password, but non-matching new passwords
        change_password_page.change_password('password', 'newpassword',
                                             'newpassword2')
        alerts = change_password_page.get_all_alerts()
        self.assertEqual(1, len(alerts))
        self.assertIn("You must type the same password each time",
                      alerts[0].text)

        # They then enter the current password and matching new passwords and
        # are redirected back to the homepage where an alert tells them they
        # have successfully updated their password
        change_password_page.change_password('password', 'newpassword',
                                             'newpassword')
        settings_page.assert_is_current_url_for_user('registered')
        self.assertIn("Password successfully updated",
                      settings_page.get_success_alert_text())

        # They refresh the page and notice that the alert is now gone
        self.browser.refresh()
        settings_page.assert_is_current_url_for_user('registered')
        with self.assertRaises(NoSuchElementException):
            settings_page.get_success_alert_text()

        # The logout and are able to log back in with the new password
        # They enter a good, existing username and are taken back to the
        # homepage where they can see they are logged in
        self.home_page.logout()
        self.assertFalse(self.home_page.is_user_dropdown_present('registered'))

        self.home_page.login()
        self.login_page.login_as_user('registered', 'newpassword')
        self.assertTrue(self.home_page.is_current_url())
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

    def test_change_email(self):
        settings_page = SettingsPage(self)
        change_email_page = ChangeEmailPage(self)

        self.home_page.go_to_homepage()
        self.home_page.login()
        self.login_page.login_as_user('registered', 'password')
        self.assertTrue(self.home_page.is_user_dropdown_present('registered'))

        # User goes to their settings page
        self.home_page.goto_user_settings()

        # They click the change email link and are taken to the email page
        settings_page.click_change_email()
        self.assertIn('Your email addresses', self.browser.title)

        # They try to add a new email address without entering anything
        # and are warned about it
        change_email_page.click_add_email()
        self.assertIn("This field is required",
                      change_email_page.get_alerts())

        # They enter an invalid address and are warned about it
        change_email_page.enter_email_and_submit("test")
        self.assertIn("Enter a valid email address",
                      change_email_page.get_alerts())

        # They enter the address they are already registered with and are
        # warned
        change_email_page.enter_email_and_submit("registered@example.com")
        self.assertIn("This e-mail address is already associated with " +
                      "this account", change_email_page.get_alerts())

        # They enter the address that another user has used and are warned
        change_email_page.enter_email_and_submit("another@example.com")
        self.assertIn("This e-mail address is already associated with " +
                      "another account", change_email_page.get_alerts())

        # They enter a new address and see it added to the list, unverified
        change_email_page.enter_email_and_submit("test@example.com")
        content = change_email_page.get_page_content()
        self.assertIn("test@example.com", content)
        self.assertIn("Unverified", content)

        # They check their inbox, where they have a confirmation link, which
        # they follow
        message = mail.outbox[0]
        for line in message.body.split('\n'):
            if 'localhost' in line:
                url = line.split(' ')[-1][8:]
        self.browser.get(url)
        submit_btn = self.browser.find_element_by_id('submit-btn')
        content = change_email_page.get_page_content()
        self.assertIn("Please confirm that test@example.com", content)
        self.home_page.click_through_to_new_page(submit_btn)

        # User goes to their settings page and go back to the email page, where
        # they see that their new address is verified
        self.home_page.goto_user_settings()
        settings_page.click_change_email()
        content = change_email_page.get_page_content()
        self.assertIn("test@example.com", content)
        self.assertNotIn("Unverified", content)

        # They select the new email from the list and click remove
        self.browser.find_element_by_id('email_radio_2').click()
        self.browser.find_element_by_name('action_remove').click()

        # The are warned, and click cancel
        alert = self.browser.switch_to.alert
        self.assertEqual(alert.text,
                         "Do you really want to remove " +
                         "the selected e-mail address?")
        alert.dismiss()

        # The address is still in the list
        content = change_email_page.get_page_content()
        self.assertIn("test@example.com", content)

        # They click cancel again
        self.browser.find_element_by_id('email_radio_2').click()
        self.browser.find_element_by_name('action_remove').click()
        alert = self.browser.switch_to.alert
        alert.accept()

        # The address is no longer in the list
        content = change_email_page.get_page_content()
        self.assertNotIn("test@example.com", content)
