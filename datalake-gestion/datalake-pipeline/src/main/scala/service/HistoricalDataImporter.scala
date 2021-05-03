package service

import model.Sensor
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{Row, SparkSession}

object HistoricalDataImporter {

  val spark = SparkSession
    .builder.appName("test")
    .master ("local[*]")
    .getOrCreate()



  import spark.implicits._

  /**
   *
   * @param path
   * @return
   */
  def importData(path: String): RDD[Row] = {
    val inputCSV = spark
      .read
      .format("csv")
      .option("header", "true")
      .load(path)
      .rdd

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

  def insertData: Unit = {

  }

  def insertMetadata: Unit = {

  }
}
