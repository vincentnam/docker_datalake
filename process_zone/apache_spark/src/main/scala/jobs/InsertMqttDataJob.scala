package jobs

import com.google.gson.Gson
import com.typesafe.config.{Config, ConfigFactory}
import org.apache.spark.sql.Row
import org.apache.log4j.Logger
import org.apache.spark.streaming.mqtt.MQTTUtils._
import org.eclipse.paho.client.mqttv3.MqttClient
import service.{InfluxDBWriter, MongoWriter, SwiftWriter}
import org.apache.spark.streaming.api.java.JavaStreamingContext

import scala.collection.convert.ImplicitConversions.`list asScalaBuffer`
import scala.util.{Failure, Success}


object InsertMqttDataJob {
  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)
  val config: Config = ConfigFactory.load()

  def start(configFlux: Row, jssc: JavaStreamingContext): Unit = {
    val swiftWriter = new SwiftWriter(config)

    val clientId = MqttClient.generateClientId()
    // ConfigFlux : [_id, brokerUrl, checkUpdate, container_name, description, name, password, status, topic, user ]
    val brokerUrl: String = configFlux(1).asInstanceOf[String]
    val username: String = configFlux(9).asInstanceOf[String]
    val password: String = configFlux(6).asInstanceOf[String]
    val topic: String = configFlux(8).asInstanceOf[String]
    val container_name: String = configFlux(3).asInstanceOf[String]
    println(configFlux)

    val influxDDWriter = new InfluxDBWriter(config, container_name)
    println("brokerUrl: " + brokerUrl)
    println("topic: " + topic)
    val lines = createPairedStream(jssc, brokerUrl, Array(topic), clientId, username, password, cleanSession = true)

    lines.foreachRDD((rdd, time) => {
      val mongoWriter = new MongoWriter(config)
      val data = rdd.map(r => (r._1, r._2)).collect.toList
      println(data)
      if (data.nonEmpty) {
        // insert mqtt into swift
        val inserted_swift_ids = swiftWriter.writeMqtt(data, time, mongoWriter, container_name)

        // insert mqtt into influxDB
        val resInsertInfluxDB = influxDDWriter.writeMqtt(rdd, time)
        resInsertInfluxDB match {
          case Success(points) =>
            // insert operation history into mongodb
            val influxDbPoints = (new Gson).toJson(points)
            mongoWriter.putIntoHistoryDB(time.toString(), container_name,
              config.getString("swift.user"), inserted_swift_ids.mkString(","),
              "mqtt json to influxdb data points",
              data.toString, influxDbPoints)
          case Failure(exception) =>
          //            log.error(s"Insert into InfluxDB Error : $exception")
        }
      }
    })

  }

}
