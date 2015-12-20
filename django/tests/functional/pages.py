import os
import time

from selenium.common.exceptions import StaleElementReferenceException, \
    NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

ASSET_PATH = os.path.dirname(os.path.abspath(__file__)) + '/assets'

TIMEOUT = 3


def wait_for(condition_function):
    """Wait for function to evaluate as true.  Timeout after a while.

    Parameters
    ----------
    condition_function : function

    """
    start_time = time.time()
    while time.time() < start_time + TIMEOUT:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception('Timeout waiting for {}'.format(
        condition_function.__name__))


class BasePage(object):

    def __init__(self, test):
        self.test = test
        self.browser = self.test.browser

    def get_alerts(self):
        return self.browser.find_element_by_css_selector('.alert-danger').text

    def get_all_alerts(self):
        return self.browser.find_elements_by_css_selector('.alert-danger')

    def is_alert_free(self):
        try:
            self.browser.find_element_by_css_selector('.alert-danger')
            return False
        except NoSuchElementException:
            return True

    def is_user_dropdown_present(self, username):
        try:
            link = self.browser.find_element_by_id('nav-user-dropdown-toggle')
            print(link.text)
            return username == link.text.strip()
        except NoSuchElementException:
            return False

    def get_page_content(self):
        return self.browser.find_element_by_tag_name('body').text

    def click_through_to_new_page(self, elem):
        body = self.browser.find_element_by_tag_name('body')
        elem.click()

        def link_has_gone_stale():
            try:
                body.find_elements_by_id('doesnt-matter')
                return False
            except StaleElementReferenceException:
                return True

        wait_for(link_has_gone_stale)

    def enter_text_in_field_by_id(self, text, element_id):
        field = self.browser.find_element_by_id(element_id)
        field.clear()
        field.send_keys(text)

    def logout(self):
        self.browser.find_element_by_id('nav-user-dropdown-toggle').click()
        logout_button = self.browser.find_element_by_link_text("Logout")
        self.click_through_to_new_page(logout_button)
        logout_button = self.browser.find_element_by_id("logout-btn")
        self.click_through_to_new_page(logout_button)

    def login(self):
        self.browser.find_element_by_link_text("Login").click()

    def upload_file(self, filename):
        self.browser.find_element_by_id('nav-user-dropdown-toggle').click()
        self.browser.find_element_by_id('nav-upload-link').click()
        upload_box = self.browser.find_element_by_id(
            'id_upfile'
        )
        upload_box.send_keys(os.path.join(ASSET_PATH, filename))
        print("About to click upload...")
        self.click_upload()

    def upload_without_file(self):
        self.browser.find_element_by_id('nav-user-dropdown-toggle').click()
        self.browser.find_element_by_id('nav-upload-link').click()
        self.click_upload()

    def click_upload(self):
        self.browser.find_element_by_id('upload-file-btn').click()

    def cancel_upload(self):
        self.browser.find_element_by_id('cancel-upload-btn').click()


class HomePage(BasePage):

    def go_to_homepage(self):
        self.browser.get(self.test.live_server_url)

    def go_to_activity(self, name):
        self.browser.find_element_by_link_text(name).click()

    def go_to_registration(self):
        self.browser.find_element_by_link_text('Register').click()

    def is_current_url(self):
        return self.browser.current_url == (self.test.live_server_url + '/')

    def activity_list_is_empty(self):
        return [] == self.browser.find_elements_by_css_selector('.activity')


class RegistrationPage(BasePage):

    def register(self, username):
        self.enter_username(username)
        self.enter_email('test@example.com')
        self.enter_password('password')
        self.click_register()

    def enter_username(self, username):
        self.enter_text_in_field_by_id(username, 'id_username')

    def enter_email(self, email):
        self.enter_text_in_field_by_id(email, 'id_email')

    def enter_password(self, password):
        self.enter_password1(password)
        self.enter_password2(password)

    def enter_password1(self, password):
        self.enter_text_in_field_by_id(password, 'id_password1')

    def enter_password2(self, password):
        self.enter_text_in_field_by_id(password, 'id_password2')

    def click_register(self):
        register_button = self.browser.find_element_by_id('register-btn')
        self.click_through_to_new_page(register_button)


class LoginPage(BasePage):

    def login_as_user(self, username, password):
        field = self.browser.find_element_by_id('id_login')
        field.clear()
        field.send_keys(username)
        field = self.browser.find_element_by_id('id_password')
        field.clear()
        field.send_keys(password)
        self.click_login()

    def click_login(self):
        login_button = self.browser.find_element_by_id('login-btn')
        self.click_through_to_new_page(login_button)


class ActivityPage(BasePage):

    def click_edit(self):
        self.browser.find_element_by_link_text('Edit').click()

    def click_delete(self):
        self.browser.find_element_by_id('activity_delete_button').click()

    def click_add_track(self):
        self.browser.find_element_by_id('upload-file-modal-btn').click()

    def click_confirm_delete(self):
        self.browser.find_element_by_link_text('Delete It').click()

    def click_cancel_delete(self):
        self.browser.find_element_by_id("activity_delete_cancel").click()

    def go_to_track(self, name):
        self.browser.find_element_by_link_text(name).click()

    def delete_modal_is_visible(self):
        # Silly sleeps to deal with fade effect of modal
        time.sleep(.1)
        is_visible = self.browser.find_element_by_id(
            'delete_modal').is_displayed()
        time.sleep(.1)
        return is_visible

    def add_track_modal_is_visible(self):
        # Silly sleeps to deal with fade effect of modal
        time.sleep(.1)
        is_visible = self.browser.find_element_by_id(
            'upload-track-modal').is_displayed()
        time.sleep(.1)
        return is_visible

    def get_winddir(self):
        wind_dir_input = self.browser.find_element_by_id('manual-wind-dir')
        return wind_dir_input.get_attribute('value')

    def upload_track(self, filename):
        if not self.add_track_modal_is_visible():
            self.browser.find_element_by_id('upload-file-modal-btn').click()
        upload_box = self.browser.find_element_by_id(
            'id_upfile'
        )
        upload_box.send_keys(os.path.join(ASSET_PATH, filename))
        self.browser.find_element_by_id('upload-file-btn').click()


class ActivityDetailsPage(BasePage):

    def enter_text(self, element_id, text):
        field = self.browser.find_element_by_id(element_id)
        field.clear()
        field.send_keys(text)

    def enter_name(self, name):
        self.enter_text('id_name', name)

    def enter_description(self, desc):
        self.enter_text('id_description', desc)

    def enter_details(self, name, desc):
        self.enter_name(name)
        self.enter_description(desc)

    def select_activity_type(self, category):
        select = Select(self.browser.find_element_by_id('id_category'))
        select.select_by_visible_text(category)

    def enable_private(self):
        checkbox = self.browser.find_element_by_id('id_private')
        if not checkbox.is_selected():
            checkbox.click()

    def disable_private(self):
        checkbox = self.browser.find_element_by_id('id_private')
        if checkbox.is_selected():
            checkbox.click()

    def click_ok(self):
        self.browser.find_element_by_id('save-details').click()

    def click_cancel(self):
        self.browser.find_element_by_link_text('Cancel').click()


class ActivityTrackPage(BasePage):

    def click_delete(self):
        self.browser.find_element_by_id('activity_delete_button').click()

    def click_cancel(self):
        self.browser.find_element_by_id('activity_delete_cancel').click()

    def click_delete_it(self):
        self.browser.find_element_by_link_text('Delete It').click()

    def delete_modal_is_visible(self):
        # Silly sleeps to deal with fade effect of modal
        time.sleep(.5)
        is_visible = self.browser.find_element_by_id(
            'delete_modal').is_displayed()
        time.sleep(.5)
        return is_visible

    def press_right_arrow(self):
        time.sleep(.5)
        self.browser.find_element_by_tag_name('body').send_keys(
            Keys.ARROW_RIGHT
        )

    def click_trim_start(self):
        time.sleep(.5)
        self.browser.find_element_by_id('trim-start').click()

    def click_trim_end(self):
        time.sleep(.5)
        self.browser.find_element_by_id('trim-end').click()

    def click_trim_activity(self):
        time.sleep(.5)
        trim_button = self.browser.find_element_by_id('trim-activity')
        self.click_through_to_new_page(trim_button)

    def click_untrim(self):
        untrim_button = self.browser.find_element_by_link_text('Untrim')
        self.click_through_to_new_page(untrim_button)
