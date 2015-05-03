import os
import time

ASSET_PATH = os.path.dirname(os.path.abspath(__file__)) + '/assets'


class BasePage(object):

    def __init__(self, test):
        self.test = test
        self.browser = self.test.browser

    def get_alerts(self):
        return self.browser.find_element_by_css_selector('.alert-danger').text

    def get_page_content(self):
        return self.browser.find_element_by_tag_name('body').text


class HomePage(BasePage):

    def go_to_homepage(self):
        self.browser.get(self.test.live_server_url)

    def upload_file(self, filename):
        self.browser.find_element_by_id('upload-file-modal-btn').click()
        upload_box = self.browser.find_element_by_id(
            'id_upfile'
        )
        upload_box.send_keys(os.path.join(ASSET_PATH, filename))
        self.browser.find_element_by_id('upload-file-btn').click()

    def upload_without_file(self):
        self.browser.find_element_by_id('upload-file-modal-btn').click()
        self.browser.find_element_by_id('upload-file-btn').click()

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
        field = self.browser.find_element_by_id('id_username')
        field.send_keys(username)
        field = self.browser.find_element_by_id('id_email')
        field.send_keys('test@example.com')
        field = self.browser.find_element_by_id('id_password1')
        field.send_keys('password')
        field = self.browser.find_element_by_id('id_password2')
        field.send_keys('password')
        self.browser.find_element_by_id('register-btn').click()


class ActivityPage(BasePage):

    def click_edit(self):
        self.browser.find_element_by_link_text('Edit').click()

    def click_delete(self):
        self.browser.find_element_by_id('activity_delete_button').click()

    def click_confirm_delete(self):
        self.browser.find_element_by_link_text('Delete It').click()

    def click_cancel_delete(self):
        self.browser.find_element_by_id("activity_delete_cancel").click()

    def delete_modal_is_visible(self):
        # Silly sleeps to deal with fade effect of modal
        time.sleep(.1)
        is_visible = self.browser.find_element_by_id(
            'delete_modal').is_displayed()
        time.sleep(.1)
        return is_visible


class ActivityDetailsPage(BasePage):

    def enter_text(self, id, text):
        field = self.browser.find_element_by_id(id)
        field.clear()
        field.send_keys(text)

    def enter_name(self, name):
        self.enter_text('id_name', name)

    def enter_description(self, desc):
        self.enter_text('id_description', desc)

    def enter_details(self, name, desc):
        self.enter_name(name)
        self.enter_description(desc)

    def click_ok(self):
        self.browser.find_element_by_id('save-details').click()

    def click_cancel(self):
        self.browser.find_element_by_link_text('Cancel').click()
