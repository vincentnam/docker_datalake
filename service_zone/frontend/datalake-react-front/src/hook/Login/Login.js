import api from "../../api/api";

export const login = (user,password, props) => {
    return api.post('login', {
        user: user,
        password: password,
    })
        .then((response) => {
            let listProjectAccess = [];
            response.data.projects.forEach((project) =>{
                if (project.name !== "datalake" && project.name !== "admin"){
                    listProjectAccess.push({
                        label: project.name,
                        name_container: project.name,
                    })
                }
            });
            props.editAuthRoles(response.data.roles);
            props.editAuthProjects(response.data.projects);
            props.editAuthToken(response.data.token);
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('isLogin', true);

            props.editListProjectAccess(listProjectAccess);
            let isAdmin = false;
            response.data.roles.forEach((role) => {
                if (role.name === "admin") {
                    isAdmin = true;
                }
            });
            if (isAdmin === true) {
                props.editAuthLoginAdmin(true);
            } else {
                props.editAuthLoginAdmin(false);
            }
            if(listProjectAccess.length === 0){
                localStorage.setItem('isNoProject', true);
                props.history.push('/info');
            } else {
                localStorage.setItem('isNoProject', false);
                props.editNameContainer(listProjectAccess[0].name_container);
                props.history.push('/home');
                return {
                    result: true
                }
            }
        })
        .catch(function (error) {
            return {
                result: false
            }
        })
}