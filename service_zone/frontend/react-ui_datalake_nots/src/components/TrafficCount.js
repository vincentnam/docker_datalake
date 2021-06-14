/* eslint-disable no-script-url */

import React from 'react';
import Link from '@material-ui/core/Link';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Title from './Title';


const classes = themes =>
    (
        {
            depositContext:
                {
                    flex: 1,
                },
        }
    )
;


export default class TrafficCount extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            nbcar : 0
        }
    }
    componentDidMount() {
        fetch("/nbcar")
            .then(res => res.json())
            .then(data => this.setState({nbcar: data.nbcar}));

    }

    render() {

        let vnb_car = parseInt(this.state.nbcar);
        if (vnb_car===0){
            vnb_car = 1 ;
        }
        const vnb_car_props= parseInt(this.props.nbcar );
        return (
            <React.Fragment>
                <Title> Car seen </Title>
                <Typography component="p" variant="h4">
                    {vnb_car * vnb_car_props}
                </Typography>
                <Typography color="textSecondary"
                            className={classes.depositContext}>
                    on 16 March, 2019
                </Typography>
                <div>
                    <Link color="primary" href="javascript:;">
                        View balance
                    </Link>
                </div>
            </React.Fragment>
        );
    }
}
