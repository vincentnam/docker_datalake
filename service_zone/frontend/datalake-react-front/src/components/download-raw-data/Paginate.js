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
                { this.props.elts.length ? 
                    <div class="commentBox">
                            <ReactPaginate
                                previousLabel={'<'}
                                nextLabel={'>'}
                                breakLabel={'...'}
                                pageCount={this.props.pageCount}
                                marginPagesDisplayed={2}
                                pageRangeDisplayed={5}
                                onPageChange={this.props.handlePageClick}
                                activeClassName={'active'}
                                breakClassName={'page-item break-me d-md-flex'}
                                breakLinkClassName={'page-link btn'}
                                containerClassName={'pagination'}
                                pageClassName={'page-item d-md-flex'}
                                pageLinkClassName={'page-link btn'}
                                previousClassName={'page-item d-md-flex'}
                                previousLinkClassName={'page-link btn'}
                                nextClassName={'page-item d-md-flex'}
                                nextLinkClassName={'page-link btn'}
                                forcePage={this.props.selected}
                            />
                    </div>
            : '' }
            </div>
        );
    }
}