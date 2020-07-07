
cd $HOME; git clone https://github.com/openstack/python-swiftclient.git &&
cd $HOME/python-swiftclient; sudo pip install -r requirements.txt; sudo python setup.py develop; cd - && git clone https://github.com/openstack/swift.git && cd $HOME/swift; sudo pip install --no-binary cryptography -r requirements.txt; sudo python setup.py develop; cd - && cd $HOME/swift; sudo pip install -r test-requirements.txt && exit
