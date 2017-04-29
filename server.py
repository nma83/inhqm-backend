from flask import Flask, request
import db
import json

application = Flask(__name__)
pgdb = db.pgdb()

@application.route("/view", methods=['POST'])
def view():
    nodes = request.get_json()
    ways = pgdb.waysFromNodes(nodes['body'])
    return json.dumps(ways)

@application.route("/search")
def search():
    nodesRet = []
    searchword = request.args.get('q', '')
    if searchword != '':
        nodes = pgdb.getNodes(searchword)
    else:
        nodes = []
    for i in nodes:
        nodesRet.append({ 'value': i[0], 'label': [i[1], i[2]] })
    return json.dumps(nodesRet)

@application.route("/edit", methods=['POST'])
def edit():
    ways = request.get_json()
    pgdb.saveWays(ways['body'])
    return json.dumps({ 'code': 'Ok' })

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
