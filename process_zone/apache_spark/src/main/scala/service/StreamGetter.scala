package service

import com.typesafe.config.Config
import org.apache.avro.io.Encoder
import org.apache.spark.sql.catalyst.dsl.expressions.StringToAttributeConversionHelper
import org.apache.spark.sql.catalyst.encoders.RowEncoder
import org.apache.spark.sql.functions.{col, regexp_replace, udf, when}
import org.apache.spark.sql.{Dataset, Row, SparkSession}

import java.util.Base64
//import org.mongodb.scala._

import scala.language.postfixOps

import com.mongodb.spark._

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

    val fluxCollectionStatusTrue = fluxCollection.where(fluxCollection("checkUpdate") === true && fluxCollection("status") === true)
    var nbUpdate = 0
    for (configFlux <- fluxCollectionStatusTrue.rdd.collect()) {
      if (configFlux(2).asInstanceOf[Boolean]) {
        nbUpdate += 1
      }
    }
    if (nbUpdate > 0) {
      val configCollection = spark.read.format("com.mongodb.spark.sql.DefaultSource")
        .options(Map("uri" -> mongodbUri, "database" -> "mqtt", "collection" -> "flux")).load()

      val checkUpdateFalse = udf { (checkUpdate: Boolean) =>
        if (checkUpdate) false else checkUpdate
      }
      configCollection.withColumn("checkUpdate", checkUpdateFalse(configCollection("checkUpdate")))

      val confCol = configCollection.map(row => {
        val row1: Boolean = row(2).asInstanceOf[Boolean]
        val checkUpdate: Boolean = if (row1) false else row1
        Row(row(0), row(1), checkUpdate, row(3), row(4), row(5), row(6), row(7), row(8), row(9))
      })(configCollection.encoder)

      MongoSpark.save(confCol.write.options(Map("uri" -> mongodbUri, "database" -> "mqtt", "collection" -> "flux")).option("replaceDocument", "true").mode("append"))

      return true
    } else {
      return false
    }
  }

}
