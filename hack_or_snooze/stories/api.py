from ninja import Router
from .models import Story

router = Router()

# TODO: schema

# TODO: ENDPOINT STUBS

@router.post('/')
def post_story(request):
    pass

@router.get('/')
def get_stories(request, user_id: int):
    """Get all stories."""
    pass

@router.get('/{str:story_id}')
def get_story(request, story_id: str):
    """Get individual story by ID."""
    pass
        # FIXME: is there a UUID type for the id?