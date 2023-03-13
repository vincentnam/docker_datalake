import api from "../../api/api";

export const loadInfoUser = (token) => {
    return api.post('auth-token/projects', {
        token: token
    })
        .then((response) => {
            let listProjectAccess = [];
            response.data.projects.forEach((project) => {
                if (project.name !== "datalake" && project.name !== "admin") {
                    listProjectAccess.push({
                        label: project.name,
                        name_container: project.name,
                    })
                }
            });
            return{
                container_name: listProjectAccess[0].name_container,
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}

export const loadAllInfoUser = (token, props) => {
    return api.post('auth-token', {
        token: token
    })
        .then((response) => {
            props.editAuthRoles(response.data.roles);
            props.editAuthProjects(response.data.projects);
            response.data.roles.forEach((role) => {
                if (role.name === "admin") {
                    props.editAuthLoginAdmin(true);
                }
            })
            let listProjectAccess = [];
            response.data.projects.forEach((project) => {
                if (project.name !== "datalake" && project.name !== "admin") {
                    listProjectAccess.push({
                        label: project.name,
                        name_container: project.name,
                    })
                }
            });
            props.editListProjectAccess(listProjectAccess);
            if (listProjectAccess.length === 0) {
                localStorage.setItem('isNoProject', true);
            } else {
                localStorage.setItem('isNoProject', false);
                props.editNameContainer(listProjectAccess[0].name_container);
                return {
                    listProjectAccess: listProjectAccess,
                    container: listProjectAccess[0].name_container,
                };
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}
