"""
ib_rest - call the Infoblox REST API.

Author:  Philip Harper
Edited:  1/8/2025
"""
import requests


class NotLoggedInException(Exception):
    """"""
    def __init__(self):
        """"""
        self.message = "Log in before calling the API method!"
        super().__init__(self.message)


def loggedin_check(func):
    """
    If the wrapped instance method is called without the IB WAPI having
    already been logged in to raise the appropriate Exception.
    """
    def wrapped(*args, **kwargs):
        """"""
        if not args[0].isloggedin:
            raise NotLoggedInException
        return func(*args, **kwargs)
    return wrapped

        
class Connection:
    """
    A Connection instance will allow login and logout to an Infoblox REST
    API (WAPI), store the authentication and abstract the HTTP requests.
    """
    def __init__(self, url="", certificate_bundle=""):
        """"""
        self.url=""
        self.certificate_bundle=False
        self.session = requests.Session()
        self.schema = dict()
        self.response = None
        if url:
            self.initialize(url, certificate_bundle)
            
    def initialize(self, url:str, certificate_bundle:str):
        """
        Reset the target Grid Manager and HTTPS certificate bundle. 
        """
        self.url=url
        self.certificate_bundle = certificate_bundle if certificate_bundle else False
        
    def login(self, user:str, password:str):
        """
        Log in to the Infoblox Grid Manager REST API (WAPI) with API enabled credentials.  
        """
        if self.isloggedin:
            self.logout()
        self.response = self.session.get(self.url+"/?_schema", auth=(user,password), verify=self.certificate_bundle)
        if self.response.status_code == 200:
            self.schema.update(self.response.json())

    def logout(self):
        """
        Invalidate the stored session credentials and indicate that the previous login
        is now logged out.
        """
        self.response = self.session.post(self.url+"/logout")
        self.schema = dict()
        
    @property
    def isloggedin(self) -> bool:
        """
        Has this Connection been, successfully, logged into?
        """
        return bool(self.schema)
    
    @loggedin_check
    def get(self, wapi_type:str, params={}):
        """
        Send an HTTP GET request and return the response.
        """
        self.response = self.session.get(self.url+"/"+wapi_type, verify=self.certificate_bundle, params=params)
        return self.response
    
    @loggedin_check
    def get_by_reference(self, reference:str, params={}) -> dict:
        """
        If the WAPI object reference (_ref) has already been determined use that to
        get the specific WAPI object.
        Return the REST API object.
        """
        uri = self.url+"/"+reference
        self.response = self.session.get(uri, params=params)
        return self.response
    
    @loggedin_check
    def get_paged(self, wapi_type:str, params={}, page_size=20) -> list:
        """
        When a long list of objects is expected a paged query is prefered.
        """
        def add_objects():
            """
            Extend the list (wapi_objects_l) with the new page of WAPI objects.
            """
            self.response = self.get(wapi_type, get_parms)
            if self.response.status_code == 200:
                 wapi_objects_l.extend(self.response.json()["result"])
            else:
                print(self.response.status_code)
        wapi_objects_l = list()
        get_parms = dict()
        get_parms.update(params)
        page_params = {
            "_paging": "1",
            "_return_as_object": "1",
            "_max_results": page_size
            }
        get_parms.update(page_params)
        add_objects()
        while True:
            next_page_id = self.response.json().get("next_page_id")
            if next_page_id is None:
                break
            get_parms.update({"_page_id":next_page_id})
            add_objects()
        return wapi_objects_l

    @loggedin_check
    def stream(self, wapi_type:str, params={}, page_size=20):
        """
        When a long list of objects is expected generate in a stream.
        """
        def get_objects():
            """
            Set the list (wapi_objects_l) with the new page of WAPI objects.
            Yield from the resulting list
            """
            nonlocal wapi_objects_l
            self.response = self.get(wapi_type, get_parms)
            if self.response.status_code == 200:
                 wapi_objects_l = self.response.json()["result"]
            else:
                print(self.response.status_code)
        wapi_objects_l = list()
        get_parms = dict()
        get_parms.update(params)
        page_params = {
            "_paging": "1",
            "_return_as_object": "1",
            "_max_results": page_size
            }
        get_parms.update(page_params)
        get_objects()
        for wapi_object in wapi_objects_l:
            yield wapi_object
        
        while True:
            next_page_id = self.response.json().get("next_page_id")
            if next_page_id is None:
                break
            get_parms.update({"_page_id":next_page_id})
            get_objects()
            for wapi_object in wapi_objects_l:
                yield wapi_object


    
    @loggedin_check
    def post(self, wapi_type:str, data:dict, params={}, headers={}):
        """
        Send an HTTP POST request and return the response.
        """
        self.response = self.session.post(self.url+"/"+wapi_type, verify=self.certificate_bundle, json=data, params=params, headers=headers)
        return self.response
    
    @loggedin_check
    def put(self, reference:str, data:dict):
        """
        Send an HTTP PUT request and return the response.
        """
        self.response = self.session.put(self.url+"/"+reference, verify=self.certificate_bundle, json=data)
        return self.response
    
    @loggedin_check
    def delete(self, reference:str):
        """
        Send an HTTP DELETE request and return the response.
        """
        self.response = self.session.delete(self.url+"/"+reference)
        return self.response
        
    def __enter__(self):
        """
        Enable an instance of this class to be used as a Context Manager as
        long as the Connection is initialized with at least an URL.
        """
        if not self.url:
            raise UnitializedException
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        When exiting the Context Manager log out if logged in.
        """
        if self.isloggedin:
            self.logout()
        

if __name__ == "__main__":
    """"""
    from ltlddslta01_info import url, certificate_bundle
    import os
    with Connection(url=url, certificate_bundle=certificate_bundle) as ib_conn:
        ib_conn.login(os.environ["ib-account-ro"], os.environ["ib-password-ro"])
        #response = ib_conn.get("networkview", params={"name":"default"})
        #response = ib_conn.get("networkview", params={"is_default":"True"})
        #response = ib_conn.get_by_reference("networkview/ZG5zLm5ldHdvcmtfdmlldyQw:default/true")
        response = ib_conn.get("grid")
        print(response.json()[0])
        #response = ib_conn.get_by_reference(response.json()[0]["_ref"], params={"_return_fields":"name,allow_recursive_deletion"})
        #print(type(response))
        """
        print(ib_conn.isloggedin)
        for key, value in ib_conn.schema.items():
            print("{}\t{}\n".format(key, value))
        """
        #results = ib_conn.get_paged("zone_auth", page_size=200)
        """
        for dhcp_range in ib_conn.stream("range", params={"_return_fields":"network,member","server_association_type":"MEMBER"}):
            print(dhcp_range)
        """
        #print(len(results))
        """
        for result in results:
            print("zone:\t{}\tview:\t{}".format(result.get("fqdn"), result.get("view")))
        """

    if not ib_conn.isloggedin:
        print("logged out.")
