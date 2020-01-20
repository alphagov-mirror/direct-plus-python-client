import logging
import requests


class DnBClient(object):
    """
    """
    def __init__(
        self,
        username,
        password,
        logger=None,  # optional Logger object
        raise_for_api_errors=True,  # if False will not raise D&B API errors
        raise_for_status=False,  # if True will raise HTTPError for 400 <= status_code < 600
    ):
        """
        """
        # store the params in object
        self.username = username
        self.password = password
        self.logger = logger if logger else logging.getLogger(__name__)
        self.raise_for_api_errors = raise_for_api_errors
        self.raise_for_status = raise_for_status
        # requests constants
        self.access_token = None
        self.protocol = 'https'
        self.domain = 'plus.dnb.com'
        self.headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }

    def _get_access_token(self):
        """
        """
        response = requests.post(
            f'{self.protocol}://{self.domain}/v2/token',
            json={'grant_type': 'client_credentials'},
            auth=requests.auth.HTTPBasicAuth(
                username=f'{self.username}',
                password=f'{self.password}',
            ),
            headers=self.headers
        )
        # TODO: handle failure to obtain a token
        self.access_token = response.json().get('access_token')
        if self.access_token:  # store token and update the headers
            self.headers['authorization'] = f'Bearer {self.access_token}'
            return self.access_token

    def _dnb_request(self, method, version, endpoint, payload={}):
        """
        """
        if self.access_token is None:
            self.access_token = self._get_access_token()
        url = f'{self.protocol}://{self.domain}/{version}/{endpoint}'
        if method == 'get':
            response = requests.get(url, headers=self.headers, params=payload)
        else:
            response = getattr(requests, method)(url, headers=self.headers, data=payload)
        if response.status_code != 200:
            raise NotImplementedError  # TODO: raise appropriate exception
        if 'error' in response.json() and response.json()['error']['errorCode'] == '00040':
            self.access_token = self._get_access_token()
            # recursively retry the request
            response = self._dnb_request(method, version, endpoint, payload)
        else:
            return response.json()

    def supplier_details(self, duns_number):
        """
        """
        # make the request to the D&B API
        response = self._dnb_request(
            'get', 'v1', f'data/duns/{duns_number}', payload={'productId': 'cmpelk', 'versionId': 'v2'}
        )
        # TODO: if 'error' in response: handle common errors
        # TODO: flatten and format response
        return response

    def find_supplier(self, payload={}):
        """
        https://directplus.documentation.dnb.com/openAPI.html?apiID=IDRCleanseMatch
        """
        # required parameters
        if not ('duns' not in payload or 'countryISOAlpha2Code' not in payload):
            raise  # TODO: find appropriate error
        # reasonable defaults below
        if 'candidateMaximumQuantity' not in payload:
            payload['candidateMaximumQuantity'] = 100  # maximum allowed
        if 'confidenceLowerLevelThresholdValue' not in payload:
            payload['confidenceLowerLevelThresholdValue'] = 1  # minimum allowed
        # make the request to the D&B API
        response = self._dnb_request('get', 'v1', 'match/cleanseMatch', payload=payload)
        if 'error' in response and response['error']['errorCode'] == '20505':
            return []
        suppliers = []
        for candidate in response['matchCandidates']:
            # TODO: reduce (by response_keys), flatten and format the respone
            suppliers.append(candidate)
        return response
