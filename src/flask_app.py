from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
from models import MysfitModel
from utils import precheck
from os import environ as env
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

_ = boto3.resource('dynamodb', region_name=env.get('AWS_DEFAULT_REGION', 'us-east-1'))
TABLE = _.Table(env.get('TABLE'))
force_load = 'FORCE_UPDATE' in env.keys()

precheck(TABLE, force=force_load)

# The service basepath has a short response just to ensure that healthchecks
# sent to the service root will receive a healthy response.
@app.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /mysfits instead. Please refer to documentation."})

# Retrive mysfits from DynamoDB based on provided querystring params, or all
# mysfits if no querystring is present.
@app.route("/mysfits", methods=['GET'])
def getMysfits():

    model = MysfitModel()
    logger.info("Testing")
    filterCategory = request.args.get('filter')
    if filterCategory:
        filter = {}
        attributeName=request.args.get('filter')
        if attributeName == "GoodEvil":
            filter['indexName'] = MysfitModel.GOODEVILINDEX
        elif attributeName == "LawChaos":
            filter['indexName'] = MysfitModel.LAWCHAOSINDEX
        else:
            raise Exception("Unknown FilterExpression Key")
        filter['attributeKey'] = attributeName
        filter['attributeValue'] = request.args.get('value')
        resp = json.dumps(model.list_items(table=TABLE, filter=filter))
    else:
        resp = json.dumps(model.list_items(table=TABLE))

    flaskResponse = Response(resp)
    flaskResponse.headers.add('Access-Control-Allow-Origin', '*')
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# retrieve the full details for a specific mysfit with their provided path
# parameter as their ID.
@app.route("/mysfits/<name>", methods=['GET'])
def getMysfit(name):

    model = MysfitModel()
    resp = model.get(attributeKey='Name', attributeValue=name )
    flaskResponse = Response(json.dumps(resp))
    flaskResponse.headers.add('Access-Control-Allow-Origin', '*')
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
