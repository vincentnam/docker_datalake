#TODO: Add endpoint creation in keystone bootstrap for each management node created in the architecture 
#TODO: Use variable to configure conf file in keystone
#TODO: Add Keystone federation to a keycloak Identity provider

#TODO: Test list bucket with token provided in request
# Security TODO list:

Potential security breach : 
    
    - Swift container in privileged mode 
        - #TODO give defined list of privilege instead of full privileged mode  

## TODO (deferred): Centralize Keystone token management in Flask

### Current situation

The web GUI stores the Keystone token in `localStorage` and local credentials in
`sessionStorage`. Flask is already the only public gateway, so this improvement is
useful but not currently a priority. It allows to open Keystone service (in order to make authentication federation 
process from external to internal datalake Keystone) without risking to expose the Keystone token through web GUI.

### Target architecture

Flask would become the single authentication and session authority for all data lake
clients:
- Store Keystone tokens in Valkey and expose only an `HttpOnly` session cookie
- Use the same server-side session for local login and federated SSO
- Remove Keystone tokens and passwords from browser storage and API responses
- Load authentication from the Flask session for all API requests
- Revoke the Keystone token and delete the session on logout
- JupyterHub authenticate through short-lived tickets issued by Flask


# Other
curl -H "Authorization: Bearer gAAAAABpoat_E62omkMt_iIW3O7etR8a8CUPTt7r33sefp_wNLRsgBW4h8jORAzwGhwnLO-pNXd45BKvMJ5vpEJ64qeJBQxDjJF7hB27QdYzM7jvMoWN-oHAn58WelrveFEqoB8zjs5BEimX3If-QofMGAMleM8RktpFB3E-LZRSKX79O-eDauA" http://localhost:3001/buckets
curl -X GET -H "X-Username: admin" -H "X-Password: admin"      -H "Content-Type: application/json"      http://localhost:3001/buckets



# Bug : 
If loop0 is already used, Object storage will raise error "no space left"
Solution : 

    losetup -d /dev/loop0

#TODO : Fix the loop device creation only using loop0, should be using the device created, not only the loop0


#Test purpose
export OS_USERNAME=admin
export OS_PASSWORD=admin
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2

## Licence



Copyright (C) 2020-2026 Vincent-Nam DANG  
Copyright (C) 2021-2026 docker_datalake contributors



The software license does not apply to data, notebooks, business scripts, queries, models, results, configurations, or other independent content merely because they are used by, provided to, or created with the project.
These items remain subject to the rights and licenses chosen by their respective owners.

Third-party components used or executed by the project, particularly in the form of separate containers, remain governed by their respective licenses.
