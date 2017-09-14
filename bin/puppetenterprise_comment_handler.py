import sys
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication
sys.path.append(make_splunkhome_path(['etc', 'apps', 'puppetenterprise_itsi', 'lib']))
sys.path.append(make_splunkhome_path(['etc', 'apps', 'SA-ITOA', 'lib']))
from handler_utils.pe_handler import PuppetEnterpriseHandler
from ITOA.setup_logging import setup_logging
from itsi.event_management.sdk.eventing import Event

REST_HANDLER_LOG = 'puppetenterprise_itsi_rest.log'
DEFAULT_LOGGER = setup_logging(REST_HANDLER_LOG, 'puppetenterprise.handlers.comment')

REQUIRED_FIELDS = [
    'event_id',
    'message',
]

class CommentHandler(PuppetEnterpriseHandler, PersistentServerConnectionApplication):

    def __init__(self, command_line, command_arg):
        """
            initialize the object. parameters are unused
        """
        super(CommentHandler, self).__init__(command_line, command_arg, logger=DEFAULT_LOGGER)
        PersistentServerConnectionApplication.__init__(self)
        self.required_fields = REQUIRED_FIELDS

    def return_success(self):
        """
            builds a success response object

            @returns: <object> A response object
        """
        success_message = 'Successfully added comment'
        return self.build_response(
            200,  # HTTP status code
            {     # Payload of the request.
                'message': success_message
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
        message = input_payload.get('message')

        session_key = kwargs.get('session_key')

        self.logger.info(
            'action=PROCESS_COMMENT event_id=%s children=%s message="%s"',
            event_id,
            children,
            message
        )

        event = Event(session_key, logger=self.logger)
        event.create_comment(event_id, message)
        return self.return_success()
