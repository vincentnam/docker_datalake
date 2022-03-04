package service

import com.typesafe.config.Config
import org.apache.spark.sql.{Dataset, Row, SparkSession}

class StreamGetter(config: Config) {

  val mongodbUri = s"mongodb://${config.getString("mongo.host")}:${config.getString("mongo.port")}/"

  val spark = SparkSession
    .builder()
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse")
    .master("local[*]")
    .getOrCreate()

}
