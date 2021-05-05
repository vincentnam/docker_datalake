package config

import com.typesafe.config.Config
import org.apache.spark.sql.SparkSession

class Configuration(config: Config) extends Serializable {
  val mongoHost = config.getString("mongo.host")
  val mongoPort = config.getString("mongo.port")
  val mongoUser = config.getString("mongo.user")
  val mongoPwd = config.getString("mongo.pass")
  val swiftHost = config.getString("swift.host")
  val swiftPort = config.getString("swift.port")
  val swiftUser = config.getString("swift.user")
  val swiftPwd = config.getString("swift.pass")
  val csvPath = config.getString("data.path")

  val appName = config.getString("app.name")

  val spark = SparkSession
    .builder.appName(appName)
    .master ("local[*]")
    .getOrCreate()

  spark.sparkContext.setLogLevel("INFO")
}
