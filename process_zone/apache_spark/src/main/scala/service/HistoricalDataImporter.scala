package service

import config.Configuration
import model.Sensor
import org.apache.spark.sql.{DataFrame, Row, SparkSession}

class HistoricalDataImporter(conf: Configuration) {

//  @transient lazy val log = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val spark = SparkSession
    .builder
    .master ("local[*]") // To change on cluster mode
    .getOrCreate()

  import spark.implicits._

  /**
   *
   * @return
   */
  def importData(): DataFrame = {
//    log.info("Importing csv file")

    val inputCSV = spark
      .read
      .format("csv")
      .option("header", "true")
      .load(conf.csvPath)

    inputCSV
  }

  /**
   *
   * @param row
   * @return
   */
  def toSensor(row: Row): Sensor = {
    Sensor(
      row.getAs[String]("_id"),
      row.getAs[String]("measuretime"),
      row.getAs[String]("topic"),
      row.getAs[String]("payload.value"),
      row.getAs[String]("payload.value_units"),
      row.getAs[String]("payload.input"),
      row.getAs[String]("payload.subID"),
      row.getAs[String]("payload.unitID"),
    )
  }
}
