"""OpenAPI v3 Specification"""

# apispec via OpenAPI
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields

# Create an APISpec
spec = APISpec(
    title="Web Service - DataLake",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Define schemas
class InputSchema(Schema):
    parameter = fields.String(description="A string.", required=True)

class OutputSchema(Schema):
    msg = fields.String(description="A message.", required=True)

# register schemas with spec
#spec.components.schema("Input", schema=InputSchema)
spec.components.schema("Output", schema=OutputSchema)

# add swagger tags that are used for endpoint annotation
tags = [
            {'name': 'mongodb_router',
             'description': 'Routes relative to MongoDB'
            },
            {'name': 'influxdb_router',
             'description': 'Routes relative to InfluxDB'
            },
              {'name': 'openstack_swift_router',
             'description': 'Routes relative to Openstack Swift'
            }
       ]

for tag in tags:
    print(f"Adding tag: {tag['name']}")
    spec.tag(tag)