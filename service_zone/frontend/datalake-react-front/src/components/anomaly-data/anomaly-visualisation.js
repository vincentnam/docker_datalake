import React from "react";
import { useTable, useSortBy, usePagination } from "react-table";
import * as Icon from 'react-bootstrap-icons';

export class DataAnomalyVisiualisation extends React.Component {
    constructor(props) {
        super(props);
        this.props = props;
    }
    
    render() {
        const Table = ({ data }) => {
            const columns = React.useMemo(
                () => [
                    {
                        Header: 'Tableau des données',
                        columns: [
                            {
                                Header: "Topic",
                                accessor: "_topic"
                            },
                            {
                                Header: "Measurement",
                                accessor: "_unit"
                            },
                            {
                                Header: "Valeur",
                                accessor: "_value"
                            },
                            
                            {
                                Header: "Date first detection",
                                accessor: "_datetime"
                            },
                            {
                                Header: "Date last detection",
                                accessor: "_endDate_detection"
                            },
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
                useSortBy,
                usePagination,
                
            );

            // Render the UI for your table
            return (
                <>
                    <div className="grid shadow-sm p-2 mb-2">
                        <table {...getTableProps()} className="table table-bordered table-responsive-sm">
                            <thead>
                                {headerGroups.map((headerGroup) => (
                                    <tr {...headerGroup.getHeaderGroupProps()}>
                                        {headerGroup.headers.map((column) => (
                                            <th className="text-center th-color" scope="col" {...column.getHeaderProps(column.getSortByToggleProps())}>
                                                {column.render("Header")}
                                                <span>
                                                    {column.isSorted
                                                    ? column.isSortedDesc
                                                        ?  <Icon.CaretDownFill />
                                                        :  <Icon.CaretUpFill />
                                                    : ''}
                                                </span>
                                            </th>
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
       
        
        

        return (
            <div  className="data-table">
                <Table data={this.props.data} />
            </div>
        );
    }
}