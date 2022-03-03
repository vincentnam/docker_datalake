import com.typesafe.config.{Config, ConfigFactory}
import jobs.InsertMqttDataJob
import org.apache.spark.sql.{Row, SparkSession}

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

    val configCollectionStatus = configCollection.where("status == true")

    for (configFlux <- configCollectionStatus) {
      InsertMqttDataJob.start(configFlux)
    }

  }
}
