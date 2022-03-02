import com.typesafe.config.{Config, ConfigFactory}
import jobs.InsertMqttDataJob
import org.apache.spark.sql.SparkSession

object Main {
  //  System.setProperty("hadoop.home.dir", "C:/hadoop")
  val config: Config = ConfigFactory.load()
  val spark = SparkSession
    .builder()
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse")
    .master("local[*]")
    .getOrCreate()

  val mongodbUri = s"mongodb://${config.getString("mongo.host")}:${config.getString("mongo.port")}/"

  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()
    val configCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "mqtt", "collection" -> "flux")).load()

    val collection = configCollection.collect().toList
    collection = collection.filter(_.status==true)
    for (configFlux <- collection) {
      InsertMqttDataJob.start(configFlux)
    }

  }
}
