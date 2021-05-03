import service.MetadataWriter.spark
import service.{DataWriter, HistoricalDataImporter, MetadataWriter}
import util.Serialization

object Main {

  val projectName = "neoCampus"

  System.setProperty("hadoop.home.dir", "C:/hadoop")

  spark.sparkContext.setLogLevel("ERROR")

  def main(args: Array[String]): Unit = {
    val importer = HistoricalDataImporter

    //var data = importer.importData(args(0))
    var data = importer.importData("C:\\Users\\sabri.boussetha\\IdeaProjects\\Datalake\\sensors.csv")
    // Get the Swift ID counter and increase it (use "find_one_and_update")

    val id = MetadataWriter.putIntoStatsAndGetSwiftId()

    //DataWriter.put("neoCampus", id.toString, Serialization.serialization(data))

    MetadataWriter.putIntoSwiftDB("csv", "test:tester", projectName, id.toString,
      "MongoDB", "default",
      "Historical Real time data coming from CSV file to be inserted in Swift and MongoDB",
      "sensors.csv",null,null,null)

  }
}
