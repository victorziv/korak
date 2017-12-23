from werkzeug.utils import HTMLBuilder
from werkzeug.urls import Href
from config import logger
# ____________________________________


def compose_task_report(task):

    html = HTMLBuilder('html')
    href = Href('http://localhost:5000')

    task['log'] = html.a('LOG', href=href(task['log']))
    return task
# ____________________________________


def evaluate_page_data(total_records, current_page, rows_limit):
    logger.debug("Current page: %s", current_page)
    logger.debug("Rows limit: %s", rows_limit)

    if total_records:
        # round up total pages number
        if (total_records % rows_limit):
            total_pages = int(total_records / rows_limit + 1)
        else:
            total_pages = int(total_records / rows_limit)
    else:
        total_pages = 0

    logger.debug("Total pages: %s", total_pages)

    # if for some reason the current page is greater than total_pages - let it be total_pages
    if current_page > total_pages:
        current_page = total_pages

    # calculating the starting position
    offset = (rows_limit * current_page) - rows_limit

    # if for some reason ( the user set the page number being 0 for one) the start is negative
    # set it to zero
    if offset < 0:
        offset = 0

    logger.debug('Calculated offset: %r', offset)
    return total_pages, offset
# ____________________________________
