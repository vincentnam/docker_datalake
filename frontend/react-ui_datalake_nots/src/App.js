import React from 'react';

import './App.css';
import { makeStyles } from '@material-ui/core/styles';
import 'react-dropzone-uploader/dist/styles.css'
import DropZoneCard from './components/DropZoneCard'
import Dashboard from "./components/Dashboard";
import Testfield from "./components/Testfield";
import {Container, Row, Col, Navbar, Nav, NavDropdown, Form, FormControl, Button} from "react-bootstrap";
import Navbar_dash from "./components/Navbar";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link, BrowserRouter
} from "react-router-dom";
import TrafficCount from "./components/TrafficCount";
import D3component from "./components/d3component_graph";
import D3Graph from "./components/d3component_graph";
import D3Histo from "./components/d3component_histogram";
import D3Test from "./components/dropzone/Upload";
import D3TimeSerie from "./components/d3compoenent_timeserie";
import Upload from "./components/dropzone/Upload";


function Test(){
  return <div>TEST</div>
}
function App() {


  const useStyles = makeStyles({
    root: {
      minWidth: 275,
    },
    bullet: {
      display: 'inline-block',
      margin: '0 2px',
      transform: 'scale(0.8)',
    },
    title: {
      fontSize: 14,
    },
    pos: {
      marginBottom: 12,
    },
  });

  var componentConfig = { postUrl: 'no-url' };
  var djsConfig = { autoProcessQueue: true,
    dictDefaultMessage: "Déposez un fichier à téléverser - Drop file to upload it",
    addRemoveLinks:true, multiple: true }
  var eventHandlers = { addedfile: (file) => console.log(file) }
  return (
      // <D3Test></D3Test>
      <div>
        <Router>
        <header>

            <Navbar className="light" bg="light"    expand="lg">
              <Navbar.Brand href="#home">neOCampus datalake</Navbar.Brand>
              <Navbar.Toggle aria-controls="basic-navbar-nav" />
              <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                  <Nav.Link  href="#home"><Link to={"/data_insertion"}> Data insertion </Link></Nav.Link>
                  <Nav.Link href="#link"><Link to={"data_vizualisation"}>Data visualization</Link></Nav.Link>
                  <Nav.Link href="#link"><Link to={"data_download"}>Data download</Link></Nav.Link>
                  <NavDropdown title="Data download" id="basic-nav-dropdown">
                    <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
                    <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
                    <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
                    <NavDropdown.Divider />
                    <NavDropdown.Item href="#action/3.4">Separated link</NavDropdown.Item>
                  </NavDropdown>
                </Nav>
                <Form inline>
                  <FormControl type="text" placeholder="Search" className="mr-sm-2" />
                  <Button variant="outline-success">Search</Button>
                </Form>

              </Navbar.Collapse>


            </Navbar>


        </header>
        <main>
          <Route path="/data_insertion">

            <Container>
              <Row>
                <Col sm={12} style={{paddingTop:"10px"}}>

                  <DropZoneCard config={componentConfig}
                                                                               eventHandlers={eventHandlers}
                                                                               djsConfig={djsConfig}></DropZoneCard>

                  {/*<D3Graph data={"tt"}></D3Graph>*/}

                </Col>
                <Col sm={4}>
                </Col>
              </Row>
              {/*<Row>*/}
              {/*  <Col sm>sm=true</Col>*/}
              {/*  <Col sm>sm=true</Col>*/}
              {/*  <Col sm>sm=true</Col>*/}
              {/*</Row>*/}
            </Container>
          </Route>
          <Route path="/data_vizualisation" component={Test}>
            <Container>
            <Row>
              <Col sm={12} style={{paddingTop:"10px"}}>
                  <Col sm={4}>
                    <TrafficCount></TrafficCount>
                  </Col>
                  <Col sm={12}>
                  <D3TimeSerie  data={"tt"}></D3TimeSerie>
                    {/*<D3Test  data={"tt"}></D3Test>*/}
                    <div className="Card">
                      <Upload/>
                    </div>
                    {/*<Upload/>*/}
                  </Col>
                </Col>
              </Row>
            </Container>
        </Route>
        <Route path="/data_download" >  </Route>
        </main>
        </Router>
      </div>

  );
}

export default App;
