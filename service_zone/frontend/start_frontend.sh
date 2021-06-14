#!/bin/bash
PATH_REACT_FOLDER=${pwd}
#sudo docker build -t react_gui .
#sudo docker run -p 3000:3000 -v ./src/:/app/src -it react_gui
sudo docker-compose up --build