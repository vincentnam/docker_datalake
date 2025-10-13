import * as minio from "minio";
const mc = new minio.Client(
    {
            endPoint: "localhost",
            useSSL: false,
            port: 8080,
            accessKey: "test:tester",
            secretKey: "testing",
            signatureVersion: "v4",
    },


);
export default mc