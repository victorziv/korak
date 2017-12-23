import json
import hashlib
from config import logger
from models import Testcase

testcase_registry = []
# _________________________


def calculate_case_checksum(case):
    return hashlib.md5(json.dumps(case, sort_keys=True).encode('utf-8')).hexdigest()

# _________________________


def add_to_cache(case):
    case['checksum'] = calculate_case_checksum(case)
    logger.debug("Calculated checksum: %s", case['checksum'])
    saved_checksum = Testcase.get_checksum(case['name'])
    logger.debug("Found checksum: %s", saved_checksum)

    if saved_checksum is None:
        logger.debug("Add new TESTCASE to DB: {}".format(case))
        Testcase.add(case)
        return

    if saved_checksum != case['checksum']:
        logger.debug("Update changed TESTCASE to DB: {}".format(case))
        Testcase(case['name']).update(case)
# ___________________________


def parse_attributes(description):
    attrs = {}
    if description is None:
        return attrs

    for line in description.split('\n'):
        l = line.strip()
        if not l:
            continue

        if 'Attributes' in line:
            continue

        parts = l.split(':', 1)
        if len(parts) != 2:
            continue

        attrs[parts[0].strip()] = parts[1].strip()

    return attrs
# __________________________


def testcase(active=True):
    def decorate(func):
        case = {
            'name': func.__name__,
            'description': func.__doc__
        }

        case_attributes = parse_attributes(case['description'])
        case.update(case_attributes)

        logger.info('Register testcase {} (active={})'.format(case['name'], active))
        if active:
            add_to_cache(case)
            case['func'] = func
            testcase_registry.append(case)
        else:
            Testcase.remove(case)
            testcase_registry.remove(case)
        return func
    return decorate
# _________________________
