import React from 'react';
import ReactPaginate from 'react-paginate';

export class Paginate extends React.Component {

    constructor(props) {
        super(props);
        this.props = props;
    }
    render() {
        return (
            <div>
                { this.props.data.length ? 
                    <div class="commentBox">
                            <ReactPaginate
                                previousLabel={'previous'}
                                nextLabel={'next'}
                                breakLabel={'...'}
                                pageCount={this.props.pageCount}
                                marginPagesDisplayed={2}
                                pageRangeDisplayed={5}
                                onPageChange={this.props.handlePageClick}
                                activeClassName={'active'}
                                breakClassName={'page-item break-me'}
                                breakLinkClassName={'page-link'}
                                containerClassName={'pagination row justify-content-md-center'}
                                pageClassName={'page-item'}
                                pageLinkClassName={'page-link'}
                                previousClassName={'page-item'}
                                previousLinkClassName={'page-link'}
                                nextClassName={'page-item'}
                                nextLinkClassName={'page-link'}
                                forcePage={this.props.selected}
                            />
                    </div>
            : '' }
            </div>
        );
    }
}