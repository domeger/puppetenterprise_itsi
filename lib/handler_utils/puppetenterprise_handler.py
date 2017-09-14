"""
    This file is used as a template for creating Persistent
    Connection REST Handlers
"""
import os
import sys
import json

# pylint: disable = import-error
from ITOA.setup_logging import setup_logging

if sys.platform == "win32":
    import msvcrt
    # Binary mode is required for persistent mode on Windows.
# pylint: disable = no-member
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)
# pylint: enable = no-member
# pylint: enable = import-error


DEFAULT_LOGGER = setup_logging('puppetenterprise.log', 'puppetenterprise.handler')

class puppetenterpriseHandler(object):
    """
        This class is the template for Persistent Connection
        Handlers. For examples of use see /bin/puppetenterprise_comment_handler.py
        and /bin/puppetenterprise_response_handler.py.

        The main concept is that there are:
         * 1 Mandatory method to override (process_request)
         * 1 Optional method to override (validate_request)
         * 2 member variables you can optionally set (valid_methods, required_fields)
             > they are used to validate the input before calling validate_request

        In addition, there are some helpful utilities you can call (see their docs below):
         * handle_puppetenterprise_error
         * build_response
    """
    def __init__(self, command_line, command_arg, **kwargs):
        """
            initialize the object. parameters are unused
        """
        self.logger = kwargs.get('logger', DEFAULT_LOGGER)
        self.command_line = command_line
        self.command_arg = command_arg
        self.valid_methods = ['POST']
        self.required_fields = []

    def handle_puppetenterprise_error(self, message, exception, **kwargs):
        """
            Logs an error and creates a response body
            @param message: <str> An error message
            @param exception: <exception> The exception
            @param status_code: <number>, An optional status code to
                associate with the error. defaults to 400

            @returns: <object> A response body with status and payload
        """
        status_code = kwargs.get('status_code', 400)
        if not message:
            message = 'An unknown error occurred.'
        self.logger.error(message)
        self.logger.exception(exception)
        return self.build_response(
            status_code,
            {'message': message}
        )

    def build_response(self, status_code, payload):
        """
            Logs to info and creates a response body
            @param status_code: <number> The status code to return
            @param payload: <object> The payload to return

            @returns: <object> A response body with status and payload
        """
        self.logger.info('status=%s payload=%s', status_code, payload)
        return {
            'status': status_code,
            'payload': payload
        }

    def check_required_fields(self, input_payload, **kwargs):
        """
            Checks to see if any required fields are missing
            @param input_payload: <object> The request payload in object form
            @param required_fields: <list>, An optional list of field names to
                check for, defaults to self.required_fields

            @returns: <list> The list of required field names that are missing
        """
        required_fields = kwargs.get('required_fields', self.required_fields)
        missing_required_fields = []
        for key in required_fields:
            if input_payload.get(key) is None:
                missing_required_fields.append(key)
        return missing_required_fields

    def validate_method(self, method, **kwargs):
        """
            Checks to see if any required fields are missing
            @param method: <str> An HTTP Method (should be all caps)
            @param valid_methods: <list>, An optional list of methods to check
                for, defaults to self.valid_methods

            @returns: <list> The list of required field names that are missing
        """
        valid_methods = kwargs.get('valid_methods', self.valid_methods)
        return method in valid_methods

    def validate_request(self, input_payload, **kwargs):
        """
            A method to override to provide any additional validation beyond
            valid methods and required field checking
            @param input_payload: <object> The request payload in object form
            @param method: <str> The HTTP Method (should be all caps) <kwargs>
            @param session_key: <str> The Splunk session key <kwargs>
            @param server_rest_uri: <str> The Splunk Server base url <kwargs>

            @returns: <object|None> If a validation error exists, return an
                error object, otherwise return a Falsey value
        """
        pass

# pylint: disable = unused-argument
# pylint: disable = no-self-use
    def process_request(self, input_payload, **kwargs):
        """
            A method to override to provide any additional validation beyond
            valid methods and required field checking
            @param input_payload: <object> The request payload in object form
            @param method: <str> The HTTP Method (should be all caps) <kwargs>
            @param session_key: <str> The Splunk session key <kwargs>
            @param server_rest_uri: <str> The Splunk Server base url <kwargs>

            @returns: <object> A response object, likely made by self.build_response
        """
        raise ValueError('This handler did not implement process_request')
# pylint: enable = no-self-use
# pylint: enable = unused-argument

    def handle(self, in_string):
        """
            the handler method for incoming http requests
            @param in_string: <str> the http request input string

            @returns: <object> A response object, likely made by self.build_response
        """
        try:
            self.logger.debug('INPUT: %s', json.dumps(in_string))
            input_request = json.loads(in_string)

            method = input_request.get('method')

            if not self.validate_method(method):
                error_template = 'METHOD= %s SUPPORTED_METHODS= %s'
                return self.build_response(
                    405,
                    error_template % (method, ",".join(self.valid_methods))
                )

            input_payload = json.loads(input_request.get('payload'))

            missing_fields = self.check_required_fields(input_payload)
            if missing_fields:
                return self.build_response(
                    400,
                    {
                        'error_code': 'INVALID_REQUEST',
                        'error_message': 'Missing Required Fields',
                        'missing_fields': missing_fields
                    }
                )
            # else:
            session_key = input_request.get('session').get('authtoken')
            server_rest_uri = input_request.get('server').get('rest_uri')

            validation_error = self.validate_request(
                input_payload,
                method=method,
                session_key=session_key,
                server_rest_uri=server_rest_uri
            )
            if validation_error:
                return self.build_response(400, validation_error)

            return self.process_request(
                input_payload,
                method=method,
                session_key=session_key,
                server_rest_uri=server_rest_uri
            )
# pylint: disable = broad-except
        except Exception, exception:
            message = 'An unknown error occurred.'
            self.logger.error(message)
            self.logger.exception(exception)
            return self.build_response(400, {'message': message})
# pylint: enable = broad-except
