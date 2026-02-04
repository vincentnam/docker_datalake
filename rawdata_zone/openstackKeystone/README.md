script.sh : build + docker compose

#TODO : finish config (connection Horizon to keystone test + Swift connection)
#TODO : Refactor folders (keystone = python wsgi.py lib ; horizon = apache2 conf ; etc/apache2 = keystone apache 2 conf ; etc/horizon = horizon python conf -> unmaintanable, not logic, need refactor)