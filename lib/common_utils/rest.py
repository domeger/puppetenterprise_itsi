import json
import urllib2

from urlparse import urlparse
from ITOA.setup_logging import setup_logging

DEFAULT_LOGGER = setup_logging('puppetenterprise.log', 'rest')

class RESTClientValidationException(Exception):
    """
        Exception Class used for REST Client Validation Exceptions
    """
    pass

class RESTClientResponseException(Exception):
    """
        Exception Class used for REST Client Response Exceptions
    """
    pass

def validate_url(url, **kwargs):
    """
        URLs should all be validated, for now it only checks to make sure it uses
            a valid protocol (https)
        @param logger: <Logger>, An optional logger object that can be used to log
            information about requests
        @param url: <str>, A url we are going to send to
        @param auto_convert: <boolean> An optional value which controls whether or not we should
            automatically convert the url to use the https protocol

        @return: <str>, The validated url (may be auto corrected to use https)
        @raise: <RESTClientValidationException>, if the url does not use the https protocol
    """
    logger = kwargs.get('logger', DEFAULT_LOGGER)
    auto_convert = kwargs.get('auto_convert', False)
    if url.lower().startswith('https://'):
        return url
    elif auto_convert and url.lower().startswith('http://'):
        logger.info('action=VALIDATE_URL url=%s auto_convert=True', url)
        url = convert_to_https(url, logger=logger)
        return url
    raise RESTClientValidationException('URL must start with HTTPS')


def convert_to_https(url, **kwargs):
    """
        Converts the scheme in a url to https
        @param logger: <Logger>, An optional logger object that can be used to log
            information about requests
        @param url: <str>, A url we are going to send to

        @return: <str>, The validated url (may be auto corrected to use https)
        @raise: <RESTClientValidationException>, if the url does not use the https protocol
    """
    logger = kwargs.get('logger', DEFAULT_LOGGER)
    parts = urlparse(url)
    logger.info('action=CONVERT_TO_HTTPS url=%s scheme=%s', url, parts.scheme)
    return url.replace("http://", "https://")


class RESTClient(object):
    """
        Class used to make REST Calls in a validated fashion
    """

    def __init__(self, **kwargs):
        """
            @param logger: <Logger>, An optional logger object that can be used to log
                information about requests
            @param return_json: <boolean>, If true, the client will parse the response
                body as json and return the parsed value
        """
        self.logger = kwargs.get('logger', DEFAULT_LOGGER)
        self.return_json = kwargs.get('return_json', False)

    def _send_request(self, req, headers):
        """
            Makes the request and optionally parses the response as json
            @param req: <urllib2.Request>, A url request

            @return: <json|str|boolean>, False if the request failed,
                JSON if specified when constructing the client, otherwise the String response
        """
        try:
            for header in headers:
                req.add_header(header, headers.get(header))

            res = urllib2.urlopen(req)
            response_body = res.read()
            if self.return_json:
                response_body = json.loads(response_body)
            if res.code >= 200 and res.code < 300:
                return response_body
            self.logger.error('action=SEND_REQUEST code=%d body=%s', res.code, response_body)
            return False
        except urllib2.HTTPError, error:
            self.logger.error(
                'action=SEND_REQUEST error_code="%s" error_body:"%s"',
                error,
                error.read()
            )
            return False


    def get(self, url, **kwargs):
        """
            @param url: <str>, The url to send the request to
            @param query: <dict>, an optional map of query param key, value pairs
            @param headers: <dict>, an optional map of header key, value pairs
            @param force_https: <boolean>, an optional value that controls whether the url
                should automatically be converted to https

            @return: <json|str|boolean>, False if the request failed,
                JSON if specified when constructing the client, otherwise the String response
        """
        force_https = kwargs.get('force_https', False)
        # query = kwargs.get('query', {})
        headers = kwargs.get('headers', {})

        if force_https:
            url = convert_to_https(url, logger=self.logger)
        self.logger.info("action=GET url=%s", url)
        req = urllib2.Request(url)

        return self._send_request(req, headers)


    def post(self, url, **kwargs):
        """
            @param url: <str>, The url to send the request to
            @param body: <dict>, the optional payload to send as part of the request
            @param headers: <dict>, an optional map of header key, value pairs
            @param force_https: <boolean>, an optional value that controls whether the url
                should automatically be converted to https

            @return: <json|str|boolean>, False if the request failed,
                JSON if specified when constructing the client, otherwise the String response
        """
        force_https = kwargs.get('force_https', False)
        body = kwargs.get('body', {})
        headers = kwargs.get('headers', {})

        if force_https:
            url = convert_to_https(url, logger=self.logger)
        self.logger.info("action=POST url=%s", url)
        req = urllib2.Request(url, body)

        return self._send_request(req, headers)
