from repository.piientity import PIIGroup,PIIEntity
import logging
from util import getCurrentDateTime
from repository.dbhandler import GetSession
from sqlalchemy.orm import joinedload

class PIIRepository:

    @staticmethod
    def readall():
        with GetSession() as session:
            try:
                return session.query(PIIGroup ).options(joinedload(PIIGroup.piientities)).order_by(PIIGroup.group_name).all()
            except Exception as e:
                raise e
            finally:
                session.close()