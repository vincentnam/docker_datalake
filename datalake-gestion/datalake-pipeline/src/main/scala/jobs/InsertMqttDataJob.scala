package jobs

import com.typesafe.config.{Config, ConfigFactory}
import org.apache.log4j.Logger
import org.apache.spark.SparkConf
import org.apache.spark.streaming.Seconds
import org.apache.spark.streaming.api.java.JavaStreamingContext
import org.apache.spark.streaming.mqtt.MQTTUtils
import org.eclipse.paho.client.mqttv3.MqttClient
import service.{MetadataWriter, SwiftWriter, InfluxDBWriter}

import scala.util.{Failure, Success}


object InsertMqttDataJob {
  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)

  def start(topic: String): Unit = {
    val config: Config = ConfigFactory.load()
    val swiftWriter = new SwiftWriter(config)

    val brokerUrl = config.getString("mqtt.brokerUrl")
    val username = config.getString("mqtt.username")
    val password = config.getString("mqtt.password")
    val batchDuration = config.getInt("mqtt.batchDuration")

    val sparkConf: SparkConf = new SparkConf().setMaster("local[*]").setAppName("StreamingMQTT")
    val jssc = new JavaStreamingContext(sparkConf, Seconds(batchDuration))
    val clientId = MqttClient.generateClientId()
    println("brokerUrl: " + brokerUrl)
    println("topic: " + topic)
    val lines = MQTTUtils.createPairedStream(jssc, brokerUrl, Array(topic), clientId, username, password, cleanSession = true)

    lines.foreachRDD((rdd, time) => {
      val data = rdd.map(r => r._2).collect
      if (data.size() > 0) {
        // println(data.toString)
        // Get the Swift ID counter and increase it
        val metadataWriter = new MetadataWriter(config)
        val id = metadataWriter.putIntoStatsAndGetSwiftId()
        val contentType = "application/json"
        val swiftContainer = config.getString("swift.container")
        val inserted = swiftWriter.put(swiftContainer, id.toString, data.toString, contentType)

        // handle atomic insertion & failure
        inserted match {
          case Success(_) =>
            // insert metadata into mongoDB
            metadataWriter.putIntoSwiftDB(contentType, config.getString("swift.user"), swiftContainer, id.toString,
              "Swift", "default",
              s"Insert MQTT into Swift, topic: ${topic}",
              s"mqtt_${time.toString().replace(' ', '_')}.json")

            // insert mqtt into influxDB
            val influxDDWriter = new InfluxDBWriter(config)
            influxDDWriter.writeMqtt(rdd, time)

            println("swift object id: " + id.toString)
            println(data.toString)
          case Failure(exception) =>
            log.error(s"Execption Occured while inserting data into data lake. Reseting swift Id : $exception")
            metadataWriter.resetLastSwiftId()
        }

      }
    })

    jssc.start()
    jssc.awaitTermination()
  }
}
