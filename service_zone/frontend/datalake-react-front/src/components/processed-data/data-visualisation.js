import React from "react";
import { Graph } from './graph';
import { useTable, usePagination } from "react-table";


export class DataVisiualisation extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
    }
    times() {
        const times = this.props.dataGraph._time;
        const result = [];
        if (times !== undefined) {
            for (const [key, value] of Object.entries(times)) {
                result.push(value);
            }
        }
        return result;
    }

    values() {
        const values = this.props.dataGraph._value;
        const result = [];
        if (values !== undefined) {
            for (const [key, value] of Object.entries(values)) {
                result.push(value);
            }
        }
        return result;
    }
    numberData() {
        let data = this.props.dataGraph._value;
        let result = null
        if (data === undefined) {
            result = 0;
        } else {
            result = Object.keys(this.props.dataGraph._value).length;
        }
        return result;
    }
    render() {
        const Table = ({ data }) => {
            const columns = React.useMemo(
                () => [
                    {
                        Header: 'Tableau des données',
                        columns: [
                            {
                                Header: "Datetime",
                                accessor: "_time"
                            },
                            {
                                Header: "Valeur",
                                accessor: "_value"
                            },
                            {
                                Header: "Measurement",
                                accessor: "_measurement"
                            },
                            {
                                Header: "Topic",
                                accessor: "topic"
                            }
                        ]
                    }
                ],
                []
            );
            // Use the state and functions returned from useTable to build your UI
            const {
                getTableProps,
                getTableBodyProps,
                headerGroups,
                prepareRow,
                page, // Instead of using 'rows', we'll use page,
                // which has only the rows for the active page

                // The rest of these things are super handy, too ;)
                canPreviousPage,
                canNextPage,
                pageOptions,
                pageCount,
                gotoPage,
                nextPage,
                previousPage,
                setPageSize,
                state: { pageIndex, pageSize }
            } = useTable(
                {
                    columns,
                    data,
                    initialState: { pageIndex: 0 }
                },
                usePagination
            );

            // Render the UI for your table
            return (
                <>
                    <div className="grid shadow-sm p-2 mb-4">
                        <table {...getTableProps()} className="table table-bordered table-responsive-sm">
                            <thead>
                                {headerGroups.map((headerGroup) => (
                                    <tr {...headerGroup.getHeaderGroupProps()}>
                                        {headerGroup.headers.map((column) => (
                                            <th className="text-center th-color" scope="col" {...column.getHeaderProps()}>{column.render("Header")}</th>
                                        ))}
                                    </tr>
                                ))}
                            </thead>
                            <tbody {...getTableBodyProps()}>
                                {page.map((row, i) => {
                                    prepareRow(row);
                                    return (
                                        <tr {...row.getRowProps()}>
                                            {row.cells.map((cell) => {
                                                return (
                                                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                                                );
                                            })}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                        {/* Pagination can be built however you'd like. 
                            This is just a very basic UI implementation:
                        */}
                        <div className="pagination d-flex align-content-center justify-content-between">
                            <div className="col-sm-6">
                                <button className="btn btn-table" onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                                    {"<<"}
                                </button>{" "}
                                <button className="btn btn-table" onClick={() => previousPage()} disabled={!canPreviousPage}>
                                    {"<"}
                                </button>{" "}
                                <span className="mr-2 ml-4">
                                    Page{" "}
                                    <strong>
                                        {pageIndex + 1} sur {pageOptions.length}
                                    </strong>{" "}
                                </span>
                                <button className="btn btn-table" onClick={() => nextPage()} disabled={!canNextPage}>
                                    {">"}
                                </button>{" "}
                                <button className="btn btn-table" onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                                    {">>"}
                                </button>{" "}
                            </div>
                            <div className="col-sm-2">
                                <select className="form-control"
                                    value={pageSize}
                                    onChange={(e) => {
                                        setPageSize(Number(e.target.value));
                                    }}
                                >
                                    {[10, 20, 30, 40, 50].map((pageSize) => (
                                        <option key={pageSize} value={pageSize}>
                                            Montrer {pageSize}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </>
            );
        }
        const TitleGraph = () => {
            if (this.props.topic === "") {
                return (
                    <h5></h5>
                );
            } else {
                return (
                    <h5 className="title-graph mb-4">Bucket: <span><b>{this.props.bucket}</b></span> - Measurement: <span><b>{this.props.measurement}</b></span> - Topic: <span><b>{this.props.topic}</b></span></h5>
                );
            }
        }
        
        const Show = () => {
            if (this.props.topic === "") {
                return (
                    <div></div>
                );
            } else {
                return (
                    <div className="card p-3">
                        <TitleGraph />
                        <Graph 
                            dataGraph={this.props.dataGraph}
                        />
                    </div>
                );
            }
        }

        return (
            <div className="mt-1 row d-flex">
                <nav className="tab-show">
                    <div className="nav nav-pills" id="pills-tab" role="tablist">
                        <button className="nav-link active" id="nav-raw-tab" data-bs-toggle="pill"
                                data-bs-target="#nav-raw" type="button" role="tab" aria-controls="nav-raw"
                                aria-selected="true">Graphique
                        </button>
                        <button className="nav-link" id="nav-handled-tab" data-bs-toggle="pill"
                                data-bs-target="#nav-handled" type="button" role="tab" aria-controls="nav-handled"
                                aria-selected="false">Tableau de données
                        </button>
                    </div>
                </nav>
                <div className="tab-content mt-2" id="pills-tabContent">
                    <div className="tab-pane fade show active" id="nav-raw" role="tabpanel"
                        aria-labelledby="nav-raw-tab">
                        <Show />
                    </div>
                    <div className="tab-pane fade" id="nav-handled" role="tabpanel"
                        aria-labelledby="nav-handled-tab">
                        <div  className="data-table">
                            <Table data={this.props.data} />
                        </div>
                    </div>
                </div>  
            </div>
        );
    }
}