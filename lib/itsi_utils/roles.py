from common_utils.rest import RESTClient

# import ITSI libraries
from ITOA.setup_logging import setup_logging

DEFAULT_LOGGER = setup_logging('puppetenterprise.log', 'util')

ITSI_ROLES = [
    'itoa_user',
    'itoa_analyst',
    'itoa_admin'
]

def has_role(user_roles, roles_to_check):
    """
        Compares two lists of strings to see if they have any overlap
        @param user_roles: <list[str]> the roles of the user we are checking
        @param roles_to_check: <list[str]> the set of roles we want to find
        @return: <bool> True, if there is overlap between the two lists, false otherwise

    """
    for role_to_check in roles_to_check:
        if role_to_check in user_roles:
            return True
    return False

def is_itsi_user(server_uri, session_key, username, **kwargs):
    """
        Checks to see if the user exists in Splunk with one of the necessary ITSI Roles
        @param server_uri: <str> the domain of the splunk server
        @param session_key: <str> a valid session key for the splunk server
        @param username: <str> the username of the user we are validating
        @return: <bool> True, if the user exists and has one of the ITIS roles, false otherwise

    """
    logger = kwargs.get('logger', DEFAULT_LOGGER)
    logger.info('action=IS_ITSI_USER server_uri=%s username=%s', server_uri, username)

    rest = RESTClient(return_json=True, logger=logger)
    url_template = '%s/services/authentication/users/%s?output_mode=json'
    url = url_template % (server_uri, username)
    headers = {'Authorization': 'Splunk %s' % session_key}

    logger.info('action=GET_USER request_url=%s', url)
    response_body = rest.get(url, headers=headers)
    if response_body:
        roles = response_body['entry'][0]['content']['roles']
        if has_role(roles, ITSI_ROLES):
            return True
        # else:
        logger.warn(
            'warning=INVALID_USER username=%s roles=%s valid_roles=%s',
            username,
            ','.join(roles),
            ','.join(ITSI_ROLES)
        )
        return False
    # else:
    logger.warn(
        'warning=%s username=%s message="%s"'
        'CHECK_USER_FAILED',
        username,
        'Unable to find user'
    )
    return False
