import json
import os
from django.test import TestCase


from characters.services import (
    get_key,
    get_level,
)
from users.models import CustomUser


CUR_DIR = os.path.dirname(__file__)


class ServicesTest(TestCase):
    fixtures = ['characters.json', 'characters_api_key.json']

    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.user = CustomUser.objects.create_user(
            email='test@cc.com',
            password='test123',
            url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )

    def test_get_key(self):
        status_code, response_data = get_key(
            user=self.user,
        )
        self.assertEqual(status_code, 200)

    def test_get_level(self):
        path = f'{self.path}/get_level'
        fixtures = (
            (200, 'valid'),
            (200, 'valid_but_not_provided'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = get_level(
                api_key=data['api_key'],
            )
            self.assertEqual(status_code, code, msg=fixture)
