from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from ninja.errors import AuthenticationError

from stories.models import Story

# NICETOHAVE: remove email from the model since we will not
# be using it


class User(AbstractUser):
    """User model. Currently draws from AbstractUser with no additional
    columns."""

    # NICETOHAVE: model should include DB constraints on username pattern to
    # mirror schema validation?
    username = models.CharField(
        primary_key=True,
        max_length=150,
    )

    # Need to set blank=False, otherwise the ModelSchema from DjangoNinja will
    # interpret these fields as optional:
    first_name = models.CharField(
        max_length=150,
        blank=False,
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
    )

    # FIXME:Right now, this field is acting as a "Query that has not been fired off"
    # Essentially it is not a proper walkable ORM field
    # Research this for next time
    favorites = models.ManyToManyField(Story, related_name="favorited_by")

    @classmethod
    def signup(cls, user_data):
        """Sign up a new user with provided credentials.

        Returns user instance or raises IntegrityError on duplicate username."""

        user = cls.objects.create(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        user.set_password(raw_password=user_data.password)
        user.save()

        return user

    @classmethod
    def login(cls, user_data):
        """Log in an existing user with provided credentials.

        Returns user instance or raises error if credentials are incorrect."""

        user = cls.objects.get(username=user_data.username)

        if user.check_password(user_data.password):
            return user
        else:
            raise AuthenticationError("Unauthorized")


# class Favorite(models.Model):
#     """Favorite model.

#     A favorite is a many-to-many relationship between users and stories.
#     """

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.RESTRICT,
#         related_name='favorites',
#     )

#     story = models.ForeignKey(
#         'stories.Story',
#         on_delete=models.RESTRICT,
#     )

#     class Meta:
#         unique_together = ['user_id', 'story_id']
