import pytest  # noqa
from models import Customer
pytestmark = pytest.mark.basemodel
# ______________________________


def test_machine_queries_object(db):
    customer = Customer()
    assert hasattr(customer, 'query')
    assert hasattr(customer.query, 'db')
    assert hasattr(customer.query.db, 'cursor')
    assert type(customer.query.db.cursor).__name__ == 'DictCursor'

# ______________________________


def test_customer_create(db):
    c = Customer()
    customers = [
        dict(
            name='British Telecom',
            web='home.bt.com',
        ),

        dict(
            name='Cellcom',
            web='cellcom.co.il',
        ),

        dict(
            name='Mahle GmbH',
            web='www.mahle.com',
        ),

    ]

    for customer in customers:
        rowid = c.add(customer)
        print("Row ID: {}".format(rowid))
        assert type(rowid).__name__ == 'int'

# ____________________________________
