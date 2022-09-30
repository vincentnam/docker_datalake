import json

# get_last_raw_data method

mimetype = 'application/json'
headers = {
    'Content-Type': mimetype,
    'Accept': mimetype
}

def test_get_last_raw_data_if_key_is_present(client):
    
    params = {
         'container_name': 'neOCampus'
    }
    response = client.post("/api/last-raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    assert "result" in result

def test_get_last_raw_data_if_response_is_dict(client):
    
    params = {
         'container_name': 'neOCampus'
    }
    response = client.post("/api/last-raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    assert isinstance(result, dict)

def test_get_last_raw_data_if_parameter_is_present(client):
    
    params = {
        
    }
    response = client.post("/api/last-raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    assert "result" in result

# get_metadata method

def test_get_metadata_if_all_parameters_are_present(client):
    
    params = {
        'beginDate': '2021-04-01',
        'endDate' : '2022-03-30',
        "filetype": [
            "application/json"
        ]
    }
    response = client.post("/api/raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    
    assert "error" in result and result['error'] == "Missing required fields."

def test_get_metadata_if_campus_parameter_is_absent(client):
    
    params = {
        'beginDate': '2021-04-01',
        'endDate' : '2022-03-30',
        "filetype": [
            "application/json"
        ]
    }
    response = client.post("/api/raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    
    assert "error" in result and result['error'] == "Missing required fields."

def test_get_metadata_if_filetype_parameter_is_absent(client):
    
    params = {
        'container_name': 'neOCampus',
        'beginDate': '2021-04-01',
        'endDate': '2021-03-30'
    }
    response = client.post("/api/raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    print(result)
    assert "error" in result and result['error'] == "Missing required fields."

def test_get_metadata_if_filetype_parameter_is_absent(client):
    
    params = {
        'beginDate': '2021-04-01',
        'endDate' : '2022-03-30'
    }
    response = client.post("/api/raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    
    assert "error" in result and result['error'] == "Missing required fields."

def test_get_metadata_if_limit_is_absent(client):
    
    params = {
        'beginDate': '2021-04-01',
        'endDate' : '2022-03-30'
    }
    response = client.post("/api/raw-data", data=json.dumps(params), headers=headers)
    result = json.loads(response.data)
    
    assert "error" in result and result['error'] == "Missing required fields."