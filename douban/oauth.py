#! /usr/bin/env python
#coding=utf-8

import cgi
import urllib
import time
import random
import urlparse
import hmac
import base64

VERSION = '1.0' # Hi Blaine!
HTTP_METHOD = 'GET'
SIGNATURE_METHOD = 'PLAINTEXT'

# Generic exception class
class OAuthError(RuntimeError):
    def __init__(self, message='OAuth error occured'):
        self.message = message

# optional WWW-Authenticate header (401 error)
def build_authenticate_header(realm=''):
    return {'WWW-Authenticate': 'OAuth realm="%s"' % realm}

# url escape
def escape(s):
    # escape '/' too
    return urllib.quote(s, safe='~')

# util function: current timestamp
# seconds since epoch (UTC)
def generate_timestamp():
    return int(time.time())

# util function: nonce
# pseudorandom number
def generate_nonce(length=8):
    return ''.join(str(random.randint(0, 9)) for i in range(length))

# OAuthConsumer is a data type that represents the identity of the Consumer
# via its shared secret with the Service Provider.
class OAuthConsumer(object):
    key = None
    secret = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

# OAuthToken is a data type that represents an End User via either an access
# or request token.     
class OAuthToken(object):
    # access tokens and request tokens
    key = None
    secret = None

    '''
    key = the token
    secret = the token secret
    '''
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def to_string(self):
        return urllib.urlencode({'oauth_token': self.key, 'oauth_token_secret': self.secret})

    # return a token from something like:
    # oauth_token_secret=digg&oauth_token=digg
    @staticmethod   
    def from_string(s):
        params = cgi.parse_qs(s, keep_blank_values=False)
        key = params['oauth_token'][0]
        secret = params['oauth_token_secret'][0]
        return OAuthToken(key, secret)

    def __str__(self):
        return self.to_string()

# OAuthRequest represents the request and can be serialized
class OAuthRequest(object):
    '''
    OAuth parameters:
        - oauth_consumer_key 
        - oauth_token
        - oauth_signature_method
        - oauth_signature 
        - oauth_timestamp 
        - oauth_nonce
        - oauth_version
        ... any additional parameters, as defined by the Service Provider.
    '''
    parameters = None # oauth parameters
    http_method = HTTP_METHOD
    http_url = None
    version = VERSION

    def __init__(self, http_method=HTTP_METHOD, http_url=None, parameters=None):
        self.http_method = http_method
        self.http_url = http_url
        self.parameters = parameters or {}

    def set_parameter(self, parameter, value):
        self.parameters[parameter] = value

    def get_parameter(self, parameter):
        try:
            return self.parameters[parameter]
        except:
            raise OAuthError('Parameter not found: %s' % parameter)

    def _get_timestamp_nonce(self):
        return self.get_parameter('oauth_timestamp'), self.get_parameter('oauth_nonce')

    # get any non-oauth parameters
    def get_nonoauth_parameters(self):
        parameters = {}
        for k, v in self.parameters.iteritems():
            # ignore oauth parameters
            if k.find('oauth_') < 0:
                parameters[k] = v
        return parameters

    # serialize as a header for an HTTPAuth request
    def to_header(self, realm=''):
        auth_header = 'OAuth realm="%s"' % realm
        # add the oauth parameters
        if self.parameters:
            for k, v in self.parameters.iteritems():
                auth_header += ', %s="%s"' % (k, v)
        return {'Authorization': auth_header}

    # serialize as post data for a POST request
    def to_postdata(self):
        return '&'.join('%s=%s' % (escape(str(k)), escape(str(v))) for k, v in self.parameters.iteritems())

    # serialize as a url for a GET request
    def to_url(self):
        return '%s?%s' % (self.get_normalized_http_url(), self.to_postdata())

    # return a string that consists of all the parameters that need to be signed
    def get_normalized_parameters(self):
        params = self.parameters
        
        param_str = urlparse.urlparse(self.http_url).query
        params.update(OAuthRequest._split_url_string(param_str))
        
        try:
            # exclude the signature if it exists
            del params['oauth_signature']
        except:
            pass
        key_values = params.items()
        # sort lexicographically, first after key, then after value
        key_values.sort()
        # combine key value pairs in string and escape
        return '&'.join('%s=%s' % (escape(str(k)), escape(str(v))) for k, v in key_values)

    # just uppercases the http method
    def get_normalized_http_method(self):
        return self.http_method.upper()

    # parses the url and rebuilds it to be scheme://host/path
    def get_normalized_http_url(self):
        parts = urlparse.urlparse(self.http_url)
        url_string = '%s://%s%s' % (parts[0], parts[1], parts[2]) # scheme, netloc, path
        return url_string
        
    # set the signature parameter to the result of build_signature
    def sign_request(self, signature_method, consumer, token):
        # set the signature method
        self.set_parameter('oauth_signature_method', signature_method.get_name())
        # set the signature
        self.set_parameter('oauth_signature', self.build_signature(signature_method, consumer, token))

    def build_signature(self, signature_method, consumer, token):
        # call the build signature method within the signature method
        return signature_method.build_signature(self, consumer, token)

    @staticmethod
    def from_request(http_method, http_url, headers=None, postdata=None, parameters=None):

        # let the library user override things however they'd like, if they know
        # which parameters to use then go for it, for example XMLRPC might want to
        # do this
        if parameters is not None:
            return OAuthRequest(http_method, http_url, parameters)

        # from the headers
        if headers is not None:
            try:
                auth_header = headers['Authorization']
                # check that the authorization header is OAuth
                auth_header.index('OAuth')
                # get the parameters from the header
                parameters = OAuthRequest._split_header(auth_header)
                return OAuthRequest(http_method, http_url, parameters)
            except:
                pass

        # from the parameter string (post body)
        if http_method == 'POST' and postdata is not None:
            parameters = OAuthRequest._split_url_string(postdata)

        # from the url string
        elif http_method == 'GET':
            param_str = urlparse.urlparse(http_url).query
            parameters = OAuthRequest._split_url_string(param_str)

        if parameters:
            return OAuthRequest(http_method, http_url, parameters)

        raise OAuthError('Missing all OAuth parameters. OAuth parameters must be in the headers, post body, or url.')

    @staticmethod
    def from_consumer_and_token(oauth_consumer, token=None, http_method=HTTP_METHOD, http_url=None, parameters=None):
        if not parameters:
            parameters = {}

        defaults = {
            'oauth_consumer_key': oauth_consumer.key,
            'oauth_timestamp': generate_timestamp(),
            'oauth_nonce': generate_nonce(),
            'oauth_version': OAuthRequest.version,
        }

        defaults.update(parameters)
        parameters = defaults

        if token:
            parameters['oauth_token'] = token.key

        return OAuthRequest(http_method, http_url, parameters)

    @staticmethod
    def from_token_and_callback(token, callback=None, http_method=HTTP_METHOD, http_url=None, parameters=None):
        if not parameters:
            parameters = {}

        parameters['oauth_token'] = token.key

        if callback:
            parameters['oauth_callback'] = escape(callback)

        return OAuthRequest(http_method, http_url, parameters)

    # util function: turn Authorization: header into parameters, has to do some unescaping
    @staticmethod
    def _split_header(header):
        params = {}
        parts = header.split(',')
        for param in parts:
            # ignore realm parameter
            if param.find('OAuth realm') > -1:
                continue
            # remove whitespace
            param = param.strip()
            # split key-value
            param_parts = param.split('=', 1)
            # remove quotes and unescape the value
            params[param_parts[0]] = urllib.unquote(param_parts[1].strip('\"'))
        return params
    
    # util function: turn url string into parameters, has to do some unescaping
    @staticmethod
    def _split_url_string(param_str):
        parameters = cgi.parse_qs(param_str, keep_blank_values=False)
        for k, v in parameters.iteritems():
            parameters[k] = urllib.unquote(v[0])
        return parameters

# OAuthServer is a worker to check a requests validity against a data store
class OAuthServer(object):
    timestamp_threshold = 300 # in seconds, five minutes
    version = VERSION
    signature_methods = None
    data_store = None

    def __init__(self, data_store=None, signature_methods=None):
        self.data_store = data_store
        self.signature_methods = signature_methods or {}

    def set_data_store(self, oauth_data_store):
        self.data_store = data_store

    def get_data_store(self):
        return self.data_store

    def add_signature_method(self, signature_method):
        self.signature_methods[signature_method.get_name()] = signature_method
        return self.signature_methods

    # process a request_token request
    # returns the request token on success
    def fetch_request_token(self, oauth_request):
        try:
            # get the request token for authorization
            token = self._get_token(oauth_request, 'request')
        except:
            # no token required for the initial token request
            version = self._get_version(oauth_request)
            consumer = self._get_consumer(oauth_request)
            self._check_signature(oauth_request, consumer, None)
            # fetch a new token
            token = self.data_store.fetch_request_token(consumer)
        return token

    # process an access_token request
    # returns the access token on success
    def fetch_access_token(self, oauth_request):
        version = self._get_version(oauth_request)
        consumer = self._get_consumer(oauth_request)
        # get the request token
        token = self._get_token(oauth_request, 'request')
        self._check_signature(oauth_request, consumer, token)
        new_token = self.data_store.fetch_access_token(consumer, token)
        return new_token

    # verify an api call, checks all the parameters
    def verify_request(self, oauth_request):
        # -> consumer and token
        version = self._get_version(oauth_request)
        consumer = self._get_consumer(oauth_request)
        # get the access token
        token = self._get_token(oauth_request, 'access')
        self._check_signature(oauth_request, consumer, token)
        parameters = oauth_request.get_nonoauth_parameters()
        return consumer, token, parameters

    # authorize a request token
    def authorize_token(self, token, user):
        return self.data_store.authorize_request_token(token, user)
    
    # get the callback url
    def get_callback(self, oauth_request):
        return oauth_request.get_parameter('oauth_callback')

    # optional support for the authenticate header   
    def build_authenticate_header(self, realm=''):
        return {'WWW-Authenticate': 'OAuth realm="%s"' % realm}

    # verify the correct version request for this server
    def _get_version(self, oauth_request):
        try:
            version = oauth_request.get_parameter('oauth_version')
        except:
            version = VERSION
        if version and version != self.version:
            raise OAuthError('OAuth version %s not supported' % str(version))
        return version

    # figure out the signature with some defaults
    def _get_signature_method(self, oauth_request):
        try:
            signature_method = oauth_request.get_parameter('oauth_signature_method')
        except:
            signature_method = SIGNATURE_METHOD
        try:
            # get the signature method object
            signature_method = self.signature_methods[signature_method]
        except:
            signature_method_names = ', '.join(self.signature_methods.keys())
            raise OAuthError('Signature method %s not supported try one of the following: %s' % (signature_method, signature_method_names))

        return signature_method

    def _get_consumer(self, oauth_request):
        consumer_key = oauth_request.get_parameter('oauth_consumer_key')
        if not consumer_key:
            raise OAuthError('Invalid consumer key')
        consumer = self.data_store.lookup_consumer(consumer_key)
        if not consumer:
            raise OAuthError('Invalid consumer')
        return consumer

    # try to find the token for the provided request token key
    def _get_token(self, oauth_request, token_type='access'):
        token_field = oauth_request.get_parameter('oauth_token')
        token = self.data_store.lookup_token(token_type, token_field)
        if not token:
            raise OAuthError('Invalid %s token: %s' % (token_type, token_field))
        return token

    def _check_signature(self, oauth_request, consumer, token):
        timestamp, nonce = oauth_request._get_timestamp_nonce()
        self._check_timestamp(timestamp)
        self._check_nonce(consumer, token, nonce)
        signature_method = self._get_signature_method(oauth_request)
        try:
            signature = oauth_request.get_parameter('oauth_signature')
        except:
            raise OAuthError('Missing signature')
        # attempt to construct the same signature
        built = signature_method.build_signature(oauth_request, consumer, token)
        if signature != built:
            raise OAuthError('Signature does not match. Expected: %s Got: %s' % (built, signature))

    def _check_timestamp(self, timestamp):
        # verify that timestamp is recentish
        timestamp = int(timestamp)
        now = int(time.time())
        lapsed = now - timestamp
        if lapsed > self.timestamp_threshold:
            raise OAuthError('Expired timestamp: given %d and now %s has a greater difference than threshold %d' % (timestamp, now, self.timestamp_threshold))

    def _check_nonce(self, consumer, token, nonce):
        # verify that the nonce is uniqueish
        try:
            self.data_store.lookup_nonce(consumer, token, nonce)
            raise OAuthError('Nonce already used: %s' % str(nonce))
        except:
            pass

# OAuthClient is a worker to attempt to execute a request
class OAuthClient(object):
    consumer = None
    token = None

    def __init__(self, oauth_consumer, oauth_token):
        self.consumer = oauth_consumer
        self.token = oauth_token

    def get_consumer(self):
        return self.consumer

    def get_token(self):
        return self.token

    def fetch_request_token(self, oauth_request):
        # -> OAuthToken
        raise NotImplementedError

    def fetch_access_token(self, oauth_request):
        # -> OAuthToken
        raise NotImplementedError

    def access_resource(self, oauth_request):
        # -> some protected resource
        raise NotImplementedError

# OAuthDataStore is a database abstraction used to lookup consumers and tokens
class OAuthDataStore(object):

    def lookup_consumer(self, key):
        # -> OAuthConsumer
        raise NotImplementedError

    def lookup_token(self, oauth_consumer, token_type, token_token):
        # -> OAuthToken
        raise NotImplementedError

    def lookup_nonce(self, oauth_consumer, oauth_token, nonce, timestamp):
        # -> OAuthToken
        raise NotImplementedError

    def fetch_request_token(self, oauth_consumer):
        # -> OAuthToken
        raise NotImplementedError

    def fetch_access_token(self, oauth_consumer, oauth_token):
        # -> OAuthToken
        raise NotImplementedError

    def authorize_request_token(self, oauth_token, user):
        # -> OAuthToken
        raise NotImplementedError

# OAuthSignatureMethod is a strategy class that implements a signature method
class OAuthSignatureMethod(object):
    def get_name():
        # -> str
        raise NotImplementedError

    def build_signature(oauth_request, oauth_consumer, oauth_token):
        # -> str
        raise NotImplementedError

class OAuthSignatureMethod_HMAC_SHA1(OAuthSignatureMethod):

    def get_name(self):
        return 'HMAC-SHA1'

    def build_signature(self, oauth_request, consumer, token):
        sig = (
            escape(oauth_request.get_normalized_http_method()),
            escape(oauth_request.get_normalized_http_url()),
            escape(oauth_request.get_normalized_parameters()),
        )

        key = '%s&' % escape(consumer.secret)
        if token:
            key += escape(token.secret)
        raw = '&'.join(sig)

        # hmac object
        try:
            import hashlib # 2.5
            hashed = hmac.new(key, raw, hashlib.sha1)
        except:
            import sha # deprecated
            hashed = hmac.new(key, raw, sha)

        # calculate the digest base 64
        return base64.b64encode(hashed.digest())

class OAuthSignatureMethod_PLAINTEXT(OAuthSignatureMethod):

    def get_name(self):
        return 'PLAINTEXT'

    def build_signature(self, oauth_request, consumer, token):
        # concatenate the consumer key and secret
        sig = escape(consumer.secret)
        if token:
            sig = '&'.join((sig, escape(token.secret)))
        return sig
