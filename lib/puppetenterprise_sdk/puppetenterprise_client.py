"""
    Includes the Puppet Enterprise class which supports calls to the Puppet API.
    Currently only supports sending events.
"""
import base64

from common_utils.rest import RESTClient

# import ITSI libraries
from ITOA.setup_logging import setup_logging
# pylint: enable = import-error

DEFAULT_LOGGER = setup_logging('puppetenterprise.log', 'puppetenterprise_client')

class PuppetEnterpriseClient(object):
    """
        Class used to make calls to Puppet Enterprise API. Currently only supports sending events to a url
    """

    def __init__(self, **kwargs):
        """
            Constructor, takes no params
        """
        self.logger = kwargs.get('logger', DEFAULT_LOGGER)
        self.headers = {}
        self.add_header('Content-Type', 'application/json')

    def add_credentials(self, username, password):
        """
            Adds an authentication header using Basic Auth with the username and password
            @param username: <str> The username in puppetenterprise
            @param password: <str> The password in puppetenterprise
        """
        self.logger.info('action=ADD_CREDENTIALS username=%s', username)

        # Build the auth string
        base_64_str = base64.b64encode('%s:%s' % (username, password))
        self.add_header('Authorization', 'Basic %s' % base_64_str)

    def add_header(self, key, value):
        """
            Add a header to every request that goes through the client
            @param key: <str> the header name
            @param value: <str> the header value
        """
        self.headers[key] = value

    def send_event(self, url, puppetenterprise_event):
        """
            Sends an puppetenterprise_event to the specified url with the client's configuration
            @param url: <str> The inbound integration url
            @param puppetenterprise_event <PuppetEnterprise> The event to send to puppetenterprise
            @return <str> | False If successful, it will return the requestId from the response
        """
        self.logger.info('action=SEND_EVENT url=%s puppetenterprise_event_type=%s', url, type(puppetenterprise_event))
        rest = RESTClient(return_json=True, logger=self.logger)

        response_body = rest.post(
            url,
            headers=self.headers,
            body=puppetenterprise_event.get_json_payload(),
            force_https=True
        )
        if response_body:
            return response_body['requestId']
        return False
