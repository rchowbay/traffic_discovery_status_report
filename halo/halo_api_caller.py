import base64
import json
import urllib.parse
import urllib.request
import cloudpassage
from halo.utility import Utility


class HaloAPICaller(object):
    """This Class contains all functions that are calling HALO services through APIs"""

    def __init__(self, config):
        self.halo_api_auth_url = config.halo_api_auth_url
        self.halo_api_auth_args = config.halo_api_auth_args
        self.halo_api_hostname = config.halo_api_hostname
        self.halo_api_version = config.halo_api_version
        self.halo_api_port = int(config.halo_api_port)
        self.halo_api_key_id = config.halo_api_key_id
        self.halo_api_key_secret = config.halo_api_key_secret
        self.halo_api_auth_token = config.halo_api_auth_token
        self.output_directory = config.output_directory
        self.halo_group_id = config.halo_group_id
        self.halo_group_td_status = config.halo_group_td_status

    # Dump debug info
    @classmethod
    def dump_token(cls, token, expires):
        if token:
            Utility.log_stdout("AuthToken=%s" % token)
        if expires:
            Utility.log_stdout("Expires in %s minutes" % (expires / 60))

    @classmethod
    def get_http_status(cls, code):
        if code == 200:
            return "OK"
        elif code == 401:
            return "Unauthorized"
        elif code == 403:
            return "Forbidden"
        elif code == 404:
            return "Not found"
        elif code == 422:
            return "Validation failed"
        elif code == 500:
            return "Internal server error"
        elif code == 502:
            return "Gateway error"
        else:
            return "Unknown code [%d]" % code

    # add authentication token into the request
    @classmethod
    def add_auth(cls, req, kid, sec):
        combined = kid + ":" + sec
        combined_bytes = combined.encode("utf-8")
        encoded = base64.b64encode(combined_bytes)
        encoded_str = encoded.decode("utf-8")
        req.add_header("Authorization", "Basic " + encoded_str)

    def get_auth_token(self, url, args, kid, sec):
        req = urllib.request.Request(url)
        self.add_auth(req, kid, sec)
        if args:
            args = urllib.parse.urlencode(args).encode("utf-8")
        try:
            fh = urllib.request.urlopen(req, data=args)
            return fh.read()
        except IOError as e:
            if hasattr(e, 'reason'):
                Utility.log_stderr(
                    "Failed to connect [%s] to '%s'" % (e.reason, url))
            elif hasattr(e, 'code'):
                msg = self.get_http_status(e.code)
                Utility.log_stderr(
                    "Failed to authorize [%s] at '%s'" % (msg, url))
                data = e.read()
                if data:
                    Utility.log_stderr("Extra data: %s" % data)
                Utility.log_stderr(
                    "Likely cause: incorrect API keys, id=%s" % kid)
            else:
                Utility.log_stderr("Unknown error fetching '%s'" % url)
            return None

    def get_event_batch(self, url):
        return self.do_get_request(url, self.halo_api_auth_token)

    def do_get_request(self, url, token):
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + token)
        try:
            fh = urllib.request.urlopen(req)
            return fh.read(), False
        except IOError as e:
            auth_error = False
            if hasattr(e, 'reason'):
                Utility.log_stderr(
                    "Failed to connect [%s] to '%s'" % (e.reason, url))
            elif hasattr(e, 'code'):
                msg = self.get_http_status(e.code)
                Utility.log_stderr(
                    "Failed to fetch events [%s] from '%s'" % (msg, url))
                if e.code == 401:
                    auth_error = True
            else:
                Utility.log_stderr("Unknown error fetching '%s'" % url)
            return None, auth_error

    def authenticate_client(self):
        url = "%s:%d/%s" % (self.halo_api_hostname,
                            self.halo_api_port, self.halo_api_auth_url)
        response = self.get_auth_token(
            url, self.halo_api_auth_args, self.halo_api_key_id, self.halo_api_key_secret)
        if response:
            auth_resp_obj = json.loads(response)
            if 'access_token' in auth_resp_obj:
                self.halo_api_auth_token = auth_resp_obj['access_token']
            if 'expires_in' in auth_resp_obj:
                self.expires = auth_resp_obj['expires_in']
        return self.halo_api_auth_token

    def get_all_groups(self):
        url = "%s:%d/%s/groups" % (
            self.halo_api_hostname, self.halo_api_port, self.halo_api_version)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error

    def get_group_childs(self, group_id):
        url = "%s:%d/%s/groups?parent_id=%s" % (
            self.halo_api_hostname, self.halo_api_port, self.halo_api_version, group_id)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error

    def get_group_td_status(self, group_id):
        url = "%s:%d/v2/groups/%s/scanner_settings" % (
            self.halo_api_hostname, self.halo_api_port, group_id)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error
    
    def get_group_details(self, group_id):
        url = "%s:%d/v2/groups/%s" % (
            self.halo_api_hostname, self.halo_api_port, group_id)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error

    def get_all_groups_per_page(self, page):
        url = "%s:%d/%s/groups&per_page=100&page=%s" % (
            self.halo_api_hostname, self.halo_api_port, self.halo_api_version, page)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error

    def get_group_childs_per_page(self, group_id, page):
        url = "%s:%d/%s/groups?parent_id=%s&per_page=100&page=%s" % (
            self.halo_api_hostname, self.halo_api_port, self.halo_api_version, group_id, page)
        (data, auth_error) = self.do_get_request(url, self.halo_api_auth_token)
        if data:
            return json.loads(data), auth_error
        else:
            return None, auth_error

    def credentials_work(self):
        """
        Attempts to authenticate against Halo API
        """
        good = True
        try:
            self.authenticate_client()
        except cloudpassage.CloudPassageAuthentication:
            good = False
        return good
