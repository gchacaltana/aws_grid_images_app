import './App.css';

import React, { useState } from 'react';
import { Row, Col, Button, Container, Form, Badge, Spinner, Nav, NavItem, NavLink} from 'react-bootstrap';
import { FileUploader } from "react-drag-drop-files";

import { withAuthenticator } from '@aws-amplify/ui-react';
import { Auth } from '@aws-amplify/auth';
import { generate }  from "randomstring";

import '@aws-amplify/ui-react/styles.css';

const fileTypes = ["JPG", "JPEG"];
const baseUrl = 'REPLACE_ME_WITH_THE_API_URL'

function App({ signOut, user }) { 
  const [uploadingCount, setUploadingCount] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  const [uniqueId, ] = useState(generate());
  const [img, setImg] = useState();
  const [gridGenerating, setGridGenerating] = useState(false);


  const handleChange = (files) => {

    for (let i=0; i<files.length; i++) {
      setUploadingCount(prevUploadingCount => prevUploadingCount + 1);
      const file = files[i];
      var reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = async function () {
        fetch(
          `${baseUrl}/add_image?uniqueGridId=${uniqueId}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "image/jpg",
              'Authorization': user.signInUserSession.idToken.jwtToken
            },
            body: this.result
          }
        ).then(() => {
          setFileCount((prevFileCount) => prevFileCount + 1);
          setUploadingCount((prevUploadingCount) => prevUploadingCount - 1);
        });
      };
      reader.onerror = function (error) {
        console.log('Error: ', error);
      };
    }
  };

  const generateGrid = async () => {
    var sess = await Auth.currentSession();
    setGridGenerating(true);
    fetch(
      `${baseUrl}/generate_grid?uniqueGridId=${uniqueId}`,
      {
        
        
        method: "POST",
        headers: {
          'Authorization': sess.getAccessToken().getJwtToken()
        },
      }
    )
      .then((response) => response.json())
      .then((data) => {
        const imageUrl = data["presigned_url"];
        console.log(imageUrl);
        setImg(imageUrl);
        setGridGenerating(false);
      });
  };
  
  return (
    
    <Container className="p-3">
    <Nav className="justify-content-center"><NavItem><NavLink onClick={signOut}>Sign out</NavLink></NavItem></Nav>
    <Row>
    <Col>
      <Form>
        <Form.Group className="mb-3">
          <Form.Label>UniqueGridId</Form.Label>
          <Form.Control
            type="text"
            id="inputUniqueId"
            value={uniqueId}
            readOnly
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Drag and drop images below</Form.Label>
          <FileUploader
                disabled={uploadingCount > 0}
                multiple={true}
                handleChange={handleChange}
                name="file"
                types={fileTypes}
              />
          
        </Form.Group>
        <Form.Group className="mb-3">
          { uploadingCount > 0 && <Spinner></Spinner> } <Form.Label>Uploaded <Badge bg="primary">{fileCount}</Badge> images</Form.Label>
        </Form.Group> 
      </Form>

     { gridGenerating ? <Spinner></Spinner> :  <Button onClick={() => generateGrid()}>Generate Grid </Button> }
     
      <p><img src={img}  alt=""/></p>

    </Col>
    </Row>
    </Container>
  );
}

export default withAuthenticator(App);