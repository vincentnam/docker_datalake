import com.typesafe.config.{Config, ConfigFactory}
import config.Configuration
import service.{DataWriter, HistoricalDataImporter, MetadataWriter}
import util.Serialization

import scala.util.{Failure, Success}

object Main {

  val projectName = "neoCampus"

  System.setProperty("hadoop.home.dir", "C:/hadoop")

  def main(args: Array[String]): Unit = {
    val configuration: Config = ConfigFactory.load()
    val conf: Configuration = new Configuration(configuration)

    val importer = new HistoricalDataImporter(conf)

    //var data = importer.importData(args(0))
    val data = importer.importData("C:\\Users\\sabri.boussetha\\IdeaProjects\\Datalake\\sensors.csv")

    val metadataWriter = new MetadataWriter(conf)
    // Get the Swift ID counter and increase it (use "find_one_and_update")
    val id = metadataWriter.putIntoStatsAndGetSwiftId()

    val dataWriter = new DataWriter(conf)

    val inserted = dataWriter.put("neoCampus", id.toString, Serialization.serialization(data))

    // handle atomic insertion & failure
    inserted match {
      case Success(df) => {
        metadataWriter.putIntoSwiftDB("csv", "test:tester", projectName, id.toString,
          "MongoDB", "default",
          "Historical Real time data coming from CSV file to be inserted in Swift and MongoDB",
          "sensors.csv",null,null,null)
      }
      case Failure(exception) => {
        println(s"Execption Occured while inserting data into data lake. Reseting swift Id : $exception")
        metadataWriter.resetLastSwiftId()
      }
    }
  }
}
