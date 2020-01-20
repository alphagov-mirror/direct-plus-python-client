from requests.exceptions import RequestException


class DirectPlusError(RequestException):
    """
    """
    def __init__(self, *args, **kwargs):
        response = kwargs.get('response', None)
        if (
            response is not None
        ) and (
            hasattr(response, 'status_code')
        ) and (
            response.status_code == 200
        ) and (
            'error' in response.json()
        ):
            (self.api_error_code, self.api_error_mesage) = response.json()['error'].split(':')
        super(DirectPlusError, self).__init__(*args, **kwargs)
