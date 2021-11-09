import sys
import MySQLdb
import config
from services import isfloat
from services import isint
from io import StringIO

# Handling function about SQL dumps
def insert_sge_data(swift_result, swift_container, swift_id, process_type):

    # TODO : Insert data to SQL Server

    return True

sys.modules[__name__] = insert_sge_data