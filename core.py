from typing import Optional, List

from db.models.account import Account
from enums import AccountType
from utils import get_db_client_instance


def add_account(
    account_number: str,
    account_type: AccountType,
    depositor_1: str, 
    depositor_2: Optional[str], 
    amount: int,
    maturity_date: str,
    agent: str
) -> str:
    """
    Adds an account in the database with given details.
    :param account_number: Account number.
    :param account_type: Either single or joint type of account.
    :param depositor_1: First account holder name.
    :param depositor_2: For joint account, second depositor name is must.
    :param amount: Monthly installment amount.
    :param maturity_date: Maturity date of the account.
    :param agent: Details of agent like "name (agent_code)".
    :return: Return id of the added account.
    """

    account = Account(
        account_number=account_number,
        account_type=account_type,
        depositor_1=depositor_1,
        depositor_2=depositor_2,
        amount=amount,
        maturity_date=maturity_date,
        agent=agent
    )

    db_client = get_db_client_instance()
    return account.save(db_client)


def fetch_accounts(account_ids: List[str]) -> List[Account]:
    """
    Searches accounts by given list of IDs and return those.
    :param account_ids: List of IDs of accounts to fetched from DB.
    :return: Returns matched accounts.
    """
    
    if account_ids:
        db_client = get_db_client_instance()
        accounts = Account.fetch(db_client, account_ids)
        return accounts
    else:
        raise ValueError("No account id given to search accounts.")
    
