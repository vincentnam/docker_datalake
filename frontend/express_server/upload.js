const IncomingForm = require('formidable').IncomingForm
const request = require('request')
const streamBuffers = require('stream-buffers')
const Swiftclient = require('openstack-swift-client')
const swift_authenticator = new Swiftclient.SwiftAuthenticator('http://141.115.103.30:8080/auth/v1.0', 'test:tester', 'testing');
const swift_client = new Swiftclient(swift_authenticator)
const stream_lib = require("stream")
const mongo = require("mongodb")


swift_client.container.create = function (name, stream, meta, extra) {
    return this.authenticator.authenticate().then(auth => new Promise((resolve, reject) => {
        const req = request({
            method: 'PUT',
            uri: `${auth.url + this.urlSuffix}/${name}`,
            headers: this.headers(meta, extra, auth.token)
        }).on('error', err => {
            reject(err);
        }).on('response', response => {
            if (response.statusCode === 201) {
                resolve({
                    etag: response.headers.etag
                });
            } else {
                reject(new Error(`HTTP ${response.statusCode}`));
            }
        });

        stream.pipe(req);
    }));
}
swift_client.container.createStaticLargeObject = function (name, manifestList, meta, extra) {
    // for manifestList
    extra = Object.assign({
        'content-type': 'application/json'
    }, extra);

    return this.authenticator.authenticate().then(auth => new Promise((resolve, reject) => {
        request({
            uri: `${auth.url + this.urlSuffix}/${name}?multipart-manifest=put`,
            method: 'PUT',
            headers: this.headers(meta, extra, auth.token),
            json: manifestList
        }).on('error', err => {
            reject(err);
        }).on('response', response => {
            if (response.statusCode === 201) {
                resolve(response);
            } else {
                reject(new Error(`HTTP ${response.statusCode}`));
            }
        });
    }));
}


module.exports = function upload(req, res) {
    let body = []
    let counter = 0
    req.on('data',(chunk)=>{
        body.push(chunk);
        console.log(chunk.length)
        counter += 1
    }).on('end',()=>{
        console.log(body)
        console.log(req.headers)
        const container_name = "my-test2"
        let container = swift_client.container(container_name);
        const buffer = Buffer.concat(body)
        const filename = "test2"
        const stream = new stream_lib.Readable()
        stream.__read = () => {}
        stream.push(buffer)
        stream.push(null)
        console.log(container)
        console.log(req.headers["filename"])
        var MongoClient = mongo.MongoClient

        const mongo_url = "mongodb://141.115.103.31:27017"
        const dbName = "stats"
        var swift_id = -1
        MongoClient.connect(mongo_url, { useUnifiedTopology: true } ,function (err, client){
            var res = {}
            const coll = client.db(dbName).collection('swift');
            coll.findOne({"type":"object_id_file"}, function (err, result){
                // console.log(err)
                console.log(result)
                res = result
                swift_id = res["object_id"]
                console.log(result["object_id"])
                // In the mongoDB callback -> we need to wait the answer

                container.create(swift_id, stream).catch(e =>{
                        if (e.message === "HTTP 404"){
                            client.create(container_name);
                            container = client.container(container_name);
                            container.create(result["object_id"], stream).then(console.log("Fichier ajouté !"));
                            console.log("Rentre dans le 404")
                        }
                    }
                )

                client.db("swift").collection(container_name).insertOne({
                    "swift_id" : result["object_id"],
                    "filename": filename
                    //TODO: ADD OTHER METADATA NEEDED !!
                })

            })
            coll.updateOne({"type":"object_id_file"}, {"$inc": {"object_id": 1}}, function (err, resp){
                if (err) {
                    console.log("Update err")
                    console.log(err)
                }
                if (resp){
                    console.log("Update resp")
                    console.log(resp)
                }
            })
            }

            )





    })

}
// express_rest | ]
// express_rest | SwiftContainer {
//     express_rest |   childName: 'Object',
//     express_rest |   urlSuffix: '/my-container',
//     express_rest |   authenticator: SwiftAuthenticator {
//         express_rest |     _events: [Object: null prototype] {},
//         express_rest |     _eventsCount: 0,
//         express_rest |     _maxListeners: undefined,
//         express_rest |     _authenticate: [Function (anonymous)],
//         express_rest |     [Symbol(kCapture)]: false
//         express_rest |   }
//     express_rest | }

