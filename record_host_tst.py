"""
record_host_tst - Unittests for the __init__ module.

Author:  Philip Harper
Edited:  9/14/2023
Edited:  9/22/2023 added TestCase.
"""
from ltlddslta01_info import url, certificate_bundle
import os
from ib_rest import Connection
from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
from record_host import isipavailable, create_host, read_host, read_host_data, find_host
from record_host import update_host_data, update_host_ttl, update_host_comment
#
# Instantiate a Connection which targets the non-production WAPI.
#

ib_conn = Connection(url=url, certificate_bundle=certificate_bundle)

#
# Test fixtures.
#

host30 = {"name":"ddi-host30.humana.com", "ip-address": "10.32.15.30", "ttl": 300, "comment": "DDI Host 30", "reference": ""}
host30_update = {"ip-address": "10.32.15.31", "ttl": 600, "comment": "DDI Host 30 Updated"}
host30_ipv4addrs = []

class TestLogin(TestCase):
    """
    Log in to the Infoblox WAPI with an API enabled local account.
    """
    def test_login_pass(self):
        """"""
        ib_conn.login(os.environ["TECHLAB_ACCOUNT"],os.environ["TECHLAB_PASSWORD"])
        self.assertTrue(ib_conn.isloggedin)

class TestHostIpAddressAvailable(TestCase):
    """"""
    def test_host_ip_available(self):
        """
        Test that there is not, currently, a record:host assigned this IP address.
        """
        self.assertTrue(isipavailable(ib_conn, host30["ip-address"]))


class TestReadHost30NotFound(TestCase):
    """"""
    def test_find_host30(self):
        """
        Verify that an attempt to find host30 by using find_host, which will return a
        list of DNS host records matching the name field, returns an empty list since
        none have been created yet.
        """
        response = find_host(ib_conn, host30["name"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

      
class TestCreateHost30(TestCase):
    """"""
    def test_create_host30(self):
        """
        Create the new record:host using the host30 test fixture and then verify the response.
        """
        global host30
        response = create_host(ib_conn, host30["name"], [host30["ip-address"],], ttl=host30["ttl"], comment=host30["comment"])
        self.assertEqual(response.status_code, 201)
        reference = response.json()
        host30["reference"] = reference
        reference_l = reference.split("/")
        self.assertEqual(reference_l[0], "record:host")
        self.assertEqual(reference_l[1].split(":")[1], host30["name"])
        self.assertEqual(reference_l[2], "default")
        #print(response.json())


class TestHost30Created(TestCase):
    """"""
    def test_host_ip_not_available(self):
        """
        Test that there is a record:host assigned to this IP address.
        """
        self.assertFalse(isipavailable(ib_conn, host30["ip-address"]))
    def test_read_host30(self):
        """
        Read the values of host30 by specifying the reference.
        """
        host30_d = read_host(ib_conn, host30["reference"], "ttl,comment")
        self.assertEqual(host30_d.get("ttl"), host30.get("ttl"))
        self.assertEqual(host30_d.get("comment"), host30.get("comment"))
    def test_read_host30_data(self):
        """
        Read the ip addresses of host30 by specifying the reference.
        """
        host30_data = read_host_data(ib_conn, host30["reference"])
        self.assertIsInstance(host30_data, list)
        self.assertEqual(len(host30_data), 1)
        self.assertEqual(host30_data[0], host30["ip-address"])
    def test_find_host30(self):
        """
        Verify host30 by using the find_host which returns a list of DNS host records that
        match the name field - which should be only one for a specified DNS view.
        """
        global host30_ipv4addrs
        response = find_host(ib_conn, host30["name"])
        self.assertEqual(response.status_code, 200)
        response_json_l = response.json()
        self.assertIsInstance(response_json_l, list)
        self.assertEqual(len(response_json_l), 1)
        host30_d = response_json_l[0]
        self.assertEqual(host30_d["_ref"], host30["reference"])
        host30_ipv4addrs = host30_d.get("ipv4addrs")
        self.assertIsInstance(host30_ipv4addrs, list)
        self.assertEqual(len(host30_ipv4addrs), 1)
        self.assertTrue(host30_ipv4addrs[0]["_ref"].startswith("record:host_ipv4addr"))
        self.assertTrue(host30_ipv4addrs[0]["_ref"].endswith("".join([":",host30["ip-address"],"/",host30["name"],"/default"])))
        self.assertEqual(host30_ipv4addrs[0].get("ipv4addr"), host30.get("ip-address"))
        self.assertEqual(host30_ipv4addrs[0].get("host"), host30.get("name"))
        self.assertFalse(host30_ipv4addrs[0]["configure_for_dhcp"])
        #print(host30_ipv4addrs[0])

class TestHost30Update(TestCase):
    """"""
    def test_update_host30_ttl(self):
        """
        Update the ttl value from the host30_update fixture.
        """
        response = update_host_ttl(ib_conn, host30["reference"], host30_update["ttl"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), host30["reference"])
        #print(response.json())
    def test_update_host30_comment(self):
        """
        Update the comment value from the host30_update fixture.
        """
        response = update_host_comment(ib_conn, host30["reference"], host30_update["comment"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), host30["reference"])
        #print(response.json())
    def test_update_host30_data(self):
        """
        Update the IP address from the host30_update fixture.
        """
        response = update_host_data(ib_conn, host30["reference"], [host30_update["ip-address"],])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), host30["reference"])
        #print(response.json())
        

class TestHost30Updated(TestCase):
    """"""
    def test_read_host30(self):
        """
        Verify the expected values of the ttl and comment fields.
        """
        host30_d = read_host(ib_conn, host30["reference"], "ttl,comment")
        self.assertEqual(host30_d.get("ttl"), host30_update.get("ttl"))
        self.assertEqual(host30_d.get("comment"), host30_update.get("comment"))
    def test_read_host30_data(self):
        """
        Verify the expected IP address of the updated host30.
        """
        host30_data = read_host_data(ib_conn, host30["reference"])
        self.assertIsInstance(host30_data, list)
        self.assertEqual(len(host30_data), 1)
        self.assertEqual(host30_data[0], host30_update["ip-address"])        
    
class TestDeleteHost(TestCase):
    """"""
    def test_create_host30(self):
        """
        Delete the newly created record:host host30 (ddi-host30.humana.com).
        """
        response = ib_conn.delete(host30["reference"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), host30["reference"])
    
class TestLogout(TestCase):
    """"""
    def test_logout_pass(self):
        """
        Logout out and verfiy that the session has ended.
        """
        ib_conn.logout()
        self.assertFalse(ib_conn.isloggedin)

#
# Run the test cases, in series, as a suite.
#

def suite():
    """
    Gather all the tests from this module in a test suite.
    """
    test_suite = TestSuite()
    test_suite.addTest(makeSuite(TestLogin))
    test_suite.addTest(makeSuite(TestHostIpAddressAvailable))
    test_suite.addTest(makeSuite(TestReadHost30NotFound))
    test_suite.addTest(makeSuite(TestCreateHost30))
    test_suite.addTest(makeSuite(TestHost30Created))
    test_suite.addTest(makeSuite(TestHost30Update))
    test_suite.addTest(makeSuite(TestHost30Updated))
    test_suite.addTest(makeSuite(TestDeleteHost))
    test_suite.addTest(makeSuite(TestLogout))
    return test_suite

mySuite=suite()

runner=TextTestRunner()


if __name__ == "__main__":
    """"""
    runner.run(mySuite)
