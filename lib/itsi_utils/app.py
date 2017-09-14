"""
    A utility for getting information about the ITSI local app
"""
from common_utils.rest import RESTClient

# import ITSI libraries
from ITOA.setup_logging import setup_logging
# pylint: enable = import-error

DEFAULT_LOGGER = setup_logging('puppetenterprise.log', 'util')

ITSI_APP_NAME = 'SA-ITOA'

def get_itsi_version(server_uri, session_key, **kwargs):
    """
        Gets the version of the ITSI application
        @param server_uri: <str> the domain of the splunk server
        @param session_key: <str> a valid session key for the splunk server
        @return: <str|bool> If the app can be found it returns the version string, false otherwise

    """
    logger = kwargs.get('logger', DEFAULT_LOGGER)
    logger.info('action=GET_ITSI_VERSION server_uri=%s app_name=%s', server_uri, ITSI_APP_NAME)

    rest = RESTClient(return_json=True, logger=logger)
    url_template = '%s/services/apps/local/%s?output_mode=json'
    url = url_template % (server_uri, ITSI_APP_NAME)
    headers = {'Authorization': 'Splunk %s' % session_key}

    logger.info('action=GET_APP request_url=%s', url)
    response_body = rest.get(url, headers=headers)
    if response_body:
        return response_body['entry'][0]['content']['version']
    # else:
    logger.warn(
        'warning=%s app-name=%s message="%s"'
        'GET_ITSI_VERSION_FAILED',
        ITSI_APP_NAME,
        'Unable to find local app'
    )
    return False
