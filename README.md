#TODO: Add endpoint creation in keystone bootstrap for each management node created in the architecture 
#TODO: Use variable to configure conf file in keystone
#TODO: Add Keystone federation to a keycloak Identity provider
# Security TODO list:

Potential security breach : 
    
    - Swift container in privileged mode 
        - #TODO give defined list of privilege instead of full privileged mode  
    - Remove hardcoded secret


curl -H "Authorization: Bearer gAAAAABpoat_E62omkMt_iIW3O7etR8a8CUPTt7r33sefp_wNLRsgBW4h8jORAzwGhwnLO-pNXd45BKvMJ5vpEJ64qeJBQxDjJF7hB27QdYzM7jvMoWN-oHAn58WelrveFEqoB8zjs5BEimX3If-QofMGAMleM8RktpFB3E-LZRSKX79O-eDauA" http://localhost:3001/buckets
curl -X GET -H "X-Username: admin" -H "X-Password: admin"      -H "Content-Type: application/json"      http://localhost:3001/buckets



# Bug : 
If loop0 is already used, Object storage will raise error "no space left"
Solution : 

    losetup -d /dev/loop0

#TODO : Fix the loop device creation only using loop0, should be using the device created, not only the loop0
    
