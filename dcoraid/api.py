import copy
import json

import requests


class APIKeyError(BaseException):
    pass


class CKANAPI():
    def __init__(self, server, api_key):
        """User-convenient interface to the CKAN API"""
        self.api_key = api_key
        self.api_url = self._make_api_url(server)
        self.headers = {"Authorization": api_key}

    def _make_api_url(self, url):
        """Generate a complete CKAN API URL

        Any given string is changed to yield the
        form "https://domain.name/api/2/action".
        """
        if not url.count("//"):
            url = "https://" + url
        if not url.endswith("/action/"):
            url = url.rstrip("/") + "/api/3/action/"
        return url

    def get(self, api_call, **kwargs):
        """GET request

        Parameters
        ----------
        api_call: str
            An API call function (e.g. "package_show")
        kwargs: dict
            Any keyword arguments to the API call
            (e.g. `name="test-dataset"`)

        Returns
        -------
        result: dict
            Result of the API call converted to a dictionary
            from the returned json string
        """
        if kwargs:
            # Add keyword arguments
            kwv = []
            for kw in kwargs:
                kwv.append("{}={}".format(kw, kwargs[kw]))
            api_call += "?" + "&".join(kwv)
        url_call = self.api_url + api_call
        req = requests.get(url_call, headers=self.headers)
        data = req.json()
        if not data["success"]:
            raise ConnectionError(
                "Could not run API call '{}'! ".format(url_call)
                + "Reason: {} ({})".format(req.reason,
                                           data["error"]["message"]))
        return data["result"]

    def post(self, api_call, data, dump_json=True, headers={}):
        """POST request

        Parameters
        ----------
        api_call: str
            An API call function (e.g. "package_create")
        data: dict, MultipartEncoder, ...
            The data connected to the post request. For
            "package_create", this would be a dictionary
            with the dataset name, author, license, etc.
        dump_json: bool
            If True (default) dump `data` into a json string.
            If False, `data` is not touched.
        headers: dict
            Additional headers (updates `self.headers`) for the
            POST request (used for multipart uploads).

        Returns
        -------
        result: dict
            Result of the API call converted to a dictionary
            from the returned json string
        """
        new_headers = copy.deepcopy(self.headers)
        new_headers.update(headers)
        if dump_json:
            if "Content-Type" in headers:
                raise ValueError("Do not specify 'Content-Type' with "
                                 + "`dump_json=True`!")
            # This is necessary because we cannot otherwise
            # create packages with tags (list of dicts);
            # We have to json-dump the dict.
            new_headers["Content-Type"] = "application/json"
            data = json.dumps(data)

        url_call = self.api_url + api_call
        req = requests.post(url_call,
                            data=data,
                            headers=new_headers)
        data = req.json()
        if not data["success"]:
            raise ConnectionError(
                "Could not run API call '{}'! ".format(url_call)
                + "Reason: {} ({})".format(req.reason,
                                           data["error"]["message"]))
        return data["result"]

    def get_user_dict(self):
        """Return the current user data dictionary

        The user name is inferred from the API key.
        """
        # Workaround for https://github.com/ckan/ckan/issues/5490
        # Get the user that has a matching API key
        data = self.get("user_list")
        for user in data:
            if user.get("apikey") == self.api_key:
                userdata = user
                break
        else:
            raise APIKeyError(
                "Could not determine user data. Please check API key.")
        return userdata