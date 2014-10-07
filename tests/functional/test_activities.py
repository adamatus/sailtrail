from django.test import LiveServerTestCase

from selenium import webdriver

import os

ASSET_PATH = os.path.dirname(os.path.abspath(__file__)) + '/assets'


class FileUploadTest(LiveServerTestCase):
    """Test the uploading of SBN files"""

    def setUp(self):
        """Initialize testing setup"""

        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(2)

    def tearDown(self):
        """Clean-up after testing"""
        self.browser.quit()

    def test_visit_homepage(self):
        """Functional tests for visiting homepage and uploading file"""

        # Visitor comes to homepage and notices title is SailStats
        self.browser.get(self.live_server_url)
        self.assertIn('SailStats', self.browser.title)

        # They notice a file upload box and are prompted to upload a file
        upload_box = self.browser.find_element_by_id(
            'sailstats-upload-activity'
        )
        upload_box.send_keys(os.path.join(ASSET_PATH, 'kite-session1.sbn') + 
                             '\n')

        # They now see the file in the list of activities 
        self.browser.get(self.live_server_url)
        body = self.browser.find_element_by_tag_name('body').text
        self.assertIn('kite-session1.sbn', body)

        # They don't see the whole path though!
        self.assertNotIn(ASSET_PATH, body)

        # The user clicks on one of their uploaded sessions and are taken to
        # a page which shows the details of the session
        self.browser.find_element_by_link_text('kite-session1.sbn').click()
        body = self.browser.find_element_by_tag_name('body').text
        self.assertIn('kite-session1.sbn', body)
        self.assertIn(ASSET_PATH, body)

        # self.fail('Finish the tests!')

