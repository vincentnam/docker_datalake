package service

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import com.google.gson.Gson
import config.Configuration

class MetadataWriter(conf: Configuration) {

  @transient lazy val log = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val mongodbUri = "mongodb://" + conf.mongoHost + ":" + conf.mongoPort + "/"

  val spark = SparkSession
    .builder()
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse")
    .master("local[*]")
    .getOrCreate()

  import spark.implicits._

  /**
   * function used to insert metadata into Swift database (MongoDB)
   *
   * @param contentType
   * @param swiftUser
   * @param containerName
   * @param id
   * @param processedDataAreaService
   * @param dataProcess
   * @param application
   * @param originalObjectName
   * @param successfulOperations
   * @param failedOperations
   * @param otherData
   */
  def putIntoSwiftDB(contentType: String, swiftUser: String, containerName: String, id: String, processedDataAreaService: String,
          dataProcess: String, application: String, originalObjectName: String,successfulOperations: Array[String],
          failedOperations: Array[String], otherData: String)= {

    log.info("Writing metadata to Swift database")

    val historicalMetaData = HistoricalMetaData(contentType,dataProcess, swiftUser, containerName, id, application, originalObjectName,
      successfulOperations, failedOperations, processedDataAreaService, otherData)

    val gson = new Gson

    val jsonString = gson.toJson(historicalMetaData)

    val dataSet = spark.createDataset(jsonString :: Nil)

    spark.read.json(dataSet).toDF().write
      .format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "swift", "collection" -> containerName))
      .mode("append")
      .save()
  }

  /**
   *  Used to get id of the new object to add in Openstack Swift
   *
   */
  def putIntoStatsAndGetSwiftId(): Int = {

    log.info("Getting last swift ID for new object")

    val swiftCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift")).load()

    val schema = StructType(Seq(
      StructField("type", StringType, false),
      StructField("object_id", IntegerType, false)
    ))

    val toInsert = if(swiftCollection.isEmpty) {

      val toInsert = """{"type": "object_id_file", "object_id": 0}"""
      val jsonToInsert = spark.createDataset(toInsert:: Nil)

      spark.read.schema(schema).json(jsonToInsert)
        .toDF()
        .write
        .format("com.mongodb.spark.sql.DefaultSource")
        .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift"))
        .mode("overwrite")
        .save()
     0
      // TODO create unique index on object_id to ensure the uniqueness of the field
    } else {
      val newId = swiftCollection.select("object_id").first().getInt(0) + 1

      swiftCollection.withColumn("object_id", lit(newId)).write
        .format("com.mongodb.spark.sql.DefaultSource")
        .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift"))
        .mode("append")
        .save()
      newId
    }
    toInsert
  }

  /**
   *  Used to reset id if insertion to Openstack Swift failed
   */
  def resetLastSwiftId(): Unit = {

    log.info("Reseting last swift ID")

    val swiftCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift")).load()

    val lastId = swiftCollection.select("object_id").first().getInt(0) - 1

    println(s"last id : $lastId")

    if(lastId >= 0)
      swiftCollection.withColumn("object_id", lit(lastId)).write
        .format("com.mongodb.spark.sql.DefaultSource")
        .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift"))
        .mode("append")
        .save()
  }

  case class HistoricalMetaData(content_type: String, data_process: String, swift_user: String, swift_container: String,
                            swift_object_id: String, application: String, original_object_name: String,
                            successful_operations: Array[String], failed_operations: Array[String],
                            processed_data_area_service: String,other_data: String)
}
