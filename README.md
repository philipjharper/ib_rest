# ib_rest
Infoblox REST API
# Introduction 
**Purpose:**
Provides a **Connection** class which stores the URL to an Infoblox REST API endpoint and the certificate bundle to for HTTP verification.

An instance of a **Connection** will enable **login** with API credentials, sending HTTP requests (GET, POST, PUT and DELETE) and, subsequent, **logoff** to the REST API.

Other Python modules provide info for connecting to specific REST API endpoints, unittesting for the **Connection** class and some utilities that access the REST API.


# Getting Started
**General usage**:

Use an instance of Connection to carry out a session with the specified Infoblox REST API.

The location of the REST API is passed as the **url** parameter which will be the DNS name of
the Grid Manager followed by WAPI/v#.## as detailed in the Infoblox *WAPI Documentation* accessed
from the Grid Manager Help menu.

In order to verify HTTPS use a certificate bundle consisting of the root and issuing CA certificates
together together in a text file.

A session would normally include a login to the REST API one or more HTTP method (get, post, put or
delete) calls and then a logout. There are examples of the HTTP method calls, for the **network** API
type in the unittest module (init_tst.py).

The HTTP method **get** has three versions:

Send a general **get** with parameters passed as key/value pairs. This returns a list of API objects,
of the specified API type, which satisfy the search criteria.

If the reference to the desired API object is known, it is efficient to use **get_by_reference** which
will return the specific API object, with field names and values, as a Python dict.

If a long list of API objects is expected in the response use **get_paged** for a more moderate impact
on the REST API.

The Infoblox REST conventions are: 

GET - search for and return API objects. An API reference is optional.

POST - create an API object.  A new reference is generated. The **data** parameter should be a Python
dict with the, at a minimum, the fields required by that API object type.

PUT - update an API object. The object reference is required.  Set the desired new values, for object
fields, as a Python dict in the **data** parameter.

DELETE - delete an API object. The object reference is required.  There are no other parameters needed.


# Build and Test
The unittest module to validate the basic functionality of the Connection class is:  init_tst.py.

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 
