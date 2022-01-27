import { useDispatch, useSelector } from 'react-redux';
import {config} from "../../configmeta/projects";

export function SelectProjects() {
    const dispatch = useDispatch();
    let projects = [config.projects];
    const listProjects = projects.map((project) => (
        project.map((p, key) =>
            <option value={p.name_container}>{p.label}</option>
        )
    ));

    function changeProject(event) {
        dispatch({ type: "changeNameContainer", payload: {nameContainer: event.target.value} })
    }
    return (
        <>
            <select value={useSelector((state) => state.nameContainer)} onChange={event => changeProject(event)} name="project" className="form-select" >
                {listProjects}
            </select>
        </>

    );
}