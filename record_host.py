"""
record_host - DNS resource record operations for the WAPI object type record:host.
"""
from ib_rest import Connection
from ipaddress import ip_address
from requests.models import Response


def isipavailable(ib_connection: Connection, ip_s: str, network_view="default") -> bool:
    """
    Return True if a record:host is not, currently, configured with this IP address.
    Note only tests for record:host type; a configured record:a type will not be detected.
    """
    response = ib_connection.get("record:host_ipv4addr", params={"ipv4addr":ip_address(ip_s).compressed, "network_view":network_view})
    return not response.json()


def format_host_data(ip_addresses: list) -> list:
    """
    Return a list of IP address objects with the format required for creating or
    updating a DNS host record.
    """
    return [{"ipv4addr":ip_address(ip_s).compressed} for ip_s in ip_addresses]


def read_host(ib_connection: Connection, reference: str, fields="") -> dict:
    """
    Return a representation of the record:host WAPI object with the requested return fields.
    """
    return_fields = {}
    if fields:
        return_fields.update({"_return_fields":fields})
    response = ib_connection.get_by_reference(reference, params=return_fields)
    if response.status_code == 200:
        return response.json()
    #print(response.text)
    return {}


def read_host_data(ib_connection: Connection, reference: str) -> list:
    """
    Return the list of IP addresses, currently, assigned to the referenced host record.
    """
    response = ib_connection.get_by_reference(reference, params={"_return_fields":"ipv4addrs"})
    if response.status_code == 200:
        return [ipaddr.get("ipv4addr", "") for ipaddr in response.json().get("ipv4addrs", [])]
    return []

    
def create_host(ib_connection: Connection, name: str, data: list, ttl=0, comment="") -> Response:
    """
    Create a new record:host object in DNS with the name (FQDN) with the list of one or more
    IP addresses.
    """
    host_d = {"name":name,"ipv4addrs":format_host_data(data),"view": "default"}
    if ttl:
        host_d.update({"ttl":ttl})
    if comment:
        host_d.update({"comment":comment})
    return ib_connection.post(
        "record:host",
        data=host_d
        )


def find_host(ib_connection: Connection, name: str, view="default") -> Response:
    """
    Search for a record:host object with a provided name (FQDN).  The returned Response
    object will contain 0 or 1 record:host objects that match the name (FQDN).
    """
    return ib_connection.get("record:host", params={"name":name, "view": view})


def update_host_data(ib_connection: Connection, reference: str, data: list) -> Response:
    """
    Update the list of IP addresses assigned to the referenced record:host.
    """
    return ib_connection.put(reference, {"ipv4addrs": format_host_data(data)})


def update_host_ttl(ib_connection: Connection, reference: str, ttl: int) -> Response:
    """
    Update the ttl configured for the referenced record:host.
    """
    return ib_connection.put(reference, {"ttl": ttl})


def update_host_comment(ib_connection: Connection, reference: str, comment: str) -> Response:
    """
    Update the comment configured for the referenced record:host.
    """
    return ib_connection.put(reference, {"comment": comment})

    
    
if __name__ == "__main__":
    """"""
    from ltlddslta01_info import url, certificate_bundle
    import os
    ib_conn = Connection(url=url, certificate_bundle=certificate_bundle)
    ib_conn.login(os.environ["TECHLAB_ACCOUNT"],os.environ["TECHLAB_PASSWORD"])

    host_reference = ""
    
    #response = create_host(ib_conn, "ddi-host1.humana.com", ["10.32.15.30",], ttl=600, comment="DDI Host 1")
    #response = ib_conn.get_by_reference('record:host/ZG5zLmhvc3QkLjEwLmNvbS5odW1hbmEuZGRpLWhvc3Qx:ddi-host1.humana.com/default')
    response = find_host(ib_conn, "ddi-host1.humana.com")


    """
    if response.status_code in (200, 201):
        host_reference = response.json()[0]["_ref"]
    """
    
    #"""
    if response.status_code == 200:
        host_reference = response.json()[0]["_ref"]
    #"""   
    #print(host_reference)

    """
    if host_reference:
        response = update_host_ttl(ib_conn, host_reference, 60)
    """
    #"""
    if host_reference:
        response = update_host_data(ib_conn, host_reference, ["10.32.15.31","10.32.15.32"])
    #"""
    #print(isipavailable(ib_conn, "10.32.15.27"))
    
    print(response.json())
    
    """
    if response.json():
        print(response.json()[0]["_ref"])
    """
    """
    if host_reference:
        ip_addresses = read_host_data(ib_conn, host_reference)
        print(ip_addresses)
    """
    """
    if host_reference:
        host = read_host(ib_conn, host_reference, "ttl,view,network_view")
        print(host)
    """   
    ib_conn.logout()

    if not ib_conn.isloggedin:
        print("logged out.")
