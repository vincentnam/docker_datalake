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
                    <table {...getTableProps()} class="table table-bordered table-responsive-sm">
                        <thead class="thead-dark">
                            {headerGroups.map((headerGroup) => (
                                <tr {...headerGroup.getHeaderGroupProps()}>
                                    {headerGroup.headers.map((column) => (
                                        <th class="text-center" scope="col" {...column.getHeaderProps()}>{column.render("Header")}</th>
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
                    <div class="pagination d-flex align-content-center justify-content-between">
                        <div>
                            <button class="btn btn-primary" onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                                {"<<"}
                            </button>{" "}
                            <button class="btn btn-primary" onClick={() => previousPage()} disabled={!canPreviousPage}>
                                {"<"}
                            </button>{" "}
                            <button class="btn btn-primary" onClick={() => nextPage()} disabled={!canNextPage}>
                                {">"}
                            </button>{" "}
                            <button class="btn btn-primary" onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>
                                {">>"}
                            </button>{" "}
                        </div>
                        <span class="mr-2 ml-4">
                            Page{" "}
                            <strong>
                                {pageIndex + 1} sur {pageOptions.length}
                            </strong>{" "}
                        </span>
                        <select class="form-control col-sm-2"
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
                </>
            );
        }
        const TitleGraph = () => {
            if (this.props.topic === "") {
                return (
                    <h4>Graphique: </h4>
                );
            } else {
                return (
                    <h4>Graphique: Bucket: {this.props.bucket} avec le Measurement: {this.props.measurement} et le Topic: {this.props.topic}</h4>
                );
            }
        }
        return (
            <div>
                <h2>Data visualisation</h2>
                <TitleGraph />
                <Graph
                    dataGraph={this.props.dataGraph}
                />
                <br/>
                <div  class="mt-4">
                    <Table data={this.props.data} />
                </div>
            </div>
        );
    }
}