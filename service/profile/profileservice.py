from equipment.models import ProfileRecord
from repository.profile.profilerepository import ProfileRepository
from service.base.baseservice import BaseService


class ProfileService(BaseService):
    def __init__(self):
        self.repo = ProfileRepository()
        super().__init__(self.repo, ProfileRecord)