package service

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import com.google.gson.Gson
import com.mongodb.spark.MongoSpark
import com.mongodb.spark.sql.helpers.StructFields
import org.bson.Document

object MetadataWriter {


  val mongoHost =  "127.0.0.1" //  "10.200.156.254"
  val mongoPort = "27017"
  val mongoUser = "admin"
  val mongoPwd = "admin"

  //val mongodbUri = "mongodb://" + mongoUser + ":" + mongoPwd + "@" + mongoHost + ":" + mongoPort + "/"

  val mongodbUri = "mongodb://" + mongoHost + ":" + mongoPort + "/"

  val spark = SparkSession
    .builder()
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse")
    .master("local[*]")
    //.config("spark.mongodb.input.uri", mongodbUri + "stats.test_sabri")
    .getOrCreate()

  import spark.implicits._

  def putIntoSwiftDB(contentType: String, swiftUser: String, containerName: String, id: String, processedDataAreaService: String,
          dataProcess: String, application: String, originalObjectName: String,successfulOperations: Array[String],
          failedOperations: Array[String], otherData: String)= {

    val historicalMetaData = HistoricalMetaData(contentType,dataProcess, swiftUser, containerName, id, application, originalObjectName,
      successfulOperations, failedOperations, processedDataAreaService, otherData)

    val gson = new Gson

    val jsonString = gson.toJson(historicalMetaData)

    println(jsonString)
    val dataSet = spark.createDataset(jsonString :: Nil)


    spark
      .read
      .json(dataSet)
      .toDF()
      .write
      .format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "swift", "collection" -> containerName))
      .mode("append")
      .save()
  }

  /**
   *  Used to get id of the new object to add in Openstack Swift
   *
   */
  def putIntoStatsAndGetSwiftId() = {

    val swiftCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "test_sabri")).load()

    val schema = StructType(Seq(
      StructField("type", StringType, false),
      StructField("object_id", IntegerType, false)
    ))

    var newId = 0

     val toInsert = swiftCollection.isEmpty match {
      case true => {
        val toInsert = """{"type": "object_id_file", "object_id": 0}"""
        val jsonToInsert = spark.createDataset(toInsert:: Nil)

        spark
          .read
          .option("encoding", "UTF-8")
          .option("multiline", true)
          .schema(schema)
          .json(jsonToInsert)
          .toDF()
          .write
          .format("com.mongodb.spark.sql.DefaultSource")
          .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "test_sabri"))
          .mode("overwrite")
          .save()

        0
        // TODO create unique index on object_id to ensure the uniqueness of the field
      }
      case false => {
        val newId = swiftCollection.select("object_id").first().getInt(0) + 1


        println(newId)
        swiftCollection.toDF().withColumn("object_id", lit(newId)).write
          .format("com.mongodb.spark.sql.DefaultSource")
          .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "test_sabri"))
          .mode("append")
          .save()

        newId
      }
    }
  }

  case class Stats(object_id: Int)

  case class HistoricalMetaData(content_type: String, data_process: String, swift_user: String, swift_container: String,
                            swift_object_id: String, application: String, original_object_name: String,
                            successful_operations: Array[String], failed_operations: Array[String],
                            processed_data_area_service: String,other_data: String)
}
