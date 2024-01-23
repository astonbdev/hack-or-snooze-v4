import json

from django.test import TestCase

# from django.db.utils import IntegrityError
# from django.core.exceptions import ValidationError, ObjectDoesNotExist

# from ninja.errors import AuthenticationError

# from users.models import User
from users.factories import UserFactory, FACTORY_USER_DEFAULT_PASSWORD
# NOTE: do we want to use AUTH_KEY constant or hardcode string "token" in tests?
from users.auth_utils import generate_token, AUTH_KEY
# from users.schemas import SignupInput, LoginInput

from stories.factories import StoryFactory

EMPTY_TOKEN_VALUE = ''
MALFORMED_TOKEN_VALUE = 'malformed::token'
INVALID_TOKEN_VALUE = 'user:abcdef123456'


class APIStoriesPostTestCase(TestCase):
    """Test POST /stories endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.user_2 = UserFactory(username="user2")
        cls.staff_user = UserFactory(username="staffUser", is_staff=True)

        cls.user_token = generate_token(cls.user.username)
        cls.user2_token = generate_token(cls.user_2.username)
        cls.staff_user_token = generate_token(cls.staff_user.username)

        cls.valid_data = {
            "author": "post_test_author",
            "title": "post_test_title",
            "url": "post_test_url"
        }

    def test_post_story_ok_as_self(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        # extract the data that is dynamically generated by the model
        response_json = json.loads(response.content)
        response_date_created = response_json["story"]["created"]
        response_date_modified = response_json["story"]["modified"]
        response_id = response_json["story"]["id"]

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "story": {
                    "username": self.user.username,
                    "id": response_id,
                    "title": self.valid_data["title"],
                    "author": self.valid_data["author"],
                    "url": self.valid_data["url"],
                    "created": response_date_created,
                    "modified": response_date_modified
                }
            }
        )

    def test_post_story_ok_as_staff(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
            headers={AUTH_KEY: self.staff_user_token},
            content_type="application/json"
        )

        # extract the data that is dynamically generated by the model
        response_json = json.loads(response.content)
        response_date_created = response_json["story"]["created"]
        response_date_modified = response_json["story"]["modified"]
        response_id = response_json["story"]["id"]

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "story": {
                    "username": self.staff_user.username,
                    "id": response_id,
                    "title": self.valid_data["title"],
                    "author": self.valid_data["author"],
                    "url": self.valid_data["url"],
                    "created": response_date_created,
                    "modified": response_date_modified
                }
            }
        )

    def test_post_story_fail_unauthorized_no_token_header(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_post_story_fail_unauthorized_token_header_empty(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
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

    def test_post_story_fail_unauthorized_malformed_token(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
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

    def test_post_story_fail_unauthorized_invalid_token(self):

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(self.valid_data),
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

    def test_post_story_fail_missing_data(self):

        invalid_data = {
            "author": "post_test_author",
            "url": "post_test_url"
        }

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(invalid_data),
            headers={AUTH_KEY: self.user_token},
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
                            "title"
                        ],
                        "msg": "Field required"
                    }
                ]
            }
        )

    def test_post_story_unprocessable_extra_fields(self):

        invalid_data = {
            **self.valid_data,
            "extra_field": "post_test_extra"
        }

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(invalid_data),
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

    def test_post_story_no_data(self):

        response = self.client.post(
            '/api/stories/',
            headers={AUTH_KEY: self.user_token},
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
                            "author"
                        ],
                        "msg": "Field required"
                    },
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "data",
                            "title"
                        ],
                        "msg": "Field required"
                    },
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "data",
                            "url"
                        ],
                        "msg": "Field required"
                    }
                ]
            }
        )

    def test_post_story_wrong_data_type(self):

        invalid_data = {
            "author": 1,
            "title": 2,
            "url": 3,
        }

        response = self.client.post(
            '/api/stories/',
            data=json.dumps(invalid_data),
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertJSONEqual(
            response.content,
            {
                "detail": [
                    {
                        "type": "string_type",
                        "loc": [
                            "body",
                            "data",
                            "author"
                        ],
                        "msg": "Input should be a valid string"
                    },
                    {
                        "type": "string_type",
                        "loc": [
                            "body",
                            "data",
                            "title"
                        ],
                        "msg": "Input should be a valid string"
                    },
                    {
                        "type": "string_type",
                        "loc": [
                            "body",
                            "data",
                            "url"
                        ],
                        "msg": "Input should be a valid string"
                    }
                ]
            }
        )


class APIStoriesGETAllTestCase(TestCase):
    """Test GET /stories endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.story_1 = StoryFactory()
        cls.story_2 = StoryFactory()

    def test_get_all_stories_works(self):
        response = self.client.get(
            '/api/stories/',
            content_type="application/json"
        )

        # extract the date_time fields from the json to insert into our
        # test
        response_json = json.loads(response.content)
        response_dates_story1 = {
            "created": response_json["stories"][0]["created"],
            "modified": response_json["stories"][0]["modified"]
        }
        response_dates_story2 = {
            "created": response_json["stories"][0]["created"],
            "modified": response_json["stories"][0]["modified"]
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "stories": [
                    {
                        "username": self.story_1.user.username,
                        "id": self.story_1.id,
                        "title": self.story_1.title,
                        "author": self.story_1.author,
                        "url": self.story_1.url,
                        "created": response_dates_story1["created"],
                        "modified": response_dates_story1["modified"]
                    },
                    {
                        "username": self.story_2.user.username,
                        "id": self.story_2.id,
                        "title": self.story_2.title,
                        "author": self.story_2.author,
                        "url": self.story_2.url,
                        "created": response_dates_story2["created"],
                        "modified": response_dates_story2["modified"]
                    }

                ]
            }
        )


class APIStoriesGETOneTestCase(TestCase):
    """Test GET /stories/{story_id} endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.story_1 = StoryFactory()

    def test_stories_get_one_works(self):

        response = self.client.get(
            f'/api/stories/{self.story_1.id}',
            content_type="application/json"
        )

        # extract the date_time fields from the json to insert into our
        # test
        response_json = json.loads(response.content)
        response_dates_story1 = {
            "created": response_json["story"]["created"],
            "modified": response_json["story"]["modified"]
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "story": {
                    "username": self.story_1.user.username,
                    "id": self.story_1.id,
                    "title": self.story_1.title,
                    "author": self.story_1.author,
                    "url": self.story_1.url,
                    "created": response_dates_story1["created"],
                    "modified": response_dates_story1["modified"]
                }
            }
        )

    def test_stories_get_one_404(self):

        response = self.client.get(
            '/api/stories/nonexistent-id',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Not Found"
            }
        )


class APIStoriesDELETETestCase(TestCase):
    """Test DELETE /stories endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.user_2 = UserFactory(username="user2")
        cls.staff_user = UserFactory(username="staffUser", is_staff=True)

        cls.user_token = generate_token(cls.user.username)
        cls.user2_token = generate_token(cls.user_2.username)
        cls.staff_user_token = generate_token(cls.staff_user.username)

        cls.story_1 = StoryFactory()

    def test_delete_story_ok_as_self(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "deleted": True,
                "id": self.story_1.id
            }
        )

    def test_delete_story_ok_as_staff(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
            headers={AUTH_KEY: self.staff_user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "deleted": True,
                "id": self.story_1.id
            }
        )

    def test_delete_story_fails_unauthorized_no_token_header(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {
                "detail": "Unauthorized"
            }
        )

    def test_delete_story_unauthorized_fails_token_header_empty(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
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

    def test_delete_story_fails_unauthorized_malformed_token(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
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

    def test_delete_story_fails_unauthorized_invalid_token(self):

        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
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

    def test_delete_story_fails_unauthorized_wrong_user(self):
        response = self.client.delete(
            f'/api/stories/{self.story_1.id}',
            headers={AUTH_KEY: self.user2_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"detail": "Unauthorized."}
        )

    def test_delete_story_fails_not_found(self):
        response = self.client.delete(
            '/api/stories/nonexistent-id',
            headers={AUTH_KEY: self.user_token},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                'detail': 'Not Found'
            }
        )

# POST /
# works ok w/ user token ✅
# works ok w/ staff token ✅
# 401 unauthorized if no token (authentication)✅
# 401 unauthorized if malformed token (authentication)✅
# 401 unauthorized if invalid token (authentication)✅
# OTHER TESTS:
# 422 missing data✅
# 422 extra data✅
# 422 no data✅
# 422 data wrong type✅

# GET /
# works ok✅

# GET /{story_id}
# works ok✅
# 404 if user not found✅

# DELETE /stores/{story_id}
# works ok w/ user token✅
# works ok w/ staff token✅
# 401 unauthorized if no token (authentication)✅
# 401 unauthorized if malformed token (authentication)✅
# 401 unauthorized if invalid token (authentication)✅
# 401 unauthorized if different non-staff user's token (authorization)✅
# OTHER TESTS:
# 404 if story_id not found✅
