import React from "react";
import {NavLink, useHistory} from 'react-router-dom';
import api from '../api/api';
import {config} from "../configmeta/projects";
import {connect} from "react-redux";
import {editListProjectAccess, editNameContainer} from "../store/nameContainerAction";
import {editAuthProjects, editAuthRoles, editAuthToken, editAuthLoginAdmin} from "../store/authAction";
import '../navbar.css';

class UpBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            anomalies: [],
            container: this.props.nameContainer.nameContainer,
            listProjectAccess: []
        };
        this.logout = this.logout.bind(this);
        this.loadRolesProjectsUser = this.loadRolesProjectsUser.bind(this);
    }

    componentDidMount() {
        if (localStorage.getItem('isLogin')) {
            this.setState({
                listProjectAccess: this.props.nameContainer.listProjectsAccess,
                container: this.props.nameContainer.nameContainer,
            })
            this.countData(this.state.container);
            this.loadRolesProjectsUser();
            console.log(this.props.nameContainer.nameContainer);
        }
    }

    loadRolesProjectsUser() {
        api.post('auth-token', {
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.props.editAuthRoles(response.data.roles);
                this.props.editAuthProjects(response.data.projects);
                response.data.roles.forEach((role) => {
                    if (role.name === "admin") {
                        this.props.editAuthLoginAdmin(true);
                    }
                })
                let listProjectAccess = [];
                response.data.projects.forEach((project) =>{
                    if (project.name !== "datalake"){
                        listProjectAccess.push({
                            label: project.name,
                            name_container: project.name,
                        })
                    }
                });
                this.props.editNameContainer(listProjectAccess[0].name_container);
                this.props.editListProjectAccess(listProjectAccess);
                console.log(this.props.nameContainer.nameContainer);
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    logout() {
        this.props.editAuthRoles([]);
        this.props.editAuthProjects([]);
        this.props.editAuthToken("");
        this.props.editAuthLoginAdmin(false);
        localStorage.removeItem('token');
        localStorage.removeItem('isLogin');
        this.props.history.push('/');
        window.location.reload();
    }

    countData(container_name) {
        api.post('getDataAnomalyAll', {
            container_name: container_name,
            token: localStorage.getItem('token')
        })
            .then((response) => {
                this.setState({
                    anomalies: response.data.anomaly
                })
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    render() {
        const SelectProjects = () => {
            // let projects = [config.projects];
            const listProjects = this.props.nameContainer.listProjectsAccess.map((p, key) => (
                    <option key={key} value={p.name_container}>{p.label}</option>
            ));

            return (
                <div className="form-group mr">
                    <select value={this.props.nameContainer.nameContainer}
                            onChange={(event) => {
                                this.props.editNameContainer(event.target.value);
                                this.countData(event.target.value);
                            }}
                            name="project" className="form-select select-project mr">
                        {listProjects}
                    </select>
                </div>
            );
        }
        return (
            <div className="upbar d-flex justify-content-end align-items-center">
                {localStorage.getItem('isLogin') &&
                    <>
                        <SelectProjects/>
                        <div className="navbar-nav-up">
                            <NavLink activeClassName="active"
                                     className="nav-item nav-link"
                                     to="/detection-anomalies"
                                     data-toggle="tooltip" data-placement="bottom" title={this.state.anomalies.length + " Anomalies"}
                            >
                                <div className="Logo_alertes">
                                    <svg className="Path_76" viewBox="208.773 147 26.744 26.574">
                                        <path id="Path_76"
                                              d="M 233.7629089355469 173.5743103027344 L 210.5958862304688 173.5743103027344 C 209.9825592041016 173.5743103027344 209.3692016601562 173.2336120605469 209.0285034179688 172.6883239746094 C 208.6878051757812 172.1430969238281 208.6878051757812 171.461669921875 209.0285034179688 170.9168701171875 C 209.3692016601562 170.3035278320312 209.7779693603516 169.7586975097656 210.1186218261719 169.1453552246094 C 211.1407012939453 167.5779724121094 212.2308197021484 165.9430541992188 212.2308197021484 164.5117492675781 L 212.2311859130859 156.1990966796875 C 212.2992553710938 151.15673828125 216.45556640625 147.0003967285156 221.4979095458984 147.0003967285156 L 223.1333160400391 147.0003967285156 C 228.0390930175781 147.0003967285156 232.0593566894531 151.0206604003906 232.0593566894531 155.9264221191406 L 232.0593566894531 164.4437255859375 C 232.0593566894531 165.9425659179688 233.1494750976562 167.5099487304688 234.1715393066406 169.0773315429688 C 234.5802917480469 169.62255859375 234.9209899902344 170.2354736328125 235.2616577148438 170.8488159179688 C 235.6023406982422 171.3941040039062 235.6023406982422 172.0755004882812 235.2616577148438 172.6203308105469 C 234.9894104003906 173.233642578125 234.3760833740234 173.5743408203125 233.7628021240234 173.5743408203125 Z M 221.4980163574219 148.3631286621094 C 217.2050933837891 148.3631286621094 213.662109375 151.9061279296875 213.662109375 156.1990356445312 L 213.662109375 164.51171875 C 213.662109375 166.4197998046875 212.5039367675781 168.1912841796875 211.3453063964844 169.8947448730469 C 210.9365539550781 170.508056640625 210.5958709716797 171.0529174804688 210.2551879882812 171.5982055664062 C 210.1190795898438 171.8027648925781 210.1871337890625 171.9388732910156 210.2551879882812 172.0069580078125 C 210.3232574462891 172.0750122070312 210.3913116455078 172.2115173339844 210.5958862304688 172.2115173339844 L 233.7629089355469 172.2115173339844 C 233.9674835205078 172.2115173339844 234.1036071777344 172.0754089355469 234.1036071777344 172.0069580078125 C 234.1716766357422 171.9388732910156 234.2397155761719 171.8023986816406 234.1036071777344 171.5982055664062 C 233.7629089355469 171.0529479980469 233.4222259521484 170.5080871582031 233.0134735107422 169.8947448730469 C 231.8553161621094 168.1912841796875 230.6966857910156 166.3517150878906 230.6966857910156 164.51171875 L 230.6966857910156 155.9263610839844 C 230.6966857910156 151.7700500488281 227.2897644042969 148.3631286621094 223.1334228515625 148.3631286621094 L 221.4980163574219 148.3631286621094 Z">
                                        </path>
                                    </svg>
                                    <svg className="Path_77" viewBox="329 434 3.407 3.407">
                                        <path id="Path_77"
                                              d="M 330.7034606933594 437.4068908691406 C 329.7494506835938 437.4068908691406 329 436.6574401855469 329 435.7034606933594 C 329 434.7494506835938 329.7494506835938 434 330.7034606933594 434 C 331.6575012207031 434 332.4069519042969 434.7494506835938 332.4069519042969 435.7034606933594 C 332.4069519042969 436.6574401855469 331.6575012207031 437.4068908691406 330.7034606933594 437.4068908691406 Z M 330.7034606933594 435.3627624511719 C 330.4989013671875 435.3627624511719 330.36279296875 435.4989013671875 330.36279296875 435.7034606933594 C 330.36279296875 435.9080200195312 330.4989013671875 436.0441284179688 330.7034606933594 436.0441284179688 C 330.9080505371094 436.0441284179688 331.0441589355469 435.9080200195312 331.0441589355469 435.7034606933594 C 331.0441589355469 435.4989013671875 330.9080505371094 435.3627624511719 330.7034606933594 435.3627624511719 Z">
                                        </path>
                                    </svg>
                                    <svg className="Path_78" viewBox="343 133 1.363 2.044">
                                        <path id="Path_78"
                                              d="M 343 133 L 344.3627624511719 133 L 344.3627624511719 135.0441436767578 L 343 135.0441436767578 L 343 133 Z">
                                        </path>
                                    </svg>
                                </div>
                                {this.state.anomalies.length > 0 &&
                                    <span
                                        className="position-absolute translate-small top-0 badge badge-secondary rounded-pill bg-danger"
                                        style={{marginTop: '5px', marginLeft: '15px'}}>
                            {this.state.anomalies.length}
                        </span>
                                }
                            </NavLink>
                        </div>

                        <div className="navbar-nav-up">
                            <div className="nav-item dropdown">
                                {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                                <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                                   data-bs-toggle="dropdown" aria-expanded="false">
                                    <div id="User">
                                        <svg className="Path_278" viewBox="169.795 350.791 21.693 8.911">
                                            <path id="Path_278"
                                                  d="M 190.9748992919922 359.702392578125 C 190.7484893798828 359.702392578125 190.5429840087891 359.5549926757812 190.479736328125 359.3231811523438 C 190.0163269042969 357.6220703125 189.1052093505859 356.0578002929688 187.8515777587891 354.7990112304688 C 185.9241333007812 352.8715209960938 183.3643646240234 351.8076171875 180.6414489746094 351.8076171875 C 176.0488739013672 351.8076171875 172.0041656494141 354.899169921875 170.7979583740234 359.3175048828125 C 170.72412109375 359.5914306640625 170.4450378417969 359.7494506835938 170.1711273193359 359.6756591796875 C 169.8972320556641 359.601806640625 169.7392272949219 359.32275390625 169.8130645751953 359.048828125 C 171.1405181884766 354.1934204101562 175.5907897949219 350.7913208007812 180.641845703125 350.7913208007812 C 183.6386413574219 350.7913208007812 186.4563293457031 351.9605712890625 188.5730743408203 354.0778198242188 C 189.9581756591797 355.457763671875 190.9588317871094 357.1799926757812 191.4696960449219 359.0548706054688 C 191.5435943603516 359.3287353515625 191.3855285644531 359.6077880859375 191.1116485595703 359.681640625 C 191.0643768310547 359.6972045898438 191.0220489501953 359.702392578125 190.9748077392578 359.702392578125 Z">
                                            </path>
                                        </svg>
                                        <svg className="Path_279" viewBox="249.2 107.98 12.134 12.908">
                                            <path id="Path_279"
                                                  d="M 255.2671508789062 120.8883666992188 C 251.9228973388672 120.8883666992188 249.2000427246094 117.9917221069336 249.2000427246094 114.4317855834961 C 249.2000427246094 110.8714141845703 251.9228973388672 107.9800186157227 255.2671508789062 107.9800186157227 C 258.6114501953125 107.9800186157227 261.3343200683594 110.8766555786133 261.3343200683594 114.4365844726562 C 261.3343200683594 117.9965438842773 258.6114501953125 120.8883666992188 255.2671508789062 120.8883666992188 Z M 255.2671508789062 109.0014266967773 C 252.4810180664062 109.0014266967773 250.2164001464844 111.4398574829102 250.2164001464844 114.436653137207 C 250.2164001464844 117.4334564208984 252.4810180664062 119.8718719482422 255.2671508789062 119.8718719482422 C 258.0533142089844 119.8718719482422 260.3179931640625 117.4334564208984 260.3179931640625 114.436653137207 C 260.3179931640625 111.4398574829102 258.0533142089844 109.0014266967773 255.2671508789062 109.0014266967773 Z">
                                            </path>
                                        </svg>
                                        <svg className="Path_280" viewBox="70 0 33.706 33.706">
                                            <path id="Path_280"
                                                  d="M 86.85321044921875 33.70641326904297 C 77.56287384033203 33.70641326904297 70 26.14353561401367 70 16.85320663452148 C 70 7.562875270843506 77.56287384033203 0 86.85321044921875 0 C 96.14352416992188 0 103.7064056396484 7.56287670135498 103.7064056396484 16.85320663452148 C 103.7064056396484 26.14353561401367 96.14352416992188 33.70641326904297 86.85321044921875 33.70641326904297 Z M 86.85321044921875 1.022025346755981 C 78.12144470214844 1.022025346755981 71.02203369140625 8.121438026428223 71.02203369140625 16.85320281982422 C 71.02203369140625 25.58496856689453 78.12684631347656 32.68437957763672 86.85321044921875 32.68437957763672 C 95.5849609375 32.68437957763672 102.6843872070312 25.57954978942871 102.6843872070312 16.85320281982422 C 102.6843872070312 8.121437072753906 95.5849609375 1.022025346755981 86.85321044921875 1.022025346755981 Z">
                                            </path>
                                        </svg>
                                    </div>
                                </a>
                                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                    {this.props.auth.isLoginAdmin === true &&
                                        <li>
                                            <NavLink activeClassName="active"
                                                     className="nav-item nav-link text-end"
                                                     to="/config-users">
                                                Users
                                            </NavLink>
                                        </li>
                                    }
                                    <a className="text-end" style={{textDecoration: "none"}}
                                       onClick={this.logout}>Déconnexion</a>
                                </ul>
                            </div>
                        </div>
                    </>
                }


            </div>
        );


    }
}

const mapStateToProps = (state) => {
    return {
        nameContainer: state.nameContainer,
        auth: state.auth
    }
}

function WithNavigate(props) {
    let history = useHistory();
    return <UpBar {...props} history={history}/>
}

export default connect(mapStateToProps, {
    editNameContainer,
    editAuthRoles,
    editAuthToken,
    editAuthProjects,
    editAuthLoginAdmin,
    editListProjectAccess
})(WithNavigate)