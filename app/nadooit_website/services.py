import uuid
from .models import Session, Section


def get_next_section(session_id):
    pass


def check__session_id__is_valid(session_id: uuid):
    return Session.objects.filter(session_id=session_id).exists()
