from equipment.models import ProfileRecord
from repository.base.baserepository import BaseRepository


class ProfileRepository(BaseRepository):
    def __init__(self):
        super().__init__(domain=ProfileRecord)