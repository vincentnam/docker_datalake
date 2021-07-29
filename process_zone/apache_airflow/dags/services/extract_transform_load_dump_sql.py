import MySQLdb
import config

# Handling function about SQL dumps
def extract_transform_load_sql_dump(swift_result, swift_container, swift_id, process_type):

    # Connect
    db = MySQLdb.connect(
        host=config.mariadb_host,
        user=config.mariadb_user,
        passwd=config.mariadb_passwd,
        db=config.mariadb_database
    )

    cursor = db.cursor()

    # Execute SQL select statement
    cursor.execute(swift_result)

    # Close the connection
    db.close()

sys.modules[__name__] = extract_transform_load_sql_dump