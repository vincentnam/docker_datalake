export $(cat /.env | xargs)
mongosh --eval "db.createUser( { user: '$MONGO_ADMIN',pwd: '$MONGO_PWD',roles: [ 'root' ]} )" "mongodb://localhost:27017/admin"
mongosh --eval "use admin" --eval "db.auth('$MONGO_ADMIN','$MONGO_PWD')" --eval "use stats" --eval "db.traceability_big_file.insertOne({'type':'object_id_big_file','object_id':1})"
mongosh --eval "use admin" --eval "db.auth('$MONGO_ADMIN','$MONGO_PWD')" --eval "use stats" --eval "db.swift.insertOne({'type':'object_id_file','object_id':1})"

#mongosh --eval "use admin" --eval "db.createUser({user:'$MONGO_ADMIN', pwd:'$MONGO_PWD',roles:[{role:'userAdminAnyDatabase',db:'$MONGO_DB_AUTH'}]});"
