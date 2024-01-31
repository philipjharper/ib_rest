"""
test_suite_template_tst - Starter template for a Unittests  module.

Author:  Philip Harper
Edited:  9/14/2023
"""
from ltlddslta01_info import url, certificate_bundle
import os
from ib_rest import Connection
from unittest import TestCase, TestSuite, makeSuite, TextTestRunner

#
# Instantiate a Connection which targets the non-production WAPI.
#

ib_conn = Connection(url=url, certificate_bundle=certificate_bundle)

#
# Test fixtures.
#

class TestLogin(TestCase):
    """
    Log in to the Infoblox WAPI with an API enabled local account.
    """
    def test_login_pass(self):
        """"""
        ib_conn.login(os.environ["TECHLAB_ACCOUNT"],os.environ["TECHLAB_PASSWORD"])
        self.assertTrue(ib_conn.isloggedin)

class TestLogout(TestCase):
    """"""
    def test_logout_pass(self):
        """"""
        ib_conn.logout()
        self.assertFalse(ib_conn.isloggedin)

#
# Run the test cases, in order, as a suite.
#

def suite():
    """
    Gather all the tests from this module in a test suite.
    """
    test_suite = TestSuite()
    test_suite.addTest(makeSuite(TestLogin))
    test_suite.addTest(makeSuite(TestLogout))
    return test_suite

mySuite=suite()

runner=TextTestRunner()


if __name__ == "__main__":
    """"""
    runner.run(mySuite)
