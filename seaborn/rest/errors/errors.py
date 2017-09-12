""" This module contains the error message exception classes

    The HTTP status codes and descriptions are stored in status_names and status_descriptions

"""
__author__ = 'Ben Christenson'
__date__ = "6/4/16"

import traceback
from seaborn.repr_wrapper import str_name_value

GOOD_REQUEST = 200
class RestException(Exception):
    status_code = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @property
    def name(self):
        return str(self.__class__).split('.')[-1].split("'")[0]

    def __repr__(self):
        return '%s(%s)' % (self.name, self.message)

    def __str__(self):
        return self.message

    @property
    def message(self):
        return ','.join([repr(a) for a in self.args] +
                        ['%s=%s' % (k, repr(v)) for k, v in self.kwargs.items()])

    @classmethod
    def str_to_obj(cls, string):
        try:
            # todo add args to this
            kwargs = eval('dict(%s)' % string)
            return cls(**kwargs)
        except:
            return cls(string)


class ContinueException(RestException):
    """
        This means that the server has received the request headers, and that the client should proceed
        to send the request body (in the case of a request for which a body needs to be sent; for example,
        a POST request). If the request body is large, sending it to a server when a request has already
        been rejected based upon inappropriate headers is inefficient. To have a server check if the
        request could be accepted based on the request's headers alone, a client must send Expect:
        100-continue as a header in its initial request and check if a 100 Continue status code is
        received in response before continuing (or receive 417 Expectation Failed and not continue).
    """
    status_code = 100


class SwitchingProtocolsException(RestException):
    """
        This means the requester has asked the server to switch protocols and the server is
        acknowledging that it will do so.
    """
    status_code = 101


class ProcessingException(RestException):
    """
        As a WebDAV request may contain many sub-requests involving file operations, it may take a long
        time to complete the request. This code indicates that the server has received and is processing
        the request, but no response is available yet.[3] This prevents the client from timing out and
        assuming the request was lost.
    """
    status_code = 102


class OKException(RestException):
    """
        Standard response for successful HTTP requests. The actual response will depend on the request
        method used. In a GET request, the response will contain an entity corresponding to the requested
        resource. In a POST request the response will contain an entity describing or containing the
        result of the action.
    """
    status_code = 200


class CreatedException(RestException):
    """
        The request has been fulfilled and resulted in a new resource being created.
    """
    status_code = 201


class AcceptedException(RestException):
    """
        The request has been accepted for processing, but the processing has not been completed. The
        request might or might not eventually be acted upon, as it might be disallowed when processing
        actually takes place.
    """
    status_code = 202


class NonAuthoritativeInformationException(RestException):
    """
        The server successfully processed the request, but is returning information that may be from
        another source.
    """
    status_code = 203


class NoContentException(RestException):
    """
        The server successfully processed the request, but is not returning any content. Usually used
        as a response to a successful delete request.
    """
    status_code = 204


class ResetContentException(RestException):
    """
        The server successfully processed the request, but is not returning any content.
        Unlike a 204 response, this response requires that the requester reset the document view.
    """
    status_code = 205


class PartialContentException(RestException):
    """
        The server is delivering only part of the resource (byte serving) due to a range header sent
        by the client. The range header is used by tools like wget to enable resuming of interrupted
        downloads, or split a download into multiple simultaneous streams.
    """
    status_code = 206


class MultiStatusException(RestException):
    """
        The message body that follows is an XML message and can contain a number of separate response
        codes, depending on how many sub-requests were made.
    """
    status_code = 207


class AlreadyReportedException(RestException):
    """
        The members of a DAV binding have already been enumerated in a previous reply to this request,
        and are not being included again.
    """
    status_code = 208


class IMUsedException(RestException):
    """
        The server has fulfilled a request for the resource, and the response is a representation of
        the result of one or more instance-manipulations applied to the current instance.
    """
    status_code = 226


class MultipleChoicesException(RestException):
    """
        Indicates multiple options for the resource that the client may follow. It, for instance,
        could be used to present different format options for video, list files with different
        extensions, or word sense disambiguation.
    """
    status_code = 300


class MovedPermanentlyException(RestException):
    """
        This and all future requests should be directed to the given URI.
    """
    status_code = 301


class FoundException(RestException):
    """
        This is an example of industry practice contradicting the standard.
        The HTTP/1.0 specification (RFC 1945) required the client to perform a temporary redirect
        (the original describing phrase was "Moved Temporarily"), but popular browsers implemented
        302 with the functionality of a 303 See Other. Therefore, HTTP/1.1 added status codes 303 and
        307 to distinguish between the two behaviours. However, some Web applications and frameworks
        use the 302 status code as if it were the 303.
    """
    status_code = 302


class SeeOtherException(RestException):
    """
        The response to the request can be found under another URI using a GET method. When received
        in response to a POST (or PUT/DELETE), it should be assumed that the server has received the
        data and the redirect should be issued with a separate GET message.
    """
    status_code = 303


class NotModifiedException(RestException):
    """
        Indicates that the resource has not been modified since the version specified by the request
        headers If-Modified-Since or If-None-Match. This means that there is no need to retransmit
        the resource, since the client still has a previously-downloaded copy.
    """
    status_code = 304


class UseProxyException(RestException):
    """
        The requested resource is only available through a proxy, whose address is provided in the
        response. Many HTTP clients (such as Mozilla[9] and Internet Explorer) do not correctly handle
        responses with this status code, primarily for security reasons.
    """
    status_code = 305


class SwitchProxyException(RestException):
    """
        No longer used. Originally meant "Subsequent requests should use the specified proxy."
    """
    status_code = 306


class TemporaryRedirectException(RestException):
    """
        In this case, the request should be repeated with another URI; however, future requests should
        still use the original URI. In contrast to how 302 was historically implemented, the request
        method is not allowed to be changed when reissuing the original request. For instance, a POST
        request should be repeated using another POST request.
    """
    status_code = 307


class PermanentRedirectException(RestException):
    """
        The request, and all future requests should be repeated using another URI. 307 and 308 (as
        proposed) parallel the behaviours of 302 and 301, but do not allow the HTTP method to change.
    """
    status_code = 308


class BadRequestException(RestException):
    """
        The server cannot or will not process the request due to something that is perceived to be a
        client error.
    """
    status_code = 400


class UnauthorizedException(RestException):
    """
        Similar to 403 Forbidden, but specifically for use when authentication is required and has
        failed or has not yet been provided. The response must include a WWW-Authenticate header field
        containing a challenge applicable to the requested resource. See Basic access authentication
        and Digest access authentication.
    """
    status_code = 401


class PaymentRequiredException(RestException):
    """
        Reserved for future use. The original intention was that this code might be used as part of
        some form of digital cash or micropayment scheme, but that has not happened, and this code
        is not usually used. YouTube uses this status if a particular IP address has made excessive
        requests, and requires the person to enter a CAPTCHA.
    """
    status_code = 402


class ForbiddenException(RestException):
    """
        The request was a valid request, but the server is refusing to respond to it. Unlike a 401
        Unauthorized response, authenticating will make no difference.
    """
    status_code = 403


class NotFoundException(RestException):
    """
        The requested resource could not be found but may be available again in the future.
        Subsequent requests by the client are permissible.
    """
    status_code = 404


class MethodNotAllowedException(RestException):
    """
        A request was made of a resource using a request method not supported by that resource; for
        example, using GET on a form which requires data to be presented via POST, or using PUT on
        a read-only resource.
    """
    status_code = 405


class NotAcceptableException(RestException):
    """
        The requested resource is only capable of generating content not acceptable according to the
        Accept headers sent in the request.
    """
    status_code = 406


class ProxyAuthenticationRequiredException(RestException):
    """
        The client must first authenticate itself with the proxy.
    """
    status_code = 407


class RequestTimeoutException(RestException):
    """
        The server timed out waiting for the request. According to HTTP specifications:
        "The client did not produce a request within the time that the server was prepared to wait.
        The client MAY repeat the request without modifications at any later time."
    """
    status_code = 408


class ConflictException(RestException):
    """
        Indicates that the request could not be processed because of conflict in the request,
        such as an edit conflict in the case of multiple updates.
    """
    status_code = 409


class GoneException(RestException):
    """
        Indicates that the resource requested is no longer available and will not be available again.
        This should be used when a resource has been intentionally removed and the resource should be
        purged. Upon receiving a 410 status code, the client should not request the resource again in
        the future. Clients such as search engines should remove the resource from their indices.
        Most use cases do not require clients and search engines to purge the resource, and a
        "404 Not Found" may be used instead.
    """
    status_code = 410


class LengthRequiredException(RestException):
    """
        The request did not specify the length of its content, which is required by the requested resource.
    """
    status_code = 411


class PreconditionFailedException(RestException):
    """
        The server does not meet one of the preconditions that the requester put on the request.
    """
    status_code = 412


class RequestEntityTooLargeException(RestException):
    """
        The request is larger than the server is willing or able to process.
    """
    status_code = 413


class RequestURITooLongException(RestException):
    """
        The URI provided was too long for the server to process. Often the result of too much data being
        encoded as a query-string of a GET request, in which case it should be converted to a POST request.
    """
    status_code = 414


class UnsupportedMediaTypeException(RestException):
    """
        The request entity has a media type which the server or resource does not support. For example, the
        client uploads an image as image/svg+xml, but the server requires that images use a different format.
    """
    status_code = 415


class RequestedRangeNotSatisfiableException(RestException):
    """
        The client has asked for a portion of the file (byte serving), but the server cannot supply that
        portion. For example, if the client asked for a part of the file that lies beyond the end of the
        file.
    """
    status_code = 416


class ExpectationFailedException(RestException):
    """
        The server cannot meet the requirements of the Expect request-header field.
    """
    status_code = 417


class AprilFoolsException(RestException):
    """
        This code was defined in 1998 as one of the traditional IETF April Fools' jokes, in RFC 2324, Hyper
        Text Coffee Pot Control Protocol, and is not expected to be implemented by actual HTTP servers.
    """
    status_code = 418


class AuthenticationTimeoutException(RestException):
    """
        Not a part of the HTTP standard, 419 Authentication Timeout denotes that previously valid
        authentication has expired. It is used as an alternative to 401 Unauthorized in order to
        differentiate from otherwise authenticated clients being denied access to specific server resources.
    """
    status_code = 419


class EnhanceYourCalmException(RestException):
    """
        Not part of the HTTP standard, but returned by version 1 of the Twitter Search and Trends API
        when the client is being rate limited.[16] Other services may wish to implement the 429
        Too Many Requests response code instead.
    """
    status_code = 420


class UnprocessableEntityException(RestException):
    """
        The request was well-formed but was unable to be followed due to semantic errors.
    """
    status_code = 422


class LockedException(RestException):
    """
        The resource that is being accessed is locked.
    """
    status_code = 423


class FailedDependencyException(RestException):
    """
        The request failed due to failure of a previous request
    """
    status_code = 424


class UpgradeRequiredException(RestException):
    """
        The client should switch to a different protocol such as TLS/1.0.
    """
    status_code = 426


class PreconditionRequiredException(RestException):
    """
        The origin server requires the request to be conditional. Intended to prevent "the
        'lost update' problem, where a client GETs a resource's state, modifies it, and PUTs it back
        to the server, when meanwhile a third party has modified the state on the server,
        leading to a conflict."
    """
    status_code = 428


class TooManyRequestsException(RestException):
    """
        The user has sent too many requests in a given amount of time. Intended for use with rate
        limiting schemes.
    """
    status_code = 429


class RequestHeaderFieldsTooLargeException(RestException):
    """
        The server is unwilling to process the request because either an individual header field,
        or all the header fields collectively, are too large.
    """
    status_code = 431


class LoginTimeoutException(RestException):
    """
        A Microsoft extension. Indicates that your session has expired.
    """
    status_code = 440


class NoResponseException(RestException):
    """
        Used in Nginx logs to indicate that the server has returned no information to the client and
        closed the connection (useful as a deterrent for malware).
    """
    status_code = 444


class RetryWithMicrosoftException(RestException):
    """
        A Microsoft extension. The request should be retried after performing the appropriate action.
    """
    status_code = 449


class BlockedbyWindowsParentalControlsException(RestException):
    """
        A Microsoft extension. This error is given when Windows Parental Controls are turned on and
        are blocking access to the given webpage.
    """
    status_code = 450


class RedirectException(RestException):
    """
        Used in Exchange ActiveSync if there either is a more efficient server to use or the server
        cannot access the users' mailbox.
    """
    status_code = 451


class ConferenceNotFoundException(RestException):
    """
        Missing Description
    """
    status_code = 452


class NotEnoughBandwidthException(RestException):
    """
        Missing Description
    """
    status_code = 453


class SessionNotFoundException(RestException):
    """
        Missing Description
    """
    status_code = 454


class MethodNotValidInThisStateException(RestException):
    """
        Missing Description
    """
    status_code = 455


class HeaderFieldNotValidException(RestException):
    """
        Missing Description
    """
    status_code = 456


class InvalidRangeException(RestException):
    """
        Missing Description
    """
    status_code = 457


class ParameterIsReadOnlyException(RestException):
    """
        Missing Description
    """
    status_code = 458


class AggregateOperationNotAllowedException(RestException):
    """
        Missing Description
    """
    status_code = 459


class OnlyAggregateOperationAllowedException(RestException):
    """
        Missing Description
    """
    status_code = 460


class UnsupportedTransportException(RestException):
    """
        Missing Description
    """
    status_code = 461


class DestinationunreachableException(RestException):
    """
        On a login this may be caused by pending verification
    """
    status_code = 462


class KeymanagementFailureException(RestException):
    """
        Missing Description
    """
    status_code = 463


class RequestHeaderTooLargeException(RestException):
    """
        Nginx internal code similar to 431 but it was introduced earlier in version 0.9.4
    """
    status_code = 494


class CertErrorException(RestException):
    """
        Nginx internal code used when SSL client certificate error occurred to distinguish it from
        4XX in a log and an error page redirection.
    """
    status_code = 495


class NoCertException(RestException):
    """
        Nginx internal code used when client didn't provide certificate to distinguish it from 4XX
        in a log and an error page redirection.
    """
    status_code = 496


class HTTPtoHTTPSException(RestException):
    """
        Nginx internal code used for the plain HTTP requests that are sent to HTTPS port to distinguish
        it from 4XX in a log and an error page redirection.
    """
    status_code = 497


class TokenExpiredException(RestException):
    """
        Returned by ArcGIS for Server. A code of 498 indicates an expired or otherwise invalid token.
    """
    status_code = 498


class TokenrequiredException(RestException):
    """
        Returned by ArcGIS for Server. A code of 499 indicates that a token is required
        (if no token was submitted).
    """
    status_code = 499


class InternalServerErrorException(RestException):
    """
        A generic error message, given when an unexpected condition was encountered and no more
        specific message is suitable.
    """
    status_code = 500

    @property
    def message(self):
        return '...'


class NotImplementedException(RestException):
    """
        The server either does not recognize the request method, or it lacks the ability to fulfil the
        request. Usually this implies future availability
    """
    status_code = 501


class BadGatewayException(RestException):
    """
        The server was acting as a gateway or proxy and received an invalid response from the
        upstream server.
    """
    status_code = 502


class ServiceUnavailableException(RestException):
    """
        The server is currently unavailable (because it is overloaded or down for maintenance).
        Generally, this is a temporary state.
    """
    status_code = 503


class GatewayTimeoutException(RestException):
    """
        The server was acting as a gateway or proxy and did not receive a timely response from
        the upstream server.
    """
    status_code = 504


class HTTPVersionNotSupportedException(RestException):
    """
        The server does not support the HTTP protocol version used in the request.
    """
    status_code = 505


class VariantAlsoNegotiatesException(RestException):
    """
        Transparent content negotiation for the request results in a circular reference.
    """
    status_code = 506


class InsufficientStorageException(RestException):
    """
        The server is unable to store the representation needed to complete the request.
    """
    status_code = 507


class LoopDetectedException(RestException):
    """
        The server detected an infinite loop while processing the request
        (sent in lieu of 208 Already Reported).
    """
    status_code = 508


class BandwidthLimitExceededException(RestException):
    """
        This status code is not specified in any RFCs. Its use is unknown.
    """
    status_code = 509


class NotExtendedException(RestException):
    """
        Further extensions to the request are required for the server to fulfil it.
    """
    status_code = 510


class NetworkAuthenticationRequiredException(RestException):
    """
        The client needs to authenticate to gain network access. Intended for use by intercepting
        proxies used to control access to the network (e.g., "captive portals" used to require
        agreement to Terms of Service before granting full Internet access via a Wi-Fi hotspot).
    """
    status_code = 511


class NetworkReadTimeOutException(RestException):
    """
        This status code is not specified in any RFCs, but is used by Microsoft HTTP proxies to
        signal a network read timeout behind the proxy to a client in front of the proxy.
    """
    status_code = 598


class NetworkConnectTimeOutException(RestException):
    """
        This status code is not specified in any RFCs, but is used by Microsoft HTTP proxies to
        signal a network connect timeout behind the proxy to a client in front of the proxy.
    """
    status_code = 599


# not used any more
class ApiError(Exception):
    """ This exception is thrown during an API call and therefore has the added attributes:
        :param message:             str message of addition information from endpoint binding
        :param original_error:      Exception this is the original exception message
        :param http_body:           str of the body of the response message
        :param url:                 str of the url from the request
        :param status_code:         int of the http status code
        :param status_name:         str of the name for the http status code
        :param status_description:  str description of the http status or description from eagle eye bindings
    """

    def __init__(self, message=None, original_error=None, http_body=None, url=None,
                 status_code=None, status_name=None, status_description=None, server_details=''):
        self.message = message
        self.original_error = original_error
        self.stack = traceback.format_stack(limit=5)

        self.description = status_description is None and '' or str(status_description)
        self.status_code = status_code

        self.server_details = server_details

        if status_code and getattr(self,'type','NoneType') == 'NoneType':
            self.type = 'AssertionError'

        self.status_name = status_name or self.type

        self.url = url
        if http_body and hasattr(http_body, 'decode'):
            try:
                http_body = http_body.decode('utf-8')
            except:
                http_body = ('<Could not decode body as utf-8. '
                             'Please report to support@eagleeyenetworks.com>')
        self.http_body = http_body

    def __repr__(self):
        return 'API Exception ( %s )' % self.status_name + (self.server_details and (' - ' + self.server_details) or '')

    def __str__(self):
        values = [str_name_value(k, getattr(self, k, '')) for k in
                  ['type', 'message', 'status_name', 'status_code', 'url', 'server_detail']  # , 'description', 'stack'
                  if getattr(self, k, None)]
        return '\n' + '\n'.join(values)


HTTP_STATUS_CODES = {exception.status_code: exception for exception in globals().values()
                     if getattr(exception, 'status_code', None) and issubclass(exception, RestException)}
