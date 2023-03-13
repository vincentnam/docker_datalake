import api from "../../api/api";

export const users = (token) => {
    return api.post('users', {
        token: localStorage.getItem('token')
    })
        .then((response) => {
            return {
                users: response.data.users
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}


export const userRolesProjects = (user, token) => {
    return api.post('user_assignment', {
        token: localStorage.getItem('token'),
        user_id: user.id
    })
        .then((response) => {
            return {
                userAccess: response.data.assignment
            };
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const roles = (token) => {
    return api.post('all_roles', {
        token: token
    })
        .then((response) => {
            let list_roles = []
            response.data.roles.forEach((element) => {
                list_roles.push(
                    {
                        value: element.id,
                        label: element.name
                    }
                )
            });
            return {roles: list_roles};
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const projects = (token) => {
    return api.post('all_projects', {
        token: token
    })
        .then((response) => {
            let list_projects = []
            response.data.projects.forEach((element) => {
                if (element.name !== "admin") {
                    list_projects.push(
                        {
                            value: element.id,
                            label: element.name
                        }
                    )
                }
            });
            return {projects: list_projects};
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const addUser = (user, role, project, token) => {
    return api.post('role_assignments/add', {
        token: token,
        user: user.id,
        role: role.value,
        project: project.value
    })
        .then((response) => {
            return {result: true};
        })
        .catch(function (error) {
            console.log(error);
            return {result: false}
        });
}

export const deleteUser = (user, role, project, token) => {
    return api.post('role_assignments/delete', {
        token: token,
        user: user.id,
        role: role.id,
        project: project.id
    })
        .then((response) => {
            return {result: true};
        })
        .catch(function (error) {
            console.log(error);
            return {result: false}
        });
}

export const purgeUsers = (user, role, project, token) => {
    return api.post('role_assignments/purge', {token: token})
        .then((response) => {
            return {result: true};
        })
        .catch(function (error) {
            console.log(error);
            return {result: false}
        });
}
