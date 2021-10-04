import sys
import MySQLdb
import config
from services import isfloat
from services import isint
from io import StringIO

# Handling function about SQL dumps
def extract_transform_load_sql_dump(swift_result, swift_container, swift_id, process_type):

    # Start of treatment 
    s=str(swift_result,'utf-8').replace("\\n", "\n")
    lines = StringIO()
    lines.write(s)
    lines.seek(0)
    data = []
    for line in lines:
        line = line.replace("\n","")
        data.append(line)
    
    # Return insert values
    new_data = []
    insert_data = []
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
                insert_data.append(new_data)
                new_data = []
    
    # Connect
    db = MySQLdb.connect(
        host=config.mariadb_host,
        user=config.mariadb_user,
        passwd=config.mariadb_passwd,
        db=config.mariadb_database,
        port=3306,
    )

    cursor = db.cursor()
    #Treatment to put in the format of execution mariadb
    for insert in insert_data:
        values = []
        for i in insert[1:]:
            i = i.replace("(", "")
            i = i.replace("),", "")
            i = i.replace(");", "")
            i = i.replace("'", "")
            
            res = tuple(i.split(', '))
            
            res = list(res)
            
            for n, r in enumerate(res): 
                
                r = r.replace(",",".")
                #Check if the string is an int or a float
                if isint(r):
                    res[n] = int(r)
                else:
                    if isfloat(r):
                        res[n] = float(r)
                    
                
            res = tuple(res)
            values.append(res)
        
        insert_into = insert[0]
        #Configuration of the insert into 
        for x in range(0, len(values[0])):
            if x == 0:
                insert_into = insert_into + ' (%s, '
            elif x > 0 and x < len(values[0])-1:
                insert_into = insert_into + '%s, '
            else:
                insert_into = insert_into + '%s)'


        # Execute SQL select statement
        cursor.executemany(insert_into, values)
        db.commit()

    # Close the connection
    db.close()
    
    return [{'result': 'Insert done'}]

sys.modules[__name__] = extract_transform_load_sql_dump