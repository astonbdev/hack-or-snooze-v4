import json

from django.test import TestCase

from users.factories import UserFactory, FACTORY_USER_DEFAULT_PASSWORD
from users.auth_utils import generate_token

AUTH_KEY = 'token'
EMPTY_TOKEN_VALUE = ''
MALFORMED_TOKEN_VALUE = 'malformed::token'
INVALID_TOKEN_VALUE = 'user:abcdef123456'


class APIAuthTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.existing_user = UserFactory()

        cls.valid_signup_data = {
            "username": "test",
            "password": "password",
            "first_name": "testFirst",
            "last_name": "testLast"
        }

        cls.valid_login_data = {
            "username": cls.existing_user.username,
            "password": FACTORY_USER_DEFAULT_PASSWORD
        }

    def test_signup_ok(self):
        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(self.valid_signup_data),
            content_type="application/json"
        )

        # get date_joined from response so we don't encounter
        # issues with differing dates
        response_json = json.loads(response.content)
        response_date_joined = response_json["user"]["date_joined"]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response_json,
            {
                AUTH_KEY: "test:098f6bcd4621",
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "test",
                    "first_name": "testFirst",
                    "last_name": "testLast",
                    "date_joined": response_date_joined
                }
            }
        )

    def test_signup_ok_with_hyphen_username(self):

        valid_data = {
            **self.valid_signup_data,
            "username": "user-name"
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(valid_data),
            content_type="application/json"
        )

        # get date_joined from response so we don't encounter
        # issues with differing dates
        response_json = json.loads(response.content)
        response_date_joined = response_json["user"]["date_joined"]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response_json,
            {
                AUTH_KEY: "user-name:f8e156340829",
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user-name",
                    "first_name": "testFirst",
                    "last_name": "testLast",
                    "date_joined": response_date_joined
                }
            }
        )

    def test_signup_ok_with_underscore_username(self):

        valid_data = {
            **self.valid_signup_data,
            "username": "user_name"
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(valid_data),
            content_type="application/json"
        )

        # get date_joined from response so we don't encounter
        # issues with differing dates
        response_json = json.loads(response.content)
        response_date_joined = response_json["user"]["date_joined"]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response_json,
            {
                AUTH_KEY: "user_name:c56f5648d4c0",
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user_name",
                    "first_name": "testFirst",
                    "last_name": "testLast",
                    "date_joined": response_date_joined
                }
            }
        )

    def test_signup_fail_missing_data(self):

        invalid_data = {
            "username": "test",
            "password": "password",
            "first_name": "testFirst",
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "data",
                            "last_name"
                        ],
                        "msg": "Field required"
                    }
                ]
            }
        )

    def test_signup_fail_unprocessable_extra_fields(self):
        invalid_data = {
            **self.valid_signup_data,
            "extra_field": "extra_value"
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "extra_forbidden",
                        "loc": [
                            "body",
                            "data",
                            "extra_field"
                        ],
                        "msg": "Extra inputs are not permitted"
                    }
                ]
            }
        )

    def test_signup_fail_username_exists(self):

        dupe_user_data = {
            **self.valid_signup_data,
            "username": self.existing_user.username
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(dupe_user_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Username already exists."
            }
        )

    def test_signup_fail_username_must_be_slugified(self):
        """Test username only contains slugified characters, otherwise token
        generation/validation may break."""

        invalid_data = {
            **self.valid_signup_data,
            "username": "test:username"
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Username must contain only numbers, letters, underscores or hyphens."
            }
        )

    def test_signup_fail_fields_must_meet_minimum_length(self):
        """Test first_name, last_name, password, meet minimum length
        requirements to register user"""

        invalid_data = {
            "username": "",
            "first_name": "",
            "last_name": "",
            "password": "",
        }

        response = self.client.post(
            '/api/users/signup',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)

        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "string_too_short",
                        "loc": [
                            "body",
                            "data",
                            "username"
                        ],
                        "msg": "String should have at least 2 characters",
                        "ctx": {
                            "min_length": 2
                        }
                    },
                    {
                        "type": "string_too_short",
                        "loc": [
                            "body",
                            "data",
                            "first_name"
                        ],
                        "msg": "String should have at least 2 characters",
                        "ctx": {
                            "min_length": 2
                        }
                    },
                    {
                        "type": "string_too_short",
                        "loc": [
                            "body",
                            "data",
                            "last_name"
                        ],
                        "msg": "String should have at least 2 characters",
                        "ctx": {
                            "min_length": 2
                        }
                    },
                    {
                        "type": "string_too_short",
                        "loc": [
                            "body",
                            "data",
                            "password"
                        ],
                        "msg": "String should have at least 5 characters",
                        "ctx": {
                            "min_length": 5
                        }
                    }
                ]
            }
        )

    def test_login_ok(self):
        response = self.client.post(
            '/api/users/login',
            data=json.dumps(self.valid_login_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                AUTH_KEY: "user:ee11cbb19052",
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_login_fail_missing_data(self):
        invalid_data = {
            "username": self.existing_user.username,
        }

        response = self.client.post(
            '/api/users/login',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "data",
                            "password"
                        ],
                        "msg": "Field required"
                    }
                ]
            }
        )

    def test_login_fail_unprocessable_extra_fields(self):
        invalid_data = {
            **self.valid_login_data,
            "extra_field": "extra_value"
        }

        response = self.client.post(
            '/api/users/login',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "extra_forbidden",
                        "loc": [
                            "body",
                            "data",
                            "extra_field"
                        ],
                        "msg": "Extra inputs are not permitted"
                    }
                ]
            }
        )

    def test_login_fail_username_does_not_exist(self):
        invalid_data = {
            "username": "nonexistent",
            "password": "password"
        }

        response = self.client.post(
            '/api/users/login',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Invalid credentials."
            }
        )

    def test_login_fail_invalid_password(self):
        invalid_data = {
            "username": self.existing_user.username,
            "password": "bad_password"
        }

        response = self.client.post(
            '/api/users/login',
            data=json.dumps(invalid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Invalid credentials."
            }
        )


class APIUserGetTestCase(TestCase):
    """Test GET /users/{username} endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.user_2 = UserFactory(username="user2")
        cls.staff_user = UserFactory(username="staffUser", is_staff=True)

        cls.user_token = generate_token(cls.user.username)
        cls.user2_token = generate_token(cls.user_2.username)
        cls.staff_user_token = generate_token(cls.staff_user.username)

    def test_get_user_ok_as_self(self):
        """Test that a user can get their own user information with a valid
        token."""

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: self.user_token}
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_get_user_ok_as_staff(self):
        """Test that a staff user can get a different user's information with a
        valid token."""

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: self.staff_user_token}
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_get_user_fail_unauthorized_no_token_header(self):

        response = self.client.get(
            '/api/users/user'
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_get_user_fail_unauthorized_token_header_empty(self):

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: EMPTY_TOKEN_VALUE}
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_get_user_fail_unauthorized_malformed_token(self):

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: MALFORMED_TOKEN_VALUE}
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_get_user_fail_unauthorized_invalid_token(self):

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: INVALID_TOKEN_VALUE}
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_get_user_fail_unauthorized_as_different_user(self):

        response = self.client.get(
            '/api/users/user',
            headers={AUTH_KEY: self.user2_token}
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_get_user_fail_bad_request_nonexistent_user_as_staff(self):

        response = self.client.get(
            '/api/users/nonexistent',
            headers={AUTH_KEY: self.staff_user_token}
        )

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                'detail': 'Not Found'
            }
        )


class APIUserPatchTestCase(TestCase):
    """Test PATCH /users/{username} endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.user_2 = UserFactory(username="user2")
        cls.staff_user = UserFactory(username="staffUser", is_staff=True)

        cls.user_token = generate_token(cls.user.username)
        cls.user2_token = generate_token(cls.user_2.username)
        cls.staff_user_token = generate_token(cls.staff_user.username)

    def test_patch_user_ok_all_fields_as_self(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "newFirst",
                    "last_name": "newLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_ok_some_fields_as_self(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "first_name": "newFirst",
            }),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "newFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_ok_all_fields_as_staff(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: self.staff_user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "newFirst",
                    "last_name": "newLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_ok_some_fields_as_staff(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "first_name": "newFirst",
            }),
            headers={AUTH_KEY: self.staff_user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "newFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_ok_empty_body(self):
        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({}),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_ok_all_fields_with_empty_strings(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "",
                "first_name": "",
                "last_name": ""
            }),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        # Assert we receive the correct response:
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "",
                    "last_name": "",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

        # Confirm we can log back in with blank password:
        login_response = self.client.post(
            '/api/users/login',
            data=json.dumps({
                "username": self.user.username,
                "password": ""
            }),
            content_type="application/json"
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "",
                    "last_name": "",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_can_reauthenticate_with_patched_password(self):
        """This test is to ensure a patched password is re-hashed and stored
        correctly, such that a user can re-authenticate with the new
        password."""

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
            }),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        # Assert we receive the correct response:
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

        # Confirm we can log back in with new password:
        login_response = self.client.post(
            '/api/users/login',
            data=json.dumps({
                "username": self.user.username,
                "password": "new_password"
            }),
            content_type="application/json"
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "user": {
                    "stories": [],
                    "favorites": [],
                    "username": "user",
                    "first_name": "userFirst",
                    "last_name": "userLast",
                    "date_joined": "2020-01-01T00:00:00Z"
                }
            }
        )

    def test_patch_user_fail_unauthorized_no_token_header(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_patch_user_fail_unauthorized_token_header_empty(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: EMPTY_TOKEN_VALUE},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_patch_user_fail_unauthorized_malformed_token(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: MALFORMED_TOKEN_VALUE},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_patch_user_fail_unauthorized_invalid_token(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: INVALID_TOKEN_VALUE},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_patch_user_fail_unauthorized_as_different_user(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: self.user2_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_patch_user_fail_bad_request_nonexistent_user_as_staff(self):

        response = self.client.patch(
            '/api/users/nonexistent',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast"
            }),
            headers={AUTH_KEY: self.staff_user_token},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                'detail': 'Not Found'
            }
        )

    def test_patch_user_fail_unprocessable_extra_fields(self):

        response = self.client.patch(
            '/api/users/user',
            data=json.dumps({
                "password": "new_password",
                "first_name": "newFirst",
                "last_name": "newLast",
                "extra_field": "extra_value"
            }),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "extra_forbidden",
                        "loc": [
                            "body",
                            "data",
                            "extra_field"
                        ],
                        "msg": "Extra inputs are not permitted"
                    }
                ]
            }
        )
