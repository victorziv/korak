from jira import JIRA
from flask import current_app as cap
from config import logger
# ===================================


class Jirahelper:
    # ____________________________

    def __init__(self):
        pass
    # ____________________________

    def connect_to_jira(self):
        return JIRA(cap.config['JIRA_OPTIONS'], basic_auth=(cap.config['JIRA_USER'], cap.config['JIRA_PASS']))
    # ____________________________

    def get_manufacturing_ticket(self, sn, issue_type):
        conn = self.connect_to_jira()
        query = 'project = MAN AND issuetype = "%s" AND "Box Serial" = %s AND status in ( IVT, "HW Config", "On Hold")' % (  # noqa
                issue_type, sn)
        try:
            ticket = conn.search_issues(query)[0].key
            logger.info("Ticket found: %r", ticket)
        except IndexError:
            logger.error("Ticket for machine S/N %s was not found in Jira", sn)
            return None, None

        issue = conn.issue(ticket)
        logger.info("Issue found: %r", issue)
        return ticket, issue
    # ____________________________
