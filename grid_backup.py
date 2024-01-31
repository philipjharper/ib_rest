"""
grid_backup - program to download the most recent backup file from the Infoblox WAPI. 
"""
from ib_rest import Connection
from requests import get, post
import os
from ib_rest.ltlddslta01_info import url, certificate_bundle
"""
grid = "https://ltlddslta01.loutms.tree/"
wapi_version = "wapi/v2.12"
url = grid+wapi_version
certificate_bundle = "c:\cert\certificate_bundle3.txt"
"""

def fetch_backup_token(ib_connection) -> dict:
    """
    Perform the Infoblox REST API file operation (fileop) to
    generate a token and URL for the requested copy of the stored
    Grid backup file.
    """
    headers = {"Content-Type":"application/json"}
    result = {"result": False}
    response = ib_connection.post(
        "fileop",
        {"type": "BACKUP"},
        params={"_function":"getgriddata"},
        headers=headers
        )
    if response.status_code == 200:
        result.update({"result": True, "data": response.json()})
    else:
        result.update({"message": response.text})
    return result


def force_download(file_url, local_file_path):
    """
    Get the content of the request ignoring the MIME type.
    Perform a binary copy into the specified filepath.
    """
    import urllib3
    import warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"Content-type":"application/force-download"}
    response = get(
        file_url,
        headers=headers,
        verify=False,
        auth=("ddiapi_superuser",os.environ["TECHLAB_PASSWORD"])
        )
    try:
        with open(local_file_path, "wb") as bakfile:
            bakfile.write(response.content)
        #print("Download is done.")
    except PermissionError as e:
        """print(e)"""
    warnings.resetwarnings()
    return response


def send_download_complete(ib_connection, token) -> dict:
    """
    Send the download complete message to Infoblox REST API for cleanup.
    """
    headers = {"Content-Type":"application/json"}
    result = {"result": False}
    response = ib_connection.post(
        "fileop",
        {"token": token},
        params={"_function":"downloadcomplete"},
        headers=headers
        )
    if response.status_code == 200:
        result.update({"result": True})
    else:
        result.update({"message": response.text})
    return result


def parse_file_url(file_url: str) -> tuple:
    """
    Parse the file_url, from the Infoblox REST API (WAPI), to create the
    folder and filename path to receive the downloaded file contents. 
    """
    url_l = file_url.split("/")
    return url_l[4][16:], url_l[5]

    
def download(ib_connection, backup_folder_path) -> dict:
    """
    Perform the steps:
    1) fetch backup token.
    2) force download.
    3) send download complete.

    in order to download a copy of the backup file stored, locally, on
    the Infoblox Grid Master.
    """
    token = ""
    file_url = ""
    token_d = fetch_backup_token(ib_connection)
    if token_d["result"]:
        token = token_d["data"]["token"]
        print(token)
        file_url = token_d["data"]["url"]
        print(file_url)
    if token:
        file_url_parts = parse_file_url(file_url)
        directory = os.path.join(backup_folder_path, file_url_parts[0])
        os.makedirs(directory, exist_ok=True)
        bakfile_p = os.path.join(directory, file_url_parts[1])
        response = force_download(file_url, bakfile_p)
        return send_download_complete(ib_conn, token)
    return {"result": False, "message": "Download not completed."}
    
if __name__ == "__main__":
    """"""
    #from ltlddslta01_info import url, certificate_bundle
    from dhcpadmin_info import url, certificate_bundle
    import time

    start_time = time.time()
    
    ib_conn = Connection(url=url, certificate_bundle=certificate_bundle)
    #ib_conn.login(os.environ["TECHLAB_ACCOUNT"],os.environ["TECHLAB_PASSWORD"])
    ib_conn.login("ddiapi_superuser","<M1>")

    folder_p = "c:\\infoblox\\backup\\"
    #
    result = download(ib_conn, folder_p)
    print(result)
    #
    ib_conn.logout()
    if not ib_conn.isloggedin:
        print("logged out.")

    print("{:.2f} seconds.".format(time.time() - start_time))
