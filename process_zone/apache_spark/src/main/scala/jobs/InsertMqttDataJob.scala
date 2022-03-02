package jobs

import com.google.gson.Gson
import com.typesafe.config.{Config, ConfigFactory}
import org.apache.spark.sql.Row
//import org.apache.log4j.Logger
import org.apache.spark.SparkConf
import org.apache.spark.streaming.Seconds
import org.apache.spark.streaming.api.java.JavaStreamingContext
import org.apache.spark.streaming.mqtt.MQTTUtils
import org.eclipse.paho.client.mqttv3.MqttClient
import service.{InfluxDBWriter, MongoWriter, SwiftWriter}

import scala.collection.convert.ImplicitConversions.`list asScalaBuffer`
import scala.util.{Failure, Success}


object InsertMqttDataJob {
  //  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)

  def start(configFlux: Object): Unit = {
    val config: Config = ConfigFactory.load()
    val swiftWriter = new SwiftWriter(config)
    val influxDDWriter = new InfluxDBWriter(config)

    val brokerUrl = configFlux.brokerUrl
    val username = configFlux.user
    val password = configFlux.password
    val topic = configFlux.topic
    val batchDuration = configFlux.batchDuration

    val sparkConf: SparkConf = new SparkConf().setMaster("local[*]").setAppName("StreamingMQTT")
    val jssc = new JavaStreamingContext(sparkConf, Seconds(batchDuration))
    val clientId = MqttClient.generateClientId()
    println("brokerUrl: " + brokerUrl)
    println("topic: " + topic)
    val lines = MQTTUtils.createPairedStream(jssc, brokerUrl, Array(topic), clientId, username, password, cleanSession = true)

    lines.foreachRDD((rdd, time) => {
      val mongoWriter = new MongoWriter(config)
      val data = rdd.map(r => (r._1, r._2)).collect.toList
      if (data.nonEmpty) {
        println("raw data: " + data)
        // insert mqtt into swift
        val inserted_swift_ids = swiftWriter.writeMqtt(data, time, mongoWriter)

        // insert mqtt into influxDB
        val resInsertInfluxDB = influxDDWriter.writeMqtt(rdd, time)
        resInsertInfluxDB match {
          case Success(points) =>
            // insert operation history into mongodb
            val influxDbPoints = (new Gson).toJson(points)
            mongoWriter.putIntoHistoryDB(time.toString(), config.getString("swift.container"),
              config.getString("swift.user"), inserted_swift_ids.mkString(","),
              "mqtt json to influxdb data points",
              data.toString, influxDbPoints)
            println("new influxDB data points: " + influxDbPoints)
          case Failure(exception) =>
//            log.error(s"Insert into InfluxDB Error : $exception")
        }
      }
    })

    jssc.start()
    jssc.awaitTermination()
  }
}
