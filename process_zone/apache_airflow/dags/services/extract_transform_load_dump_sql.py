import sys
import MySQLdb
import config
from io import StringIO

# Handling function about SQL dumps
def extract_transform_load_sql_dump(swift_result, swift_container, swift_id, process_type):

    s=str(swift_result,'utf-8').replace("\\n", "\n")
    lines = StringIO()
    lines.write(s)
    lines.seek(0)
    data = []
    for line in lines:
        line = line.replace("\n","")
        data.append(line)
    
    new_data = []
    idInsert = 0
    for d in data:
        if("INSERT" in d):
            idInsert += 1
            
        if(";" in d and idInsert > 0):
            idInsert += 1
        
        if (idInsert != 0 and idInsert < 3):
            new_data.append(d)
            if(idInsert == 2):
                idInsert = 0
    
    processing_data = "\n".join(new_data)
    
    print(processing_data)
    
    # Connect
    db = MySQLdb.connect(
        host=config.mariadb_host,
        user=config.mariadb_user,
        passwd=config.mariadb_passwd,
        db=config.mariadb_database
    )

    cursor = db.cursor()

    # Execute SQL select statement
    cursor.execute(processing_data)

    # Close the connection
    db.close()

sys.modules[__name__] = extract_transform_load_sql_dump