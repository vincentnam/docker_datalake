package service

import com.typesafe.config.Config
import org.apache.avro.io.Encoder
import org.apache.spark.sql.{Dataset, Row, SparkSession}
import spark.implicits._

import scala.language.postfixOps

class StreamGetter(config: Config) {

  val mongodbUri = s"mongodb://${config.getString("mongo.user")}:${config.getString("mongo.pwd")}@${config.getString("mongo.host")}:${config.getString("mongo.port")}/?authSource=${config.getString("mongo.db.auth")}"

  val spark = SparkSession
    .builder()
    .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse")
    .master("local[*]")
    .getOrCreate()

  def getAllStreams(): Dataset[Row] = {
    val configCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "mqtt", "collection" -> "flux")).load()

    val configCollectionStatus = configCollection.where("status == true")

    return configCollectionStatus
  }

  def changeFlag(): Boolean = {
    val fluxCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
      .options(Map("uri" -> mongodbUri, "database" -> "mqtt", "collection" -> "flux")).load()

    val fluxCollectionStatusTrue = fluxCollection.where("checkUpdate == true")
    var errors = 0
    for (configFlux <- fluxCollectionStatusTrue.rdd.collect()) {
      if (configFlux(9).asInstanceOf[Boolean]) {
        errors += 1
      }
    }
    if (errors > 0) {
      return true
    } else {
      return false
    }
  }

}
