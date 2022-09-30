import pyodbc

SQLSERVER_URL = "Neocampus-datalake-sql.dev.modiscloud.net"
SQLSERVER_DB = "IndexCPT"
SQLSERVER_LOGIN = "sa"
SQLSERVER_PWD = "!ModisSGE"

server = globals()["SQLSERVER_URL"]
database = globals()["SQLSERVER_DB"]
username = globals()["SQLSERVER_LOGIN"]
password = globals()["SQLSERVER_PWD"]

#Connection String
connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = connection.cursor()

#Sample select query
#cursor.execute("SELECT @@version;")

cursor.execute("SELECT TOP (10) [Chrono] \
, SUBSTRING(Name, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)+2, CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) \
, SUBSTRING(Name, 1, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) \
, Value \
, TS \
  FROM [IndexCPT].[dbo].[Table_Index] \
  WHERE len(Name) - len(replace(Name,'.','')) >=2;");

row = cursor.fetchone()

while row:
    print(row[0], row[1], row[2], row[3])
    row = cursor.fetchone()

