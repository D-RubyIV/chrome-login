from typing import TypeVar, Generic, Type, List, Any

from equipment.alchemy import transactional
from equipment.models import BaseModel
from repository.base.baserepository import BaseRepository

R = TypeVar("R", bound=BaseRepository)
T = TypeVar("T", bound=BaseModel)


class BaseService(Generic[R, T]):
    def __init__(self, repo: R, entity: Type[T]):
        self.repo: BaseRepository = repo
        self.entity = entity()

    @transactional
    def find_by_id(self, entity_id: str) -> T:
        return self.repo.find_by_id(entity_id=entity_id)

    @transactional
    def create_entities(self, list_entity) -> T:
        return self.repo.create_entities(list_entity)

    @transactional
    def create_entity(self, entity) -> T:
        return self.repo.create_entity(entity)

    @transactional
    def get_entity(self) -> T:
        return self.entity

    @transactional
    def get_entities(self) -> List[T]:
        return self.repo.get_entities()

    @transactional
    def update_entity(self, entity_id: str, entity: T) -> T:
        return self.repo.update_entity(entity_id, entity)

    @transactional
    def delete_entity(self, entity):
        if entity is None:
            raise ValueError("The entity to delete cannot be None")
        self.repo.delete_entity(entity)

    @transactional
    def delete_entity_by_id(self, entity_id: str):
        self.repo.delete_entity_by_id(entity_id)

    @transactional
    def update_field_for_all(self, field_name: str, new_value: Any) -> None:
        self.repo.update_field_for_all(field_name, new_value)

    @transactional
    def upsert_records(self, records, unique_columns, update_columns):
        return self.repo.upsert_records(
            records=records,
            unique_columns=unique_columns,
            update_columns=update_columns,
        )