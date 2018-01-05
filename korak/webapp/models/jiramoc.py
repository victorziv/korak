import sys
from config import logger

issues = {
    1849: {
        'id': 1849,
        'name': 'ibox1849',
        'assignee': 'mzuchmer',
        'ticket_ivt': "MAN-1894",
        'ticket_shipment': "MAN-1997",
        'model': 'F6200',
        'customer': 'British Telecom',
        'labels': ['RPQ5'],
        'ivt_cycle': 5,
        'enclosure_drives': '3TB',
        'environment': 3,
        'created': '2017-11-13T12:37:46.000+0300'
    },

    1692: {
        'id': 1692,
        'name': 'ibox1692',
        'assignee': 'mzuchmer',
        'ticket_ivt': "MAN-1454",
        'ticket_shipment': "MAN-1857",
        'model': 'F6200',
        'customer': 'British Telecom',
        'labels': ['RPQ5'],
        'ivt_cycle': 5,
        'enclosure_drives': '3TB',
        'environment': 3,
        'created': '2017-08-15T12:37:46.000+0300'
    },

    1754: {
        'id': 1754,
        'name': 'ibox1754',
        'assignee': 'bobom',
        'ticket_ivt': "MAN-1528",
        'ticket_shipment': "MAN-1123",
        'model': 'F4200',
        'customer': 'Amdocs India',
        'enclosure_drives': '3TB',
        'labels': ['Coguar'],
        'ivt_cycle': 5,
        'environment': 11,
        'created': '2017-07-10T02:35:46.000+0300'
    },

    1802: {
        'id': 1802,
        'name': 'ibox1802',
        'assignee': 'debbyz',
        'ticket_ivt': "MAN-1014",
        'ticket_shipment': "MAN-1003",
        'model': 'F2400',
        'customer': "SAP",
        'enclosure_drives': '3TB',
        'ivt_cycle': 5,
        'labels': ['RPQ5', 'RPQ9'],
        'environment': 31,
        'created': '2017-09-12T12:35:46.000+0300'
    },

    1693: {
        'id': 1693,
        'name': 'ibox1693',
        'assignee': 'mzuchmer',
        'ticket_ivt': "MAN-2711",
        'ticket_shipment': "MAN-2901",
        'model': 'F6200',
        'customer': 'British Telecom',
        'labels': ['GreatJobEver'],
        'ivt_cycle': 5,
        'enclosure_drives': '3TB',
        'environment': 39,
        'created': '2017-10-11T18:25:46.000+0300'
    },

    1755: {
        'id': 1755,
        'name': 'ibox1755',
        'assignee': 'bobom',
        'ticket_ivt': "MAN-3839",
        'ticket_shipment': "MAN-8721",
        'model': 'F4200',
        'customer': 'Amdocs India',
        'enclosure_drives': '3TB',
        'labels': ['BLACK_IVT', 'RPQ3', 'RPQ4'],
        'ivt_cycle': 5,
        'environment': 14,
        'created': '2017-09-01T08:55:46.000+0300'
    },

    1803: {
        'id': 1803,
        'name': 'ibox1803',
        'assignee': 'debbyz',
        'ticket_ivt': "IVTS-1276",
        'ticket_shipment': "IVTS-1578",
        'model': 'F2400',
        'customer': "SAP",
        'enclosure_drives': '3TB',
        'ivt_cycle': 5,
        'labels': ['BLACK_IVT', 'RPQ5'],
        'environment': 8,
        'created': '2017-08-31T11:55:46.000+0300'
    },

}
# ====================================


class Assignee:
    def __init__(self):
        self.key = None
# ====================================


class Fields:
    pass
# ===================================


class Customized12904:
    def __init(self):
        self.value = None
# ===================================


class Customized12725:
    def __init__(self):
        self.value = None
# ===================================


class IssueIVT:
    def __init__(self, sn):
        self.fields = Fields()
        self.fields.assignee = Assignee()
        i = issues[sn]
        self.fields.assignee.key = i['assignee']
        self.fields.labels = i['labels']
        self.fields.environment = i['environment']
        self.fields.created = i['created']
        self.ticket = i['ticket_ivt']

# ===================================


class IssueShipment:
    def __init__(self, sn):
        self.fields = Fields()
        self.fields.customfield_12904 = Customized12904()
        self.fields.customfield_12725 = Customized12725()

        i = issues[sn]
        self.fields.created = i['created']
        self.fields.customfield_12904.value = i['model']
        self.fields.customfield_12725.value = i['customer']
        self.ticket = i['ticket_shipment']
# ===================================


class Jirahelper:
    def __init__(self):
        pass
    # ____________________________

    def get_manufacturing_ticket(self, sn, issue_type):
        klass = getattr(sys.modules[__name__], 'Issue%s' % issue_type)
        logger.debug("Found klass: %r", klass)
        try:
            issue = klass(sn)
        except KeyError:
            logger.exception("!ERROR")
            return None, None

        ticket = issue.ticket
        return ticket, issue
    # ____________________________
