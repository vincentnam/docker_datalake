import React from "react";
import { Header } from "./Header";
import '../home.css';
import { config } from '../configmeta/config';
import { config_processed_data } from '../configmeta/config_processed_data';

export class Home extends React.Component {

    constructor(props) {
        super(props);
        this.props = props
        this.validateFilters = this.validateFilters.bind(this);

        this.setFiletype = this.setFiletype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.handleChange = this.handleChange.bind(this);

        this.state = {
            type: 0
        }
    }

    validateFilters(event) {
        event.preventDefault()
        this.props.validateFilters()

        /*this.props.setFiletype(this.props.data.filetype)   
        this.props.setBeginDate(this.props.data.beginDate)   
        this.props.setEndDate(this.props.data.endDate)*/
    }

    setFiletype(event) {
        let filetype = event.target.value;
        this.props.setFiletype(filetype)      
    }
        
    setBeginDate(event) {
        let beginDate = event.target.value;
        this.props.setBeginDate(beginDate)
    }

    setEndDate(event) {
        let endDate = event.target.value;
        this.props.setEndDate(endDate)
    }

    // retrieve filetype by id in conf file
    getFiletypeById(datatypeConf, id) {
        let filetypesResult = ""

        datatypeConf.map((type) => (
            // loop in config file
            type.map((t) => {
                // if selected data type corresponds with current data type
                if (t.id === parseInt(id)) {
                    filetypesResult = t.type_file_accepted
                }
            })
        ));

        return filetypesResult
    }

    // when data type has changed
    handleChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        let filetypesResult = this.getFiletypeById( [config.types], value)
        this.setFiletype(filetypesResult) 

        this.setState({
            [name]: value
        });
    }

    setFiletype(value) {
        let filetype = value;
        return this.setState({ filetype: filetype })
    }

    setBeginDate(value) {
        let beginDate = value;
        return this.setState({ beginDate: beginDate })
    }

    setEndDate(value) {
        let endDate = value;
        return this.setState({ endDate: endDate })
    }

    validateFilters() {
        this.setState({
            offset: 0
        }, () => {
            this.loadObjectsFromServer();
        })
    }


    render() {
         // data type field
         const SelectDatatype = () => {
            let types = [config.types];
            if(this.props.title == "Affichage des données traitées"){
                types = [config_processed_data.types];
            }
            // loop into conf to get all data types
            const listTypes = types.map((type) => (
                type.map((t) => 
                    <option key={t.id} value={t.id}>{t.label}</option>
                )
            ));
            return (
                <select value={this.state.type} onChange={this.handleChange} name="type" className="form-control">
                    {listTypes}
                </select>
            );
        }

        return (
            <div>
                <div class="entire_page">
                    <Header style="margin-bottom: 20%;" />


                </div>
                <div class="table_homepage_zone">
                    <div class="v58_46" />
                    <div class="download_button_zone">
                        <span class="download_button">Télécharger</span>
                    </div>

                    <div class="v58_65">
                        <div class="v58_68">
                            <div class="v58_69" />
                        </div>
                        <div class="v58_70">
                            <div class="v58_71" />
                        </div>
                        <div class="v58_72">
                            <div class="v58_73" />
                        </div>
                        <div class="v58_74">
                            <div class="v58_75" />
                        </div>
                        <div class="v58_77">
                            <div class="v58_78" />
                        </div>
                        <div class="v58_80">
                            <div class="v58_81" />
                        </div>
                        <div class="v58_83">
                            <div class="v58_84" />
                        </div>
                        <div class="v58_86">
                            <div class="v58_87" />
                        </div>
                        <div class="v58_89">
                            <div class="v58_90" />
                        </div>
                        <div class="v58_92">
                            <div class="v58_93" />
                        </div>
                    </div>
                    <div class="v58_153">
                        <div class="v58_154" />
                        <div class="v58_155" />
                        <div class="v58_156" />
                        <div class="v58_157" />
                        <div class="v58_158" />
                        <div class="v58_159" />
                        <div class="v58_160" />
                        <div class="v58_161" />
                        <div class="v58_162" />
                        <div class="v58_163" />
                        <div class="v58_164" />
                    </div>
                    <div class="v64_46">
                        <div class="v58_194" />
                        <div class="v58_195" />
                        <div class="v58_196" />
                        <div class="v58_328" />
                        <div class="v58_201" />
                        <div class="v64_40" />
                        <div class="v64_41" />
                        <div class="v64_42" />
                        <div class="v64_43" />
                        <div class="v64_45" />
                        <div class="v64_44" />
                    </div>

                    <div class="object_id_swift_column">
                        <span class="object_id_swift_title">Id objet Swift</span>
                        <div class="v58_210">
                            <div class="v58_211">
                                <div class="v58_212" />
                            </div>
                            <div class="v58_213">
                                <div class="v58_214" />
                            </div>
                        </div>
                    </div>
                    <span class="swift_container_title">Container Swift</span>
                    <div class="filetype_column">
                        <span class="filetype_title">Type de fichier</span>
                        <div class="v58_318">
                            <div class="v58_319">
                                <div class="v58_320" />
                            </div>
                            <div class="v58_321">
                                <div class="v58_322" />
                            </div>
                        </div>
                    </div>
                    <span class="swift_user_title">Utilisateur Swift</span>
                    <div class="v58_323">
                        <div class="v58_324">
                            <div class="v58_325" />
                        </div>
                        <div class="v58_326">
                            <div class="v58_327" />
                        </div>
                    </div>
                    <span class="object_name_title">Nom de l’objet</span>
                    <div class="v58_267">
                        <div class="v58_268">
                            <div class="v58_269" />
                        </div>
                        <div class="v58_270">
                            <div class="v58_271" />
                        </div>
                    </div>
                    <span class="v58_284">Meta 1</span>
                    <span class="v58_292">Meta 2</span>
                    <div class="creation_date_column">
                        <span class="v58_300">Date de création</span>
                        <div class="v58_301">
                            <div class="v58_302">
                                <div class="v58_303" />
                            </div>
                            <div class="v58_304">
                                <div class="v58_305" />
                            </div>
                        </div>
                    </div>

                    <span class="last_raw_data_uploaded_title">Dernières données brutes uploadées</span>
                </div>
                <span class="home_title">Home</span>

                <div class="filters_zone">
                    <div class="v64_7" />
                    <div class="v64_8">
                        <span class="v64_9">Type de fichier</span>
                        <span class="v64_10">
                            <SelectDatatype />
                        </span>
                        <div class="v64_11">
                            <div class="v64_12">
                                <div class="v64_13" />
                            </div>
                        </div>
                    </div>
                    <div class="v64_20">
                        <span class="v64_21">Date de début</span>
                        <span class="v64_22">jj/mm/aaaa</span>
                        <div class="v64_23">
                            <div class="v64_24" />
                            <div class="v64_25" />
                        </div>
                    </div>
                    <div class="v64_26">
                        <span class="v64_27">Date de fin</span>
                        <span class="v64_28">jj/mm/aaaa</span>
                        <div class="v64_29">
                            <div class="v64_30" />
                            <div class="v64_31" />
                        </div>
                    </div>
                    <div class="v64_32">
                        <div class="v64_33">
                            <div class="v64_34">
                                <div class="v64_35" />
                            </div>
                        </div>
                    </div>
                    <div class="name" />
                    <div class="name" />
                    <div class="name" />
                </div>
            </div>
        );
    }
}