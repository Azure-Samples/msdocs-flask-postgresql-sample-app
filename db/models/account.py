import logging
from typing import Optional, List, Tuple

from sqlalchemy import JSON, Column, String, Integer, CheckConstraint

from db.models.base import Base
from db.client import DopBuddyDbClient
from enums import AccountType


log = logging.getLogger(__name__)


class Account(Base):
    """
    This table will contain an account details.
    id      account_number  account_type    depositor_name_1    depositor_name_2    amount  maturity_date   agent_code
    1       1000034567      single      Ram                 Sita                2000    20-02-2027      3197
    """

    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    account_number = Column(String(30), unique=True, nullable=False)
    account_type = Column(String(20), nullable=False) # Single or joint
    depositor_1 = Column(String(50), nullable=False)
    depositor_2 = Column(String(50), nullable=True)
    amount = Column(Integer, nullable=False)    
    maturity_date = Column(String(50), nullable=False)
    agent = Column(String(20), nullable=False)

    @classmethod
    def fetch(cls, db_client: DopBuddyDbClient, ids: List[str]) -> Optional["Account"]:
        with db_client.get_session() as session:
            log.info(f"Fetching accounts for ids: {ids}")
            return session.query(Account).filter(Account.id.in_(ids)).all()
    
    def save(self, db_client: DopBuddyDbClient) -> str:
        _id = None
        is_valid, error_message = self._is_valid()
        if is_valid:
            log.info(f"Persisting account for number: {self.account_number}")
            with db_client.get_scoped_session() as session:
                session.add(self)
                session.flush()
                _id = self.id
            
            return _id
        else:
            raise ValueError(error_message)

    def _is_valid(self) -> Tuple:
        required_fields = [self.account_number, self.account_type, self.depositor_1, self.amount, self.maturity_date, self.agent]
        for field in required_fields:
            if not field:
                return False, f"Please make sure required fields are filled correctly!"
        
        acc_type = AccountType(self.account_type)
        if acc_type == AccountType.JOINT:
            # depositor_2 is must for a join account.
            if not self.depositor_2:
                return False, f"Since account type is {self.account_type}, hence 2nd depositor is must"
    
        return True, ""
