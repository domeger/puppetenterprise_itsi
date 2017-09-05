"""
    This file is used for Puppet Enterprise Splunk ITSI Notable Event Alert Actions
"""
import sys

# pylint: disable = import-error
# pylint: disable = wrong-import-position
from splunk.clilib.bundle_paths import make_splunkhome_path

sys.path.append(make_splunkhome_path(['etc', 'apps', 'puppetenterprise_itsi', 'lib']))
sys.path.append(make_splunkhome_path(['etc', 'apps', 'SA-ITOA', 'lib']))

# import puppetenterprise libraries
from common_utils.password import get_password
from puppetenterprise_sdk.pe_event import puppetenterpriseEvent
from puppetenterprise_sdk.pe_client import puppetenterpriseClient

# import ITSI libraries
from ITOA.setup_logging import setup_logging
from itsi.event_management.sdk.eventing import Event
from itsi.event_management.sdk.custom_event_action_base import CustomEventActionBase
# pylint: enable = wrong-import-position
# pylint: enable = import-error

# The name of the log file to write to
PE_ITSI_LOG = 'puppetenterprise_itsi.log'

# The name of the password defining communication with puppetenterprise
puppetenterprise_PASSWORD_NAME = 'puppetenterprise_itsi_password'

# The keys of the individual Grouped Events that will be added to the pe_event payload in
#   the event map property
EVENT_KEYS = [
    'alert_level',
    'alert_severity',
    'alert_value',
    'change_type',
    'composite_kpi_name',
    'description',
    'drilldown_uri',
    'event_description',
    'event_id',
    'health_score',
    'host',
    'linecount',
    'orig_index',
    'owner',
    'scoretype',
    'search_name',
    'service_ids',
    'severity',
    'severity_label',
    'source',
    'splunk_server',
    'tag',
    'time',
    'title',
]

# The keys of the parent event/group that will be added to the pe_event properties
CORRELATION_KEYS = [
    'alert_level',
    'alert_severity',
    'alert_value',
    'change_type',
    'composite_kpi_id',
    'composite_kpi_name',
    'description',
    'drilldown_search_search',
    'drilldown_uri',
    'event_description',
    'event_id', #is_required
    'health_score',
    'host',
    'index',
    'latest_alert_level',
    'linecount',
    'orig_index',
    'owner',
    'scoretype',
    'search_name',
    'search_type',
    'service_ids',
    'severity',
    'severity_label',
    'severity_value',
    'source',
    'splunk_server',
    'splunk_server_group',
    'tag',
    'time',
    'title',
]

# A mapping of severity values to their labels
SEVERITY_TO_LABEL = {
    '1': 'info',
    '2': 'normal',
    '3': 'low',
    '4': 'medium',
    '5': 'high',
    '6': 'critical'
}

# Defines which events to update
SHOULD_UPDATE_CORRELATION = True
SHOULD_UPDATE_CHILDREN = False

def build_pe_client(username, server_uri, session_key, logger):
    """
        Builds a new puppetenterpriseClient object
        @param username: <str> an optional puppetenterprise Username
        @param server_uri: <str> the domain of the splunk server
        @param session_key: <str> a valid session key for the splunk server
        @return: <puppetenterpriseClient> an puppetenterprise Client that can be used to make requests to pe API
    """
    pe_client = puppetenterpriseClient(logger=logger)
    if username:
        password = get_password(
            server_uri,
            session_key,
            puppetenterprise_PASSWORD_NAME
        )
        if password is False:
            raise Exception('Error getting password: %s', puppetenterprise_PASSWORD_NAME)
        pe_client.add_credentials(username, password)
    return pe_client

class puppetenterpriseITSI(CustomEventActionBase):
    """
        The puppetenterpriseITSI class extends the CustomEventActionBase and is used to
        send an Event to puppetenterprise
    """

    def __init__(self, settings):
        """
        Initialize the object
        @type settings: dict/basestring
        @param settings: incoming settings for this alert action that splunkd
            passes via stdin.

        @returns Nothing
        """
        self.logger = setup_logging(pe_ITSI_LOG, 'puppetenterprise.itsi.event.action')

        super(puppetenterpriseITSI, self).__init__(settings, self.logger)

        config = self.get_config()
        username = config['username']

        self.pe_client = build_pe_client(
            username,
            self.settings.get('server_uri'),
            self.get_session_key(),
            self.logger
        )

        self.result = self.settings.get('result')
        self.endpoint_url = config['endpoint_url']
        self.recipients = config['recipients']
        self.priority = config['priority']

        self.logger.info(
            'action=%s username=%s endpoint_url=%s recipients=%s priority=%s',
            'PE_ITSI_INIT',
            username,
            self.endpoint_url,
            self.recipients,
            self.priority
        )



    def get_prop_value(self, key, value):
        """
            Safely gets the value of a property for use in an Puppet Enterprise Event.
            Currently supports list, str, unicode, None types

            @param key: <str> the name of the property
            @param value: <any> the value of the property
            @return: string
        """
        value_type = type(value)
        if value_type is list:
            return ','.join(value)
        elif value_type is str or value_type is unicode:
            return value
        elif value is None:
            return ''
        self.logger.warn('warning=INVALID_PROP_TYPE key=%s value_type=%s', key, value_type)
        return False


    def get_key_values_from_object(self, keys, source_object):
        """
            Helper method for getting a list of values from an object
            @param keys: <list>, a list of str representing the keys to extrat
            @param source_object: <dict>, a standard python map object
            @return: <dict> with only the selected keys
        """
        result = {}
        for key in keys:
            value = self.get_prop_value(key, source_object.get(key))
            if value is not False:
                result[key] = value
        return result


    def get_notable_event_pe_properties(self):
        """
            Helper method for getting the correlation event's properties
            @return: <dict> an object with only the keys we wish to send to puppetenterprise
        """
        return self.get_key_values_from_object(CORRELATION_KEYS, self.result)


    def get_event_details(self, event):
        """
            Helper method for getting an event's properties that we are interested in
            @param event: <dict>, an event's details from the Notable Event SDK
            @return: <dict> an object with only the keys we wish to send to puppetenterprise for the event
        """
        return self.get_key_values_from_object(EVENT_KEYS, event)


    def get_severity_label(self, event_details):
        """
            returns the label for the event's severity
            @param event_details: <dict>, an event's details from the Notable Event SDK
            @return: <str>, the label matching the event's severity
        """
        severity_value = event_details.get('severity')
        event_severity = SEVERITY_TO_LABEL.get(severity_value)
        if event_severity is None:
            self.logger.warning('type=BAD_SEVERITY severity=%s', severity_value)
            event_severity = 'other'
        return event_severity


    def add_success_comment_to_event(self, event_id, request_id):
        """
            Adds a success comment to an event
            @param event_id: <str> the event id
            @param request_id: <str> the request id received from puppetenterprise
            @return: None
        """
        comment = 'Successfully sent request to Puppet Enterprise: [%s]' % (request_id)
        event = Event(self.get_session_key(), self.logger)
        event.create_comment(event_id, comment)

    def send_pe_event(self, events_by_id, event_ids_by_severity):
        """
            Preps and sends an event to Puppet Enterprise
            @param events_by_id: <dict> a dict of event ids to their event
            @param event_ids_by_severity: <dit> a dict of severities to a
                list of events with that severity

            @returns: <str|bool> If the request was successful, it will return
                the requestId from Puppet Enterprise. Otherwise, False.
        """
        pe_event = puppetenterpriseEvent()
        properties = self.get_notable_event_pe_properties()
        for key in properties:
            pe_event.add_property(key, properties[key])

        pe_event.add_property('event_count', len(events_by_id))
        pe_event.add_property('events_by_id', events_by_id)
        pe_event.add_property('event_ids_by_severity', event_ids_by_severity)
        pe_event.add_property('pe_should_update_correlation', SHOULD_UPDATE_CORRELATION)
        pe_event.add_property('pe_should_update_children', SHOULD_UPDATE_CHILDREN)

        for recipient in self.recipients.split(';'):
            target_name = recipient.strip()
            pe_event.add_recipient(target_name)

        pe_event.set_priority(self.priority)

        return self.pe_client.send_event(self.endpoint_url, pe_event)

    def get_correlation_event_id(self):
        """
            Gets the Id of the Correlation Event
            @returns: <str|None> An event id if is available
        """
        return self.result.get('event_id')

    def execute(self):
        """
            The execute method that actually handles the Notable Event Alert
            @return: None
        """
        correlation_event_id = self.get_correlation_event_id()
        if correlation_event_id is None:
            raise Exception('Missing correlation event_id')

        event_count = 0
        try:
            events_by_id = {}
            event_ids_by_severity = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
                'normal': [],
                'info': [],
                'other': []
            }

            for data in self.get_event():
                if isinstance(data, Exception):
                    # Generator can yield an Exception
                    # We cannot print the call stack here reliably, because
                    # of how this code handles it, we may have generated an exception elsewhere
                    # Better to present this as an error
                    self.logger.error(data)
                    raise data

                event_id = data.get('event_id')
                if not event_id:
                    self.logger.warning('Event does not have an `event_id`. No-op.')
                    continue

                event_details = self.get_event_details(data)
                events_by_id[event_id] = event_details
                event_count += 1

                event_ids_by_severity.get(self.get_severity_label(event_details)).append(event_id)

            request_id = self.send_pe_event(events_by_id, event_ids_by_severity)
            if request_id is False:
                event = Event(self.get_session_key(), logger=self.logger)
                msg = 'An error occurred while sending request to puppetenterprise.'
                msg += ' See %s for details.' % PE_ITSI_LOG
                event.create_comment(
                    correlation_event_id,
                    msg
                )
                raise Exception('Failed to execute one or more send event actions.')

            if SHOULD_UPDATE_CORRELATION:
                self.add_success_comment_to_event(correlation_event_id, request_id)

            if SHOULD_UPDATE_CHILDREN:
                for event_data in events_by_id.values():
                    event_id = event_data.get('event_id')
                    is_correlation_event = event_id != correlation_event_id
                    if is_correlation_event or self.should_update_correlation is not True:
                        self.add_success_comment_to_event(event_id, request_id)

# pylint: disable = broad-except
        except ValueError:
            pass # best case, try every event.
        except Exception, exception:
            self.logger.error('Failed to execute PE.')
            self.logger.exception(exception)
            sys.exit(1)
        return
# pylint: enable = broad-except

if __name__ == '__main__':
    LOGGER = setup_logging(pe_ITSI_LOG, 'puppetenterprise.itsi')
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        INPUT_PARAMS = sys.stdin.read()
        try:
            pe_ITSI = puppetenterpriseITSI(INPUT_PARAMS)
            pe_ITSI.execute()
# pylint: disable = broad-except
        except Exception, exception:
            LOGGER.error('Failed to execute PE.')
            LOGGER.exception(exception)
            raise exception
# pylint: enable = broad-except
