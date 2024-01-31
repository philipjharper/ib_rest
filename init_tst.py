"""
init_tst - Unittests for the __init__ module.

Author:  Philip Harper
Edited:  9/26/2023
"""
from ltlddslta01_info import url, certificate_bundle
import os
from ib_rest import Connection, NotLoggedInException
from unittest import TestCase, TestSuite, makeSuite, TextTestRunner

#
# Instantiate a Connection which targets the non-production WAPI.
#

ib_conn = Connection(url=url, certificate_bundle=certificate_bundle)

#
# Test fixtures.
#

network_data = {
    "network":"1.0.4.0/24",
    "comment":"test network"
    }

network_data_update = {"comment":"Test new comment!"}

network_reference = ""

#
# Test Cases.
#

class TestNotLoggedIn(TestCase):
    """
    Send a GET request to tha Web API before logging in.
    """
    def test_schema_version(self):
        """"""
        self.assertRaises(NotLoggedInException, ib_conn.get, ("grid"))

        
class TestLogin(TestCase):
    """
    Log in to the Infoblox WAPI with an API enabled local account.
    """
    def test_login_pass(self):
        """"""
        ib_conn.login(os.environ["TECHLAB_ACCOUNT"],os.environ["TECHLAB_PASSWORD"])
        self.assertTrue(ib_conn.isloggedin)


class TestSchema(TestCase):
    """
    The login method uses GET to retrieve the WAPI schema and saves the value in the
    instance attribute named schema.

    The schema is a dictionary with 3 items: requested_version, supported_objects and
    supported_versions.

    Test for the above 3 items in the saved schema after a successful login.
    """
    def test_schema_version(self):
        """"""
        self.assertTrue(url.endswith(ib_conn.schema.get("requested_version", "0.0")))
    def test_supported_objects(self):
        """"""
        self.assertIsInstance(ib_conn.schema.get("supported_objects"), list)
    def test_supported_versions(self):
        """"""
        self.assertIsInstance(ib_conn.schema.get("supported_versions"), list)

        
class TestGet(TestCase):
    """
    Get the WAPI grid object and verify that the reference string has the expected
    format.
    """
    def test_get_grid(self):
        """"""
        result = ib_conn.get("grid")
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json()[0]["_ref"].startswith("grid"))
        #print(result.json())


class TestPaging(TestCase):
    """
    The paged version of the get method returns a list of the requested objects.
    """
    def test_get_networkviews(self):
        """"""
        networkviews = ib_conn.get_paged("networkview")
        for networkview in networkviews:
            networkview["_ref"].startswith("networkview")
        #print(result.json())


class TestSearchNetwork(TestCase):
    """"""
    def test_search_network_fail(self):
        """
        Search for a network that is known to not exist.
        """
        result = ib_conn.get("network", params={"network":network_data["network"]})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), [])
        #print(result.json())

        
class TestAddNetwork(TestCase):
    """"""    
    def test_add_network(self):
         """
         Add a test network to the default networkview.
         """
         global network_reference
         result = ib_conn.post("network", network_data)
         self.assertEqual(result.status_code, 201)
         network_reference = result.json()
         self.assertTrue(network_reference.startswith("network/"))
         self.assertTrue(network_reference.endswith("/default"))


class TestGetNetwork(TestCase):
    """"""    
    def test_get_network(self):
         """
         Read the new network by specifying the newly generated reference.
         """
         result = ib_conn.get_by_reference(network_reference, params={"_return_fields":"high_water_mark"})
         self.assertEqual(result.status_code, 200)
         self.assertEqual(result.json().get("high_water_mark", 0), 95)
         #print(result.json())


class TestUpdateNetwork(TestCase):
    """
    Update fields of the test network.
    """
    def test_update_network(self):
        """
        Update the test network..
        """
        global network_reference
        result = ib_conn.put(network_reference, data=network_data_update)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), network_reference)


class TestSearchNetworkbyComment(TestCase):
    """"""
    def test_search_network_pass(self):
        """
        Search for a network that has a comment.
        """
        result = ib_conn.get("network", params={"comment":network_data_update["comment"]})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()[0].get("_ref"), network_reference)
        #print(result.json())

        
class TestDeleteNetwork(TestCase):
    """"""
    def test_delete_network(self):
        """
        Delete the test network from the default networkview.
        """
        global network_reference
        result = ib_conn.delete(network_reference)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), network_reference)

        
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
    test_suite.addTest(makeSuite(TestNotLoggedIn))
    test_suite.addTest(makeSuite(TestLogin))
    test_suite.addTest(makeSuite(TestSchema))
    test_suite.addTest(makeSuite(TestGet))
    test_suite.addTest(makeSuite(TestPaging))
    test_suite.addTest(makeSuite(TestSearchNetwork))
    test_suite.addTest(makeSuite(TestAddNetwork))
    test_suite.addTest(makeSuite(TestGetNetwork))
    test_suite.addTest(makeSuite(TestUpdateNetwork))
    test_suite.addTest(makeSuite(TestSearchNetworkbyComment))
    test_suite.addTest(makeSuite(TestDeleteNetwork))
    test_suite.addTest(makeSuite(TestLogout))
    return test_suite

mySuite=suite()

runner=TextTestRunner()


if __name__ == "__main__":
    """"""
    runner.run(mySuite)
