from flask import jsonify
import json

# get_all_buckets method

def test_get_all_buckets_if_key_is_present(client):
    response = client.get("/api/bucket")
    result = json.loads(response.data)
    assert "buckets" in result

def test_get_all_buckets_if_response_is_dict(client):
    response = client.get("/api/bucket")
    result = json.loads(response.data)
    assert isinstance(result, dict)

    