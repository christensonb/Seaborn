""" This is a simple wrapper around request to make a REST http api call
    This will throw exception if the response code is not within 200-399

    This is primarily used to debug or test api calls so it contains a lot of helper
    functions for displaying or tracking the api call

    Also this will return a Repr wrapper version of the json data
"""
__author__ = 'Ben Christenson'
__date__ = "10/7/15"

import datetime
import json
import os
import time
from copy import deepcopy
import requests
import logging as log
from requests.models import PreparedRequest as PreparedRequest_
from requests.sessions import Session

from seaborn.file import get_filename
from seaborn.repr_wrapper import *
from seaborn.rest.errors import *
from seaborn.timestamp import reformat_date
from seaborn.repr_wrapper import str_name_value
from seaborn.calling_function import function_kwargs

try:
    from OpenSSL.SSL import ZeroReturnError
except Exception as e_:
    ZeroReturnError = None

import gevent

TIMESTAMPS_ORDER = ['create', 'setup', 'repeat', 'send', 'receive', 'stream', 'last_stream', 'process', 'exception',
                    'report']

VERIFY = False # set this to false if your ssl certificate is self signed (i.e. not paid for and hosted on a 3rd party)


class ApiCall(object):
    PreparedRequest = PreparedRequest_
    session = Session()

    def __init__(self, name=None, label=None, base_uri=None, endpoint_params=None, headers=None, cookies=None,
                 accepted_return=None, timeout=None, max_duration=None, max_size=None, proxies=None,
                 method=None, data=None, hooks=None, params=None):
        # This will initialize a lot of place holders for the api call
        self._timestamps = {'create': time.time()}  # dictionary of timestamps
        self.error = None  # stores the ExceptionError if there is one
        self.status_code = None  # http request response code
        self.raw_data = None  # data as it was parsed out of response content
        self.sub_url = None  # the request url path
        self.url = None  # complete url
        self.request_data = None  # data in the api request call
        self.json = None  # json in the api request call
        self.files = None  # files saved to (for save method)
        self.filename = None  # filename to save the video or image to
        self.response = None  # response returned
        self.start = None  # time the request started
        self._stage = STAGE_INIT  # stage of the api call
        self._server_timing = None  # timing for the server
        self.repeat_needed = 0  # m3u8 needs to repeat calls if the list isn't done
        self.content_length = None  # length of the content in bytes
        self.method = method  # method of the call ['GET','POST','PUT','DELETE']
        self.data = None  # data as it is returned from the endpoint code with Repr wrapper
        self.hooks = {}  # hooks, pass through to request
        self.params = {}  # parameters sent in api request call
        self.prepared_request = self.PreparedRequest()  # internal prepared request

        # these are the parameters passed in
        self.name = name or ""  # name of the api call which will be the endpoint name
        self.label = label or ""  # label (key) to reference this api call in the connection
        self.base_uri = base_uri  # full base_uri, e.g. www.google.com
        self.endpoint_params = endpoint_params or {}  # parameters sent to the endpoint class method
        self.headers = headers or {}  # headers in the api request call
        self.cookies = cookies or {}  # cookies in the api request call
        self.accepted_return = accepted_return  # accepted return type ['json','html']
        self.timeout = timeout  # timeout
        self.max_duration = max_duration  # max duration for testing, but it cuts the call short
        self.max_size = max_size  # max size for testing, but it cuts the call short
        self.proxies = proxies  # proxies, pass through to request
        self.method = method
        if method:
            self.set_request(data=data, hooks=hooks, params=params)

    def set_request(self, method=None, sub_url="", data=None, params=None, proxies=None):
        """
        :param method: str of the method of the api_call
        :param sub_url: str of the url after the uri
        :param data: dict of form data to be sent with the request
        :param params: dict of additional data to be sent as teh request parameters
        :param proxies: str of the proxie to use
        :return: None
        """
        self.method = method or self.method
        self.url = self.base_uri and (self.base_uri + sub_url) or sub_url
        self.params.update(params or {})
        self.proxies = proxies or self.proxies
        if self.params:
            self.url += '?' + '&'.join(['%s=%s' % (k, v) for k, v in self.params.items()])
        self.request_data = deepcopy(data)
        self._timestamps['setup'] = time.time()
        if isinstance(data, dict) and 'content-type' not in self.headers:
            self.headers['content-type'] = 'application/json'
            self.json = data  # don't change this user.post
        else:
            self.data = data

        if self.accepted_return is not None:
            self.headers['Accept'] = {'json': 'application/json', 'html': 'text/html'}[self.accepted_return]

        self._stage = STAGE_SET

    @property
    def endpoint_url(self):
        return self.url.split('?')[0]

    @property
    @repr_return
    def status(self):
        if self.error is not None:
            return "Exception: %s %s" % (self.status_code or '', self.name)
        if self._stage is STAGE_DONE or self._stage is STAGE_DONE_DATA_FORMATTED:
            return '[' + str(self.status_code) + '] ' + self._stage
        return 'API Call stuck at stage: ' + self._stage

    @property
    @repr_return
    def report(self):
        return self.url + '\n' + str(
            self.error or self.data)

    def __getitem__(self, item):
        return eval('self.' + str(item))

    @property
    def response_cookies(self):
        """
        This will return all cookies set
        :return: dict {name, value}
        """
        try:
            ret = {}
            for cookie_base_uris in self.response.cookies._cookies.values():
                for cookies in cookie_base_uris.values():
                    for cookie in cookies.keys():
                        ret[cookie] = cookies[cookie].value
            return ret
        except Exception as e:
            self.error = ApiError("Exception in making Request with:: %s\n%s" % (e_, traceback.format_exc()))
            raise Exception(self.error)

    @property
    def timedelta(self):
        times = sorted([v for k, v in self._timestamps.items() if k != 'report'])
        return datetime.timedelta(seconds=times[-1] - times[0])

    @property
    def duration(self, significant_digits=3):
        """
        :param significant_digits: int of the number of significant digits in the return
        :return: float of the time in seconds of the api call request
        """
        try:
            return round(self._timestamps['receive'] - self._timestamps['send'], significant_digits)
        except Exception as e:
            return None

    @property
    def stream_time(self, significant_digits=3):
        """
        :param significant_digits: int of the number of significant digits in the return
        :return: float of the time in seconds of how long the data took to stream
        """
        try:
            return round(self._timestamps['last_stream'] - self._timestamps['stream'], significant_digits)
        except Exception as e:
            return None

    @property
    def latency(self, significant_digits=3):
        """
        :param significant_digits: int of the number of significant digits in the return
        :return: float of the time in seconds of the api call or stream data
        """
        try:
            end = 'stream' in self._timestamps and 'stream' or 'receive'
            return round(self._timestamps[end] - self._timestamps['send'], significant_digits)
        except Exception as e:
            return None

    def __repr__(self):
        ret = '%s <%s> <%s> ' % (self.label.ljust(6), self.status.ljust(36), self.timedelta)
        ret += ' %s ' % self.method[:4].ljust(4).upper()
        ret += self.url
        if self.params:
            ret += '?' + ';'.join(['%s=%s' % (k, v) for k, v in self.params.items()])
        return ret

    def __str__(self):
        space = 20
        ret = [str_name_value(k, self[k]) for k in ['label', 'method', 'url']]
        cookies = [str_name_value(k, v) for k, v in self.cookies.items()]
        params = [str_name_value(k, v) for k, v in self.params.items()]
        request_header = [str_name_value(k, v) for k, v in self.headers.items()]
        response_header = [str_name_value(k, v) for k, v in getattr(self.response, 'headers', {}).items()]

        endpoint_params = [str_name_value(k, v) for k, v in self.endpoint_params.items()]
        if self.request_data is None:
            request_data = ['']
        elif isinstance(self.request_data, dict):
            request_data = [str_name_value(k, v) for k, v in self.request_data.items()]
        else:
            request_data = ['    ' + str(self.request_data)]

        status = [str_name_value(k, v) for k, v in {'status': self.status,
                                                    'elapsed': self.timedelta}.items()]

        timestamps = [str_name_value(k, self._timestamps[k]) for k in TIMESTAMPS_ORDER if k in self._timestamps]

        ret = ("Request:", '\n'.join(ret),
               "Endpoint Params:", '\n'.join(endpoint_params),
               "Request Params:", '\n'.join(params),
               "Request Data:", '\n'.join(request_data),
               "Request Header:", '\n'.join(request_header),
               "Response Header:", '\n'.join(response_header),
               "Cookies:", '\n'.join(cookies),
               'Curl:', '    ' + self.curl,
               "Response:", '\n'.join(status),
               "Timestamps:", '\n'.join(timestamps))

        ret = ("%s\n%s\n\n" * int(len(ret) / 2)) % ret
        if self.error is not None:
            ret += "Exception:\n    " + str(self.error)
        return ret

    @property
    @repr_return
    def curl(self):
        """
        This will generate a curl equivalent call
        :return: str
        """
        ret = 'curl -X %s ' % self.method
        ret += self.url
        if self.request_data:
            ret += " -d '%s'" % json.dumps(self.request_data)
        if self.headers:
            ret += ''.join([' -H "%s: %s"' % (k, v) for k, v in self.headers.items()])
        if self.cookies:
            ret += ' --cookie "%s"' % ('&'.join(['%s=%s' % (k, v) for k, v in self.cookies.items()]),)
        return ret

    @property
    @repr_return
    def safe_curl(self):
        """
        This will generate a curl equivalent call with the session ID and password removed
        :return: str
        """
        ret = 'curl -X %s ' % self.method
        ret += str(self.endpoint_url)
        if self.params:
            ret += '?' + '&'.join(
                ['%s=%s' % (k, [v, '[%s]' % k.upper()][k in ['A', 'token', 'password']]) for k, v in
                 self.params.items()])
        if self.request_data:
            ret += " -d '%s'" % json.dumps(self.request_data)
        if self.headers:
            ret += ''.join(
                [' -H "%s: %s"' % (k, v if k != 'Authorization' else '[API_KEY]:') for k, v in self.headers.items()])
        if self.cookies:
            ret += ' --cookie "%s"' % ('&'.join(['%s=%s' % (k, '[%s]' % k.upper()) for k, v in self.cookies.items()]),)
        return ret

    @property
    @repr_return
    def safe_url(self):
        """
        This will generate a url equivalent call without private parameters
        :return: str
        """
        ret = str(self.endpoint_url)
        if self.params:
            ret += '?' + '&'.join(
                ['%s=%s' % (k, [v, '[%s]' % k.upper()][k in ['A', 'token', 'password', 'session']]) for k, v in
                 self.params.items()])
        return ret

    def send(self, stream_to_file=None):
        """
        This will perform the http request.
        stream_to_file: str of the file name to stream the data too
        :return: str of status
        """
        try:
            self._stage = STAGE_REQUEST
            self.prepared_request.prepare(method=self.method,
                                          url=self.endpoint_url,
                                          files=self.files,
                                          json=self.json,
                                          data=self.data,
                                          headers=self.headers,
                                          params=self.params,
                                          cookies=self.cookies,
                                          hooks=self.hooks)

        except Exception as e1:
            self.error = ApiError("Exception in making Request with:: %s\n%s" % (e1, traceback.format_exc()))
            raise Exception(self.error)

        try:
            self._stage = STAGE_SENDING
            self._timestamps['send'] = time.time()
            self.response = self.session.send(self.prepared_request,
                                              proxies=self.proxies,
                                              timeout=self.timeout,
                                              stream=bool(stream_to_file),
                                              verify=VERIFY,
                                              cert=None)
            self._stage = STAGE_RESPONDING
            self._timestamps['receive'] = time.time()
        except Exception as e2:
            self._timestamps.setdefault('exception', time.time())
            self.error = e2  # todo ApiError("Exception in Session Send", status_description=str(e))
            raise

        self.post_process(stream_to_file)
        self._stage = (self.name == 'Unknown') and STAGE_DONE_DATA_FORMATTED or STAGE_DONE
        return self.data

    def post_process(self, stream_to_file=False):
        """
        This will set error for an exception if the call isn't in the 200s.
        It will also extract the raw data from the response
        :stream_to_file: str of the file name to stream the data to
        :return: None
        """
        self.status_code = self.response.status_code
        if 200 <= self.status_code < 300:
            if stream_to_file:
                self.stream_to_file(stream_to_file)
            else:
                self.extract_data()
        else:
            self._timestamps.setdefault('exception', time.time())
            if self.status_code in HTTP_STATUS_CODES:
                self.error = HTTP_STATUS_CODES[self.status_code].str_to_obj(self.response.content)
            else:
                self.error = Exception('Status code = %s' % self.status_code)
            raise self.error

    def stream_to_file(self, filename):
        """
        :param filename: str of the file name to stream the data to
        :return: None
        """
        stream_size = 0
        try:
            partial_chunk = ''
            chunk_size = 1024
            m3u8_dir = None
            if filename[-5:].lower() == '.m3u8':
                self.repeat_needed = True
                m3u8_dir = self.get_ts_folder(filename)

            self.content_length = self.response.headers.get('Content-Length', None)
            self.content_length = self.content_length or self.response.headers.get('x-een-svc-renderer-file-size', None)
            self.content_length = eval(str(self.content_length))  # todo test if this is needed

            start_time = time.time()
            with open(filename, 'a') as fn:
                for chunk in self.response.iter_content(chunk_size=chunk_size):
                    stream_size += len(chunk)
                    if chunk:  # filter out keep-alive new chunks
                        self._timestamps.setdefault('stream', time.time())
                        self._timestamps['last_stream'] = time.time()
                        if m3u8_dir:
                            chunk, partial_chunk = self.download_ts(m3u8_dir, partial_chunk + chunk,
                                                                    chunk >= chunk_size)
                        elif False:
                            percent = self.content_length and round(stream_size * 100.0 / self.content_length,
                                                                    1) or '--'
                            time_delta = round(time.time() - self._timestamps['stream'], 3)
                            # print("Downloaded chunk of %s bytes out of a total of %s bytes      %s  complete    %s seconds" % (
                            #     str(len(chunk)).ljust(4), str(stream_size).rjust(len(str(self.content_length))),
                            #     percent, time_delta))

                        fn.write(chunk)
                        fn.flush()
                    if self.max_duration and time.time() - start_time > self.max_duration:
                        break
                    if self.max_size and stream_size > self.max_size:
                        break

                if partial_chunk:  # if the last message happen to be of size chunk_size
                    fn.write(self.download_ts(m3u8_dir, partial_chunk)[0])
                    fn.flush()
        except ZeroReturnError as e:
            pass
        except Exception as e:
            self._timestamps.setdefault('exception', time.time())
            self.error = ApiError("Failed to Stream Data to file:%s" % filename,
                                  status_code=self.status_code,
                                  status_description=str(e),
                                  url=self.response.url)
            raise Exception(self.error)

        self.raw_data = self.data = self.filename + ' size = ' + str(self.content_length)
        self.content_length = self.content_length or stream_size

    @staticmethod
    def get_ts_folder(filename):
        return '/ts_'.join(os.path.split(filename[:-5]))  # folder is the file name without the extension + ts_

    def download_ts(self, path, chunk, process_last_line=True):
        """
        This will look for a download ts link.  It will then download that file and replace the link with the local file.
        :param process_last_line:
        :param path:  str of the path to put the file
        :param chunk: str of the chunk file, note this could have partial lines
        :return:      str of the chunk with the local file link
        """
        import glob

        ret_chunk = []
        partial_chunk = ''
        lines = chunk.strip().split('\n')
        if not process_last_line:
            partial_chunk = lines.pop()

        for line in lines:
            if line.startswith('http:'):
                ts = '%s/%s.ts' % (path, line.split('.ts?')[0].split('/')[-1])
                relative_ts = '%s/%s.ts' % (path.split('/')[-1], line.split('.ts?')[0].split('/')[-1])
                if not os.path.exists(ts):  # this could be a repeat call
                    # log.debug("Downloading: %s at %s" % (line, time.time()))
                    gevent.spawn(ApiCall.save_url_to_file, line, ts).start()
                    gevent.sleep(0)
                    ret_chunk.append('# ' + line)
                    ret_chunk.append(relative_ts)
                    # log.debug("Done Downloading = %s"%time.time())
                else:
                    ret_chunk = []  # start over
            else:
                ret_chunk.append(line)

        if '#EXT-X-ENDLIST' in chunk:
            self.repeat_needed = 0
            gevent.sleep(0)
        elif chunk.strip():
            self.repeat_needed = 1 + len(glob.glob(path + '/*.ts'))

        ret_chunk = ret_chunk and '\n'.join(ret_chunk) + '\n' or ''
        return ret_chunk, partial_chunk

    @staticmethod
    def save_url_to_file(url, file_):
        try:
            response = requests.get(url)
            # log.debug("Saving to %s"%file)
            with open(file_, 'w') as local:
                data = response.content
                local.write(data)
        except Exception as e:
            log.error("Error with downloading %s\n%s" % (file_, e), exc_info=True)

    def extract_data(self):
        """
        This will will extract the raw data from the response
        :return: None
        """
        content_type = 'Exception in extracting content-type from header'
        try:
            content_type = self.response.headers.get('content-type', '')
            if 'application/json' in content_type:
                self.raw_data = self.data = self.response.json()
            elif self.prepared_request.headers.get('Accept', '') == 'application/json':  # todo fix this
                try:
                    self.raw_data = self.data = self.response.json()
                except Exception as e:
                    self.raw_data = self.data = self.response.content
            else:
                self.raw_data = self.data = self.response.content

            if isinstance(self.data, dict) and 'server_timing' in self.data.keys():
                self._server_timing = self.data.pop('server_timing', )  # this is internal timing debug info
                self.raw_data = self.data = self.data['original_response']

        except Exception as e:
            self._timestamps.setdefault('exception', time.time())
            self.error = ApiError("Invalid Response Data with content type: " + content_type,
                                  status_code=self.status_code,
                                  status_description=str(e),
                                  http_body=self.response.content,
                                  url=self.response.url)
            raise Exception(self.error)

    def save_formatted_data(self, data):
        """
        This will save the formatted data as a repr object (see returns.py)
        :param data: dict of the return data
        :return: None
        """
        self.data = data
        self._timestamps['process'] = time.time()
        self._stage = STAGE_DONE_DATA_FORMATTED

    def time_report_item(self, label, message=None):
        """
        This will return a dictionary for the given message based on timestamps
        :param label:
        :param message: str of the message, the first word is used to find the timestamp
        :return:        dict of times
        """
        next_ = TIMESTAMPS_ORDER[TIMESTAMPS_ORDER.index(label) + 1]
        while not next_ in self._timestamps:
            next_ = TIMESTAMPS_ORDER[TIMESTAMPS_ORDER.index(next_) + 1]

        assert label in TIMESTAMPS_ORDER
        start = self._timestamps[label] - self._timestamps[TIMESTAMPS_ORDER[0]]
        end = self._timestamps[next_] - self._timestamps[TIMESTAMPS_ORDER[0]]
        return {'Message': message,
                'Start': start,
                'End': end,
                'Sum': end - start,
                'Count': 1}

    @repr_return
    def time_report(self, include_overhead=False, header=None, include_server=True, digits=4):
        """
            Returns a str table of the times for this api call
        :param include_overhead: bool if True include information from overhead, such as the time for this class code
        :param header:           bool if True includes the column header
        :param include_server:   bool if True includes times reported by the server in the header
        :param digits:           int of the number of significant digits
        :return:                 str table of the times for the api call
        """
        try:
            self._timestamps.setdefault('report', time.time())
            header = header or ['Message', 'Start', 'End', 'Sum', 'Count']

            ret = []
            if include_overhead:
                ret.append(self.time_report_item('create', 'Overhead from api call "Create"'))
                ret.append(self.time_report_item('setup', 'Overhead from api call "Setup"'))

            if 'repeat' in self._timestamps:
                ret.append(self.time_report_item('repeat', 'First Request of the api call'))

            ret.append(self.time_report_item('send', 'Send the api call'))

            if self._server_timing and include_server:

                send_start = ret[-1]['Start']
                delta = max(0, ret[-1]['Sum'] - (self._server_timing['End'] - self._server_timing['Start']))

                if include_overhead:
                    ret.append({'Message': "Internet overhead", "Start": send_start,
                                "End": ret[0]['Start'] + delta, 'Sum': delta, 'Count': 1})

                    if 'Overhead' in self._server_timing:
                        ret.append({'Message': "Time profile overhead",
                                    "Start": send_start + delta,
                                    'Sum': self._server_timing['Overhead'],
                                    'End': send_start + delta + self._server_timing['End'] - self._server_timing[
                                        'Start'],
                                    'Count': sum(
                                        [len(msg.get('Times', [])) for msg in self._server_timing['Messages']]) + 1})

                    for msg in self._server_timing['Messages']:
                        ret.append(msg.copy())
                        ret[-1]['Start'] = ret[-1].setdefault('Start', 0) + delta + send_start
                        ret[-1]['End'] = ret[-1].setdefault('End', ret[-1]['Sum']) + delta + send_start
                else:
                    ret += self._server_timing['Messages']

            if 'stream' in self._timestamps:
                ret.append(self.time_report_item('stream', 'Streaming the api call'))

            if include_overhead:
                ret.append(self.time_report_item('receive', 'Overhead from api call "Post Processing"'))

            return 'Total Time: %s \t\tStart Time: %s\n%s' % (round(self.timedelta.total_seconds(), digits),
                                                              reformat_date(self._timestamps.get('send', '')),
                                                              str(ReprListDict(ret, col_names=header,
                                                                               digits=digits).list_of_list()))
        except Exception as e_:
            return "Exception creating time report with %s" % e_.message

    def save(self, filename=None, clean_data=False, raw=False, trash=False):
        """
        This will save the data to a filename
        :param clean_data: func call that will clean the data before saving it
        :param raw:        obj of the return object from request
        :param trash:      bool if true puts the file in the Trash folder
        :param filename:   str of the file to save to.
        :return:           str of the full path of the file
        """
        full_path = get_filename(filename or self.filename or self.name, trash)
        data = raw and self.raw_data or self.data

        if clean_data:
            data = self.clean_data(data)

        with open(full_path, 'w') as fn:
            if filename.endswith('.json'):
                fn.write(json.dumps(data, indent=2, separators=(',', ': ')))
            else:
                fn.write(str(data))
        self.filename = full_path
        return full_path

    def open_as_file(self, filename=None, clean_data=True, raw=False, trash=True):
        """
        This will save the file and then run a system command to open it.
        The default path will be the users trash folder
        :param clean_data: func call that will clean the data before saving it
        :param raw:        obj of the return object from request
        :param trash:      bool if true puts the file in the Trash folder
        :param filename:   str of the name of the file
        :return:           str of the full path
        """
        if filename or not self.filename:
            full_path = filename and get_filename(filename or self.filename, trash)
            if full_path != self.filename or not os.path.exists(full_path):
                self.filename = self.save(filename or self.name, clean_data, raw, trash)

        os.system('open ' + self.filename)

    @staticmethod
    def clean_data(data):
        """
            This will modify the data to make it more palatable
        :param data: str
        :return: str
        """
        if isinstance(data, dict):
            data = ReprDict(data)
        return data

    @property
    def sub_base_uri(self):
        """ This will return the sub_base_uri parsed from the base_uri
        :return: str of the sub_base_uri
        """
        return self.base_uri and self.base_uri.split('://')[-1].split('.')[0] or self.base_uri


STAGE_INIT = 'Init'
STAGE_SETTING = 'Setting up Request'
STAGE_SET = 'Call is Setup'
STAGE_REQUEST = 'Creating Request'
STAGE_SENDING = 'Sending Request'
STAGE_RESPONDING = 'Response Received'
STAGE_DONE = 'Call Completed Successfully, but without Formatted Data'
STAGE_DONE_DATA_FORMATTED = 'Call Completed Successfully'

if __name__ == '__main__':
    api_call = ApiCall(method='get',
                       base_uri='https://api.puzzlesandpotions.com/test')
                       # proxies={'http': 'http://127.0.0.1:4666', 'https': 'https://127.0.0.1:4665'})
    try:
        assert api_call.send()== 'Hello World!'
        print(str(api_call))
    except Exception as e:
        print("Exception: %s" % e)
        raise