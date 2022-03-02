package service

import com.google.gson.Gson
import com.typesafe.config.Config
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

class MongoWriter(config: Config) {

//  @transient lazy val log = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val mongodbUri = s"mongodb://${config.getString("mongo.host")}:${config.getString("mongo.port")}/"

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
                     dataProcess: String, application: String, originalObjectName: String, mqtt_topic: String = null,
                     successfulOperations: Array[String] = null, failedOperations: Array[String] = null, otherData: String = null) = {

//    log.info("Writing metadata to Swift database")

    val historicalMetaData = HistoricalMetaData(contentType, dataProcess, swiftUser, containerName, id, application, originalObjectName,
      mqtt_topic, successfulOperations, failedOperations, processedDataAreaService, otherData)

    val gson = new Gson

    val jsonString = gson.toJson(historicalMetaData)

    val dataSet = spark.createDataset(jsonString :: Nil)

    spark.read.json(dataSet).toDF()
      .withColumn("creation_date", current_timestamp())
      .write
      .format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "swift", "collection" -> containerName))
      .mode("append")
      .save()
  }

  /**
   * Used to get id of the new object to add in Openstack Swift
   *
   */
  def putIntoStatsAndGetSwiftId(): Int = {

//    log.info("Getting last swift ID for new object")

    val swiftCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift")).load()

    val schema = StructType(Seq(
      StructField("type", StringType, false),
      StructField("object_id", IntegerType, false)
    ))

    val toInsert = if (swiftCollection.isEmpty) {

      val toInsert = """{"type": "object_id_file", "object_id": 0}"""
      val jsonToInsert = spark.createDataset(toInsert :: Nil)

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
   * Used to reset id if insertion to Openstack Swift failed
   */
  def resetLastSwiftId(): Unit = {

//    log.info("Reseting last swift ID")

    val swiftCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift")).load()

    val lastId = swiftCollection.select("object_id").first().getInt(0) - 1

    if (lastId >= 0)
      swiftCollection.withColumn("object_id", lit(lastId)).write
        .format("com.mongodb.spark.sql.DefaultSource")
        .options(Map("uri" -> mongodbUri, "database" -> "stats", "collection" -> "swift"))
        .mode("append")
        .save()
  }

  /**
   *
   * @param creation_date
   * @param swift_container
   * @param swift_user
   * @param swift_object_id
   * @param task_type
   * @param old_data
   * @param new_data
   */
  def putIntoHistoryDB(creation_date: String,
                       swift_container: String,
                       swift_user: String,
                       swift_object_id: String,
                       task_type: String,
                       old_data: String,
                       new_data: String): Unit = {

//    log.info("Writing Operation History")

    val OperationHistoryData = OperationHistory(creation_date, swift_container, swift_user, swift_object_id, task_type,
      old_data, new_data)

    val gson = new Gson
    val dataSet = spark.createDataset(gson.toJson(OperationHistoryData) :: Nil)

    spark.read.json(dataSet).toDF().write
      .format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri,
        "database" -> config.getString("mongo.historyDB"),
        "collection" -> "operations_mqtt"))
      .mode("append")
      .save()
  }

  case class OperationHistory(creation_date: String,
                              swift_container: String,
                              swift_user: String,
                              swift_object_id: String,
                              task_type: String,
                              old_data: String,
                              new_data: String
                             )

  case class HistoricalMetaData(content_type: String, data_process: String, swift_user: String, swift_container: String,
                                swift_object_id: String, application: String, original_object_name: String,
                                mqtt_topic: String, successful_operations: Array[String], failed_operations: Array[String],
                                processed_data_area_service: String, other_data: String)
}
