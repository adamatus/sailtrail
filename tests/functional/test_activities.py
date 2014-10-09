from django.test import LiveServerTestCase

from selenium import webdriver
import shutil
import tempfile

import os

from activities.forms import ERROR_NO_UPLOAD_FILE_SELECTED

ASSET_PATH = os.path.dirname(os.path.abspath(__file__)) + '/assets'


class ActivitiesTest(LiveServerTestCase):
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

    def test_visit_homepage_and_upload_activity(self):
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

            # They are taken to the new activity page, where they are 
            # prompted to enter details about the uploaded file
            name = 'First winter kite session!'
            desc = 'The very first session of the year'
            self.browser.find_element_by_id('id_name').send_keys(name)
            self.browser.find_element_by_id('id_description').send_keys(
                desc)
            
            # They hit 'OK' and are redirected to the session page
            self.browser.find_element_by_css_selector(
                'input[type="submit"]').click()
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn(name, body)
            self.assertIn(desc, body)

            # They return to the homepage and see the activity listed
            self.browser.get(self.live_server_url)
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn(name, body)

            # The user clicks on the link for their uploaded sessions and 
            # are taken to back to a page which shows the details
            self.browser.find_element_by_link_text(name).click()
            body = self.browser.find_element_by_tag_name('body').text
            self.assertIn(name, body)

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

            # They return to their uploaded page and notice a 'delete' link
            self.browser.find_element_by_link_text(name).click()
            delete = self.browser.find_element_by_link_text('Delete')

            # The click the link and are returned to the homepage,
            # where they notice that their activity is no longer listed
            delete.click()
            self.assertEqual(self.browser.current_url, 
                             self.live_server_url + '/')
            body = self.browser.find_element_by_tag_name('body').text
            self.assertNotIn(name, body)

            # They upload another file, but this time on the details screen
            # they click cancel
            upload_box = self.browser.find_element_by_id(
                'id_upfile'
            )
            upload_box.send_keys(os.path.join(ASSET_PATH, 'kite-session2.sbn'))
            submit = self.browser.find_element_by_css_selector(
                'input[type="submit"]')
            submit.click()
            self.browser.find_element_by_link_text('Cancel').click()

            # They are taken back to the homepage, and their session is
            # not shown in the list
            self.assertEqual(self.browser.current_url, 
                             self.live_server_url + '/')

            self.assertEqual(
                [], 
                self.browser.find_elements_by_css_selector('.activity'),
                'Items appear in activity list when they should not!'
            )

            # They upload another file, but this time on the details screen
            # they navigate back to the homepage!
            upload_box = self.browser.find_element_by_id(
                'id_upfile'
            )
            upload_box.send_keys(os.path.join(ASSET_PATH, 'kite-session2.sbn'))
            submit = self.browser.find_element_by_css_selector(
                'input[type="submit"]')
            submit.click()
            self.browser.get(self.live_server_url)

            # Again, they don't see the item in the list
            self.assertEqual(
                [], 
                self.browser.find_elements_by_css_selector('.activity'),
                'Items appear in activity list when they should not!'
            )


            


