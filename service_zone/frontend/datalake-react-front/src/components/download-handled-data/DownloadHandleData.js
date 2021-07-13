import React from "react";
import { Filters } from "../download-raw-data/Filters";
import { Header } from "../Header";
import moment from "moment";
import $ from 'jquery';

export class DownloadHandleData extends React.Component {

    constructor(props) {
        super(props);

        this.setFiletype = this.setFiletype.bind(this);
        this.setDatatype = this.setDatatype.bind(this);
        this.setBeginDate = this.setBeginDate.bind(this);
        this.setEndDate = this.setEndDate.bind(this);
        this.validateFilters = this.validateFilters.bind(this)

        this.state = {
            filetype: '',
            dataType: '',
            beginDate: moment().format('Y-m-d'),
            endDate: moment().format('Y-m-d'),
        }
    }

    loadHandledDataFromServer() {
        this.handleShow()
        /*$.ajax({
          url: this.url + '/handled-data',
          data: JSON.stringify({ 
            limit: this.perPage, 
            offset: this.state.offset,
            datatype: this.state.dataType,
            beginDate: this.state.beginDate,
            endDate: this.state.endDate
          }),
          xhrFields: {
            withCredentials: true
         },
         crossDomain: true,
         contentType: 'application/json; charset=utf-8',
          dataType: 'json',
          type: 'POST',
    
          success: (data) => {
              if(data.result) {
                this.setState({
                    elements: data.result.objects,
                    pageCount: Math.ceil(data.result.length / this.perPage),
                  });
              }
          },
    
          error: (xhr, status, err) => {
            console.error(this.url, status, err.toString()); // eslint-disable-line
          },

          complete: () => {
            this.handleClose()
          }
        });*/
      }

    setFiletype(value) {
        let filetype = value;
        return this.setState({filetype: filetype})
    }

    setDatatype(value) {
        let dataType = value;
        return this.setState({dataType: dataType})
    }

    setBeginDate(value) {
        let beginDate = value;
        return this.setState({beginDate: beginDate})
    }

    setEndDate(value) {
        let endDate = value;
        return this.setState({endDate: endDate})
    }

    validateFilters() {
        this.setState({
            offset: 0
        }, () => {
            this.loadHandledDataFromServer();
        })
    }

    render() {

        let filterData = {
            'filetype': this.state.filetype,
            'beginDate': this.state.beginDate,
            'endDate': this.state.endDate
        }

        return (
            <div>
                <Header />
                <Filters 
                    setFiletype={this.setFiletype} 
                    setBeginDate={this.setBeginDate}
                    setEndDate={this.setEndDate}
                    setDatatype={this.setDatatype}
                    validateFilters={this.validateFilters}
                    data={filterData}
                />
            </div>
        )
    }
}