package jobs

import com.google.gson.Gson
import com.typesafe.config.{Config, ConfigFactory}
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{Dataset, Encoder, Row, SparkSession}
import org.apache.spark.streaming.Durations
import service.StreamGetter
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
  val config: Config = ConfigFactory.load()

  def start(): Unit = {
    val swiftWriter = new SwiftWriter(config)

    val sparkConf: SparkConf = new SparkConf()
      .setMaster("local[*]")
      .setAppName("StreamingMQTT")

    val jssc = new JavaStreamingContext(sparkConf, Durations.seconds(2))
    val clientId = MqttClient.generateClientId()

    val streamGetter : StreamGetter = new StreamGetter(config)
    val configCollectionStatus : Dataset[Row] = streamGetter.getAllStreams()

    for(configFlux <- configCollectionStatus.rdd.collect()){

      // ConfigFlux : [_id, batchDuration, brokerUrl, container_name, description, name, password, status, topic, user ]
      val brokerUrl: String = configFlux(2).asInstanceOf[String]
      val username: String = configFlux(9).asInstanceOf[String]
      val password: String = configFlux(6).asInstanceOf[String]
      val topic: String = configFlux(8).asInstanceOf[String]
      val batchDuration: Long = configFlux(1).asInstanceOf[Integer].longValue()
      val container_name: String = configFlux(3).asInstanceOf[String]

      val influxDDWriter = new InfluxDBWriter(config, container_name)
      println("brokerUrl: " + brokerUrl)
      println("topic: " + topic)
      val lines = MQTTUtils.createPairedStream(jssc, brokerUrl, Array(topic), clientId, username, password, cleanSession = true)

      lines.foreachRDD((rdd, time) => {
        val mongoWriter = new MongoWriter(config)
        val data = rdd.map(r => (r._1, r._2)).collect.toList
        if (data.nonEmpty) {
          println("raw data: " + data)
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
}
