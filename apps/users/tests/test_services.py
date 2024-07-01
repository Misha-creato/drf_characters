import json
import os
from unittest.mock import patch

from django.test import TestCase

from users.models import CustomUser
from users.services import (
    auth,
    register,
    detail,
    remove,
    confirm_email,
    password_restore,
    password_restore_request,
)


CUR_DIR = os.path.dirname(__file__)


class ServicesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.user = CustomUser.objects.create_user(
            email='test@cc.com',
            password='test123',
            url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )

    @patch('users.services.send_email_by_type')
    def test_register(self, mock_send_email_by_type):
        mock_send_email_by_type.return_value = 200
        path = f'{self.path}/register'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid_structure'),
            (406, 'already_exists'),
            (400, 'password_mismatch'),
        )

        request = self.client.post('/').wsgi_request
        get_url_func = request.build_absolute_uri

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = register(
                data=data,
                get_url_func=get_url_func,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_auth(self):
        path = f'{self.path}/auth'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid_structure'),
            (401, 'not_authenticated'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = auth(
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_detail(self):
        status_code, response_data = detail(
            user=self.user,
        )

        self.assertEqual(status_code, 200)

    def test_remove(self):
        status_code, response_data = remove(
            user=self.user,
        )

        self.assertEqual(status_code, 200)

    def test_confirm_email(self):
        path = f'{self.path}/confirm_email'
        fixtures = (
            (200, 'valid'),
            (404, 'invalid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                url_hash = json.load(file)

            status_code, response_data = confirm_email(
                url_hash=url_hash,
            )

            self.assertEqual(status_code, code, msg=fixture)

    @patch('users.services.send_email_by_type')
    def test_password_restore_request(self, mock_send_email_by_type):
        mock_send_email_by_type.return_value = 200
        path = f'{self.path}/password_restore_request'
        fixtures = (
            (200, 'valid'),
            (406, 'wrong_email'),
            (400, 'invalid_email'),
            (400, 'invalid'),
        )

        request = self.client.post('/').wsgi_request
        get_url_func = request.build_absolute_uri

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = password_restore_request(
                data=data,
                get_url_func=get_url_func,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_password_restore(self):
        path = f'{self.path}/password_restore'
        fixtures = (
            (400, 'password_mismatch'),
            (404, 'invalid'),
            (200, 'valid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            url_hash = data.pop('url_hash')
            status_code, response_data = password_restore(
                url_hash=url_hash,
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)
