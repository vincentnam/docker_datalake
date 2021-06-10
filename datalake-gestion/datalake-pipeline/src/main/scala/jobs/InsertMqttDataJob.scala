package jobs

import com.typesafe.config.{Config, ConfigFactory}
import org.apache.log4j.Logger
import org.apache.spark.SparkConf
import org.apache.spark.streaming.Seconds
import org.apache.spark.streaming.api.java.JavaStreamingContext
import org.apache.spark.streaming.mqtt.MQTTUtils
import org.eclipse.paho.client.mqttv3.MqttClient
import service.{MetadataWriter, SwiftWriter}

import scala.util.{Failure, Success}


object InsertMqttDataJob {
  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val projectName = "neOCampus"

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
    val lines = MQTTUtils.createStream(jssc, brokerUrl, topic, clientId, username, password, cleanSession = true)

    lines.foreachRDD((rdd, time) => {
      val data = rdd.collect()
      if (data.size() > 0) {
        // println(data.toString)
        // Get the Swift ID counter and increase it
        val metadataWriter = new MetadataWriter(config)
        val id = metadataWriter.putIntoStatsAndGetSwiftId()
        val contentType = "application/json"
        val inserted = swiftWriter.put(projectName, id.toString, data.toString, contentType)

        // handle atomic insertion & failure
        inserted match {
          case Success(df) =>
            metadataWriter.putIntoSwiftDB(contentType, config.getString("swift.user"), projectName, id.toString,
              "Swift", "default",
              s"Insert MQTT into Swift, topic: ${topic}",
              s"mqtt_${time.toString().replace(' ', '_')}.json", null, null, null)
          // println(data.toString)
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
