# -*- coding: utf-8 -*-
"""
Log in to Wattbike Hub and extract session data from user account.

*Requires creds.py script with USERNAME, PASSWORD variables*

Based off 'wblib' - https://github.com/AartGoossens/wblib
"""

import datetime
from os import path
import pandas as pd
import json
import requests
import creds

WATTBIKE_HUB_LOGIN_URL = 'https://api.wattbike.com/v2/login'
WATTBIKE_HUB_RIDESESSION_URL = 'https://api.wattbike.com/v2/classes/RideSession'
WATTBIKE_HUB_FILES_BASE_URL = \
    'https://api.wattbike.com/v2/files/{user_id}_{session_id}.{extension}'

class WattbikeClient:
    def __init__(self, username, password):
        """Initialize a :class:`WattbikeClient` instance.

        :param username: Wattbike user name or email address.
        :type username: str
        :param password: Wattbike account password.
        :type password: str

        """
        self.username = username
        self.password = password
        self.session_token = None

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('Exiting session')

    def _build_request_session(self):
        headers = {'Content-Type': 'application/json'}
        session = requests.Session()
        session.headers = headers
        return session

    def _post_request(self,url,payload):
        data = {
            '_method': 'GET',
            '_ApplicationId': 'Gopo4QrWEmTWefKMXjlT6GAN4JqafpvD',
            '_JavaScriptKey': 'p1$h@M10Tkzw#',
            '_ClientVersion': 'js1.6.14',
            '_InstallationId': 'f375bbaa-9514-556a-be57-393849c741eb'}

        if self.session_token:
            data.update({'_SessionToken': self.session_token})
        data.update(payload)

        with self._build_request_session() as session:
            response = session.post(
                url=url,
                data=json.dumps(data))

        if not response.ok:
            response.reason = response.content
        response.raise_for_status()

        return response.json()

    def login(self):
        self.session_token = None

        payload = {
            'username': self.username,
            'password': self.password}

        login_response = self._post_request(
            url=WATTBIKE_HUB_LOGIN_URL,
            payload=payload)

        self.session_token = login_response['sessionToken']
        self.user_id = login_response['objectId']
        print('Log in successful.')
        print('user_id: %s, session token: %s' % (self.user_id,self.session_token))

    def _get_session_ids(self, start_date=None, end_date=None):
        """Wattbike session headline data into class variable.

        All sessions recorded after 1st Jan 2019 by default.

        :param start_date: Start date of session search
        :type start_date: datetime object
        :param end_date: End date of session search
        :type end_date: datetime object

        """
        if not end_date:
            end_date = datetime.datetime.now()
        if not start_date:
            start_date = datetime.datetime(2019,1,1)

        payload = {
            'where': {
                'user': {
                    '__type': 'Pointer',
                    'className': '_User',
                    'objectId': self.user_id},
                'startDate': {
                    '$gt': {
                        '__type': 'Date',
                        'iso': start_date.isoformat()},
                    '$lt': {
                        '__type': 'Date',
                        'iso': end_date.isoformat()
                    }
                }
            }
        }
        response = self._post_request(
            url=WATTBIKE_HUB_RIDESESSION_URL,
            payload=payload)

        self.sessions = response['results']
        if not len(self.sessions):
            print('No results returned')

    def _get_session_data(self, session_id):
        response = requests.get(
            WATTBIKE_HUB_FILES_BASE_URL.format(
                user_id=self.user_id,
                session_id=session_id,
                extension='wbs'))
        response.raise_for_status()
        return response.json()

    def download_all(self):
        """ Given all headline data, pickle full session data and dump into
        '{dir}/wattbikesessions/{user_id}/{session_id}'

        """
        self._get_session_ids()
        count = 0
        for s in self.sessions:
            session_id = s['objectId']
            try:
                if path.exists('wattbikesessions/'+str(self.user_id)+'/'+str(session_id)):
                    continue
                else:
                    r = self._get_session_data(session_id)
                    if 'outcomes' in r.keys():
                        r.pop('outcomes')
                    df = pd.DataFrame(r)
                    df.to_pickle('wattbikesessions/'+str(self.user_id)+'/'+str(session_id))
                    print('session id:', session_id)
                    count += 1
            except Exception:
                print('FAILED id:', session_id)
                continue
        print('Downloaded files:',count,'/',len(self.sessions))
        return self

with WattbikeClient(creds.USERNAME,creds.PASSWORD) as client:
    client.download_all()
