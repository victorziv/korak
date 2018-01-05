import pytest  # noqa
from models import Machine
pytestmark = pytest.mark.basemodel
# ______________________________


def test_machine_queries_object(db):
    machine = Machine()
    assert hasattr(machine, 'query')
    assert hasattr(machine.query, 'db')
    assert hasattr(machine.query.db, 'cursor')
    assert type(machine.query.db.cursor).__name__ == 'DictCursor'

# ______________________________


def test_machine_create(db):
    m = Machine()
    iboxes = [
        dict(
            name='ibox1590',
            machineid='1590',
            ticket='MAN-1223',
            owner='bobo@infinidat.com',
            iboxmodel='F6XXX',
        ),

        dict(
            name='ibox1692',
            machineid='1692',
            ticket='MAN-1245',
            owner='pennyl@infinidat.com',
            iboxmodel='F4XXX',
        ),
    ]

    for ibox in iboxes:
        rowid = m.add(ibox)
        print("Row ID: {}".format(rowid))
        assert type(rowid).__name__ == 'int'

# ______________________________


def test_customer_update(db):
    machine = Machine()
    customer_name = "Cellcom"
    machineid = '1590'

    machine.query.update_customer(machineid=machineid, customer_name=customer_name)
