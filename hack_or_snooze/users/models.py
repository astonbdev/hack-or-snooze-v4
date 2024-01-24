from django.db import models
from django.contrib.auth.models import AbstractUser

from ninja.errors import AuthenticationError

from stories.models import Story


class User(AbstractUser):
    """User model."""

    username = models.CharField(
        primary_key=True,
        max_length=150,
    )

    # password = models.CharField(_("password"), max_length=128)

    # TODO: test adding PW field with min_length - how does this play with
    # existing validators?

    # Need to set blank=False, otherwise the ModelSchema from DjangoNinja will
    # interpret these fields as optional in the schema and coerce
    # their value to None if not included on the request:
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
    )

    favorites = models.ManyToManyField(
        Story,
        related_name="favorited_by",
    )

    @classmethod
    def signup(cls, user_data):
        """Sign up a new user with provided credentials.

        Takes an instance of the SignupInput schema.

        Returns user instance or raises IntegrityError on duplicate username.
        """

        user = cls.objects.create_user(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=user_data.password
        )

        user.save()

        return user

    # TODO: investigate built-in login
    @classmethod
    def login(cls, user_data):
        """Log in an existing user with provided credentials.

        Takes an instance of the LoginInput schema.

        Returns user instance on success.

        Raises error if credentials are incorrect:
            - AuthenticationError on check_password fail
            - ObjectDoesNotExist on nonexistent username
        """

        user = cls.objects.get(username=user_data.username)

        if user.check_password(user_data.password) is True:
            return user
        else:
            raise AuthenticationError("Unauthorized")

    def update(self, patch_data):
        """Update user record and return updated user instance."""

        for field, value in patch_data.items():
            if (field == 'password'):
                self.set_password(raw_password=patch_data['password'])
            else:
                setattr(self, field, value)

        self.save()

        return self
