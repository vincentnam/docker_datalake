package jobs

import com.typesafe.config.{Config, ConfigFactory}
import config.Configuration
import org.apache.spark.sql.Row
import service.{DataWriter, HistoricalDataImporter, MongoWriter}
import util.Serialization

import scala.util.{Failure, Success}

object InsertHistoricalDataJob {

//  @transient lazy val log = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val projectName = "neOCampus"

  def start(): Unit = {
//    log.info("Launching historical neOCampus data insertion into Data Lake")

    val configuration: Config = ConfigFactory.load()
    val conf: Configuration = new Configuration(configuration)

    val importer = new HistoricalDataImporter(conf)

    //var data = importer.importData(args(0))
    val data = importer.importData()

    val metadataWriter = new MongoWriter(configuration, null)
    // Get the Swift ID counter and increase it
    val id = metadataWriter.putIntoStatsAndGetSwiftId()

    val dataWriter = new DataWriter(conf)

    val inserted = dataWriter.put("neOCampus", id.toString, Serialization.serialization(data))

    // handle atomic insertion & failure
    inserted match {
      case Success(df) => {
        metadataWriter.putIntoSwiftDB("csv", "test:tester", projectName, id.toString,
          "MongoDB", "default",
          "Historical Real time data coming from CSV file to be inserted in Swift and MongoDB",
          "sensors.csv")
      }
      case Failure(exception) => {
//        log.error(s"Execption Occured while inserting data into data lake. Reseting swift Id : $exception")
        metadataWriter.resetLastSwiftId()
      }
    }
  }
}
