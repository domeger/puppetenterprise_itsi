import sys

from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication
sys.path.append(make_splunkhome_path(['etc', 'apps', 'puppetenterprise_itsi', 'lib']))
sys.path.append(make_splunkhome_path(['etc', 'apps', 'SA-ITOA', 'lib']))
from handler_utils.pe_handler import PuppetEnterpriseHandler
from itsi_utils.roles import is_itsi_user
from itsi_utils.app import get_itsi_version
from ITOA.setup_logging import setup_logging
from itsi.event_management.sdk.eventing import Event

# The name of the log file to write to
REST_HANDLER_LOG = 'puppetenterprise_itsi_rest.log'
DEFAULT_LOGGER = setup_logging(REST_HANDLER_LOG, 'puppetenterprise.handlers.response')

REQUIRED_FIELDS = [
    'event_id',
    'owner',
    'response',
    'message',
]

STATUS_NO_CHANGE = 'NO_CHANGE'

RESPONSE_TO_STATUS = {
    'acknowledge': '2',
    'resolve': '4',
    'close': '5',
    'escalate': STATUS_NO_CHANGE
}

UPDATE_UNSUPPORTED_VERSIONS = [
    '2.6.0'
]

class ResponseHandler(PuppetEnterpriseHandler, PersistentServerConnectionApplication):
    """
        This class extends the PersistentServerConnectionApplication and is used to
        update notable events Status/Owner and add a commennt
    """
    def __init__(self, command_line, command_arg):
        """
            initialize the object. parameters are unused
        """
        super(ResponseHandler, self).__init__(command_line, command_arg, logger=DEFAULT_LOGGER)
        PersistentServerConnectionApplication.__init__(self)
        self.required_fields = REQUIRED_FIELDS

    def update_event(self, event, event_id, status, owner):
        """
            Safely updates the event's status and owner if either is valid
            @param event: <EventMeta> an instance of EventMeta from the Notable Events SDK
            @param event_id: <str>|<list> an id or list of Notable Event IDs you wish to update
            @param status: <str>|<None> the status to transition the event(s) to
            @param owner: <str>|<None> the owner to assign the event(s) to
            @return: <bool> True, if the update was successful
        """
        is_update_successful = False
        try:
            update_blob = {
                'event_ids': event_id
            }
            should_send = False
            if status is not None:
                update_blob['status'] = status
                should_send = True
            if owner is not None:
                update_blob['owner'] = owner
                should_send = True

            if should_send:
                event.update(update_blob)
                is_update_successful = True
            else:
                code = 'NO_EVENT_UPDATE'
                message = 'no change to status and owner'
                self.logger.warn(
                    'warning=%s message="%s"',
                    code,
                    message
                )
                is_update_successful = True
# pylint: disable = broad-except
        except Exception, exception:
            code = 'UPDATE_EVENT_ERROR'
            message = 'Unable to update event due to sdk error'
            self.logger.error(
                'error=%s message="%s"',
                code,
                message
            )
            self.logger.exception(exception)
# pylint: enable = broad-except

        return is_update_successful

    def get_status(self, response):
        """
            Gets the status that the response is mapped to
            @param response: <str> the response from PuppetEnterprise
            @return: <str>|<None> if the response is valid it will return a status, otherwise None
        """
        response_lower = response.lower()
        status = RESPONSE_TO_STATUS.get(response_lower)
        if not status:
            self.logger.error(
                'error=INVALID_RESPONSE response=%s valid_responses=%s',
                response_lower,
                ",".join(RESPONSE_TO_STATUS.keys())
            )
        elif status == STATUS_NO_CHANGE:
            status = None
        return status

    def build_success_response(self, owner, status):
        """
            @param owner: <str|None> The username of the new owner
            @param status: <str> The new status of the Notable Event

            @returns: <object> A response object
        """
        return self.build_response(
            200,  # HTTP status code
            {    # Payload of the request.
                'message': 'Successfully handled event response',
                'is_update_successful': True,
                'owner': owner,
                'status': status
            }
        )


    def process_request(self, input_payload, **kwargs):
        """
            Overrides PuppetEnterpriseHandler
            @param input_payload: <object> The request payload in object form
            @param method: <str> The HTTP Method (should be all caps) <kwargs>
            @param session_key: <str> The Splunk session key <kwargs>
            @param server_rest_uri: <str> The Splunk Server base url <kwargs>

            @returns: <object> A response object, likely made by self.build_response
        """
        event_id = input_payload.get('event_id')
        children = input_payload.get('children')
        owner = input_payload.get('owner')
        response = input_payload.get('response')
        message = input_payload.get('message')

        session_key = kwargs.get('session_key')
        server_rest_uri = kwargs.get('server_rest_uri')

        status = self.get_status(response)
        self.logger.info(
            'event_id=%s children=%s owner=%s message="%s" response=%s status=%s',
            event_id,
            ",".join(children),
            owner,
            message,
            response,
            status
        )

        event = Event(session_key, logger=self.logger)

        if owner is not None:
            if is_itsi_user(server_rest_uri, session_key, owner, logger=self.logger) is False:
                owner = None

        itsi_version = get_itsi_version(server_rest_uri, session_key)
        if itsi_version in UPDATE_UNSUPPORTED_VERSIONS:
            event.create_comment(event_id, message)
            warning_message = 'unable to update owner and status due to version'
            self.logger.warn(
                'warning=%s message="%s" version=%s',
                'LIMITED_FUNCTIONALITY',
                warning_message,
                itsi_version
            )
            return self.build_success_response(owner, status)
        else:
            event.create_comment(event_id, message)
            if self.update_event(event, event_id, status, owner):
                return self.build_success_response(owner, status)
            # else:
            return_message = 'A problem occured while acknowledging these Notable Events.'
            return_message += ' Review the %s for more details.' % REST_HANDLER_LOG
            event.create_comment(event_id, return_message)
            return self.build_response(
                400,  # HTTP status code
                {    # Payload of the request.
                    'message': return_message,
                    'is_update_successful': False
                }
            )
