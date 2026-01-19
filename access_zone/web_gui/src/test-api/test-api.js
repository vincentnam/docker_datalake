
const minio = require("minio")
let mc
try {
  mc = new minio.Client(/*{
    endPoint: "play.min.io",
    port: 9000,
    useSSL: true,
    accessKey: "Q3AM3UQ867SPQQA43P2F",
    secretKey: "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG"
}*/
    {
      endPoint: "localhost",
      useSSL: false,
      port: 8080,
      accessKey: "test:tester",
      secretKey: "testing"
    },
    /* {
       endPoint:"localhost",
       useSSL: false,
       port: 20001,
       accessKey: "my-service-account",
       secretKey: "my-svc-secret-key",
       userAgent:window.navigator.userAgent
     }*/
    //Assume role example::
    //https://github.com/minio/minio/blob/master/docs/sts/assume-role.md#testing-an-example-with-assume-rolego

    /*,
    {
        endPoint: "localhost",
        useSSL: false,
        port: 9000,
        accessKey: "H3ERY005GCGQ98KM0DP5",
        secretKey: "MSG+WRmt8O8nxeHinNW8v9QcLT1t7JoL14zO71OH",
        sessionToken: "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NLZXkiOiJIM0VSWTAwNUdDR1E5OEtNMERQNSIsImV4cCI6MTY1NzYyMDA1OSwicGFyZW50IjoibWluaW8ifQ.3ZM7Tg9qMoCV6-sRbmdEc064-Fhtp0eBOBcgetUWx8GfihZZAnInspdiiNZFl_bq43UAh0VHg-etkhkzsvN0EA"

    }*/
  );
}catch (err){
  console.log("Error::",err)
}


mc.setRequestOptions({timeout:500})


    const removeObjectTest = () => {


      const deleteList = [{name:"non-existent"}]

      for(let i=0;i<3; i++){
        deleteList.push({
          name:`${i}.txt`
        })
      }

      deleteList.splice(2, 0, { name:"does not exist object2"} )
      deleteList.splice(1108, 0, { name:"does not exist object1110"} )

      console.log(deleteList)
      mc.removeObjects("test-bucket", deleteList ,(e, res) => {

        if (e) {
          return console.log(e)
        }
        console.log("Success", res)
// Note : Inspect the res to find out if an object deletion is success or failure.

      })
}
mc.traceOn()

removeObjectTest()



const testSelObjectContent = () =>{

  const bucketName = 'test-bucket'
  const objectName = 's3sel/large-data.json'
  mc
    .selectObjectContent(bucketName, objectName, {
      // expression: "SELECT name FROM S3Object WHERE name IN('vEOGnc', '7IhCAC') LIMIT 2", // 2 rows
      // expression: "SELECT name FROM S3Object WHERE name IN('vEOGnc', 'non-exist') LIMIT 2", // Error: Header Checksum Mismatch, Prelude CRC of 41 does not equal expected CRC of -6437716
      // expression: "SELECT name FROM S3Object WHERE name IN('vEOGnc') LIMIT 2", // Error: Header Checksum Mismatch, Prelude CRC of 85 does not equal expected CRC of 1861855291

      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'anWuPo') limit 2", // 2 rows
      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'non-exist') limit 2", //only one row but limit 2
      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'non-exist') limit 101", //only one row but limit 101 file has only 100 rows
      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'non-exist') limit 1", //only one row but limit 101 file has only 100 rows
      // expression: 'select name from s3object as s  LIMIT 500',
      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'anWuPo') limit 5",
      // expression: "select name from s3object as s where s.name IN ('huAsbq', 'anWuPo') limit 1",
      // expression: 'select name from s3object as s  LIMIT 5',
      // expression: "select name from s3object as s  where s.name LIKE 'd%'", // 3 results following are limit in incremental to non existent.
      // expression: "select name from s3object as s  where s.name LIKE 'd%' limit 1",
      // expression: "select name from s3object as s  where s.name LIKE 'd%' limit 2",
      // expression: "select name from s3object as s  where s.name LIKE 'd%' limit 3",
      // expression: "select name from s3object as s  where s.name LIKE 'd%' limit 4",
      // expression: "select name from s3object as s  where s.name LIKE 'd%' limit 5",
      // expression: "select name from S3Object as s where s.name IN ('huAsbq', 'AbapuL') limit 2",
      // expression: "select * from s3object as s where  s.type LIKE 'U%' limit 1",

      inputSerialization: { JSON: { Type: 'LINES' } },
      outputSerialization: { JSON: { RecordDelimiter: '\n' } },
      expressionType: 'SQL',
    })
    .then((res) => {
      console.log(res.records.toString())
      console.log('Success')
    })
    .catch((err) => {
      if (err) {
        return console.log('Unable to process select object content.', err.message)
      }
    })

}

