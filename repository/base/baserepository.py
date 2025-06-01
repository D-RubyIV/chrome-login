from datetime import datetime

from sqlalchemy.orm import Session
from typing import Type, TypeVar, List, Generic, Any
from sqlalchemy.dialects.sqlite import insert

from config.config import DEBUG_MODIFY
from equipment.alchemy import SessionManager, db
from equipment.models import BaseModel
from logger.logger import my_logger

# Type variable toast represent any SQLAlchemy model
T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, domain: Type[T]):
        self.domain: BaseModel = domain
        self.session_manager = SessionManager

    def get_session(self) -> Session:
        return self.session_manager.get_session()

    @db
    def get_entities(self, session: Session) -> List[T]:
        return session.query(self.domain).all()

    @db
    def create_entity(self, entity: T, session: Session):
        session.add(entity)
        session.commit()
        session.refresh(entity)
        return entity

    @db
    def create_entities(self, entity_list: List[T], session: Session):
        session.add_all(entity_list)
        session.commit()
        return entity_list

    @db
    def find_by_id(self, entity_id: str, session: Session) -> T:
        return session.query(self.domain).filter_by(id=entity_id).first()

    @db
    def update_entity(self, entity_id: str, entity: T, session: Session):
        if DEBUG_MODIFY:
            if session.object_session(entity) is None:
                print("Entity is not in the session")
                # Nếu entity không thuộc session, có thể gọi merge() để đưa vào session
            else:
                print("Entity is in the session")
            if entity in session.dirty:
                print("Entity has been modified")
            else:
                print("Entity has not been modified")
        # session.flush()
        session.commit()
        return entity

    @db
    def delete_entity(self, entity: T, session: Session) -> None:
        session.delete(entity)
        session.commit()

    @db
    def delete_entity_by_id(self, entity_id: int, session: Session) -> None:
        e = session.query(self.domain).filter_by(id=entity_id).first()
        if e:
            session.delete(e)
            session.commit()

    @db
    def update_field_for_all(self, field_name: str, new_value: Any, session: Session) -> None:
        session.query(self.domain).update(
            {field_name: new_value}, synchronize_session=False
        )
        session.commit()

    @db
    def upsert_records(self, records: list, unique_columns: list, update_columns: list, session: Session):
        """
        Thực hiện upsert (insert/update) cho một model cụ thể.

        :param session: Phiên làm việc với cơ sở dữ liệu.
        :param model: Model SQLAlchemy.
        :param records: Danh sách các đối tượng cần chèn hoặc cập nhật.
        :param unique_columns: Các cột tạo nên ràng buộc uniqueness cho upsert.
        :param update_columns: Các cột cần được cập nhật nếu đã tồn tại.
        """
        my_logger.info(f"UPSERT[{self.domain.__table__}] - Tổng số: {len(records)}")

        if len(records) > 0:
            # Log thông tin về các cột và giá trị
            my_logger.info({column.name: getattr(records[0], column.name) for column in self.domain.__table__.columns})
            my_logger.info({column: getattr(records[0], column) for column in update_columns})

        for record in records:
            # Tạo một dictionary chứa giá trị cho các cột
            record_values = {}

            # Duyệt qua các cột trong bảng và lấy giá trị tương ứng
            for column in self.domain.__table__.columns:
                column_value = getattr(record, column.name)

                # Nếu cột là khóa ngoại, lấy giá trị ID của đối tượng liên kết
                if column.foreign_keys:
                    # print("Cột khóa ngoại" + str(column.name))
                    foreign_key_info = next(iter(column.foreign_keys))
                    referenced_table = foreign_key_info.column.table.name
                    referenced_column = foreign_key_info.column.name

                    referenced_table_value = getattr(record, referenced_table, column_value)
                    # print(referenced_table_value)
                    if referenced_table_value is not None:
                        column_value = getattr(referenced_table_value, referenced_column,
                                               column_value)  # Lấy id của đối tượng liên kết
                    # print("Giá trị cột: " + str(column_value))

                if column.name == "created_time" or column.name == "updated_time":
                    column_value = datetime.now().replace(microsecond=0)
                record_values[column.name] = column_value

            # Tạo câu lệnh insert với các giá trị
            stmt = insert(self.domain).values(record_values)

            # Thực hiện upsert (nếu có trùng sẽ update)
            stmt = stmt.on_conflict_do_update(
                index_elements=unique_columns,  # Các cột đánh dấu trùng lặp
                set_={column: getattr(record, column) for column in update_columns}  # Các cột cần cập nhật
            )

            session.execute(stmt)

        session.commit()