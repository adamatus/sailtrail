from django.test import LiveServerTestCase

from selenium import webdriver
import shutil
import tempfile

import os

from activities.forms import ERROR_NO_UPLOAD_FILE_SELECTED

ASSET_PATH = os.path.dirname(os.path.abspath(__file__)) + '/assets'


class FileUploadTest(LiveServerTestCase):
    """Test the uploading of SBN files"""

    def setUp(self):
        """Initialize testing setup"""

        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean-up after testing"""
        self.browser.quit()
        shutil.rmtree(self.temp_dir)

    def test_visit_homepage(self):
        """Functional tests for visiting homepage and uploading file"""

        with self.settings(MEDIA_ROOT=self.temp_dir):
            # Visitor comes to homepage and notices title is SailStats
            self.browser.get(self.live_server_url)
            self.assertIn('SailStats', self.browser.title)

            # They notice a file upload box and are prompted to upload a file
            upload_box = self.browser.find_element_by_id(
                'id_upfile'
            )
            upload_box.send_keys(os.path.join(ASSET_PATH, 'kite-session1.sbn'))
            submit = self.browser.find_element_by_css_selector(
                'input[type="submit"]')
            submit.click()

            # They now see the file in the list of activities 
            self.browser.get(self.live_server_url)
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn('kite-session1.sbn', body)

            # The user clicks on one of their uploaded sessions and are taken 
            # to a page which shows the details of the session
            self.browser.find_element_by_link_text(
                'activities/kite-session1.sbn').click()
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn('kite-session1.sbn', body)

            # They return to the homepage and click upload without
            # choosing a file!
            self.browser.get(self.live_server_url)
            submit = self.browser.find_element_by_css_selector(
                'input[type="submit"]')
            submit.click()

            # They get a helpful error message telling them this
            # is not okay!
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn(ERROR_NO_UPLOAD_FILE_SELECTED, body)

            # self.fail('Finish the tests!')

