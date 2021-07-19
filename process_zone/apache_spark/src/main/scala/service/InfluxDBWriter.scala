package service

import com.google.gson.Gson
import com.influxdb.client.domain.WritePrecision
import com.influxdb.client.write.Point
import com.influxdb.client.{InfluxDBClient, InfluxDBClientFactory, WriteApi}
import com.typesafe.config.Config
import model.{MessageMultiValues, MessageSingleValue}
import org.apache.log4j.Logger
import org.apache.spark.api.java.JavaRDD
import org.apache.spark.streaming.Time

import java.util
import scala.collection.JavaConverters._
import scala.collection.convert.ImplicitConversions.`collection AsScalaIterable`
import scala.collection.mutable.ListBuffer
import scala.util.{Failure, Success, Try}

class InfluxDBWriter(config: Config) {
  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)
  val influxdbToken: String = config.getString("influxdb.token")
  val influxdbOrg: String = config.getString("influxdb.org")
  val influxdbBucket: String = config.getString("influxdb.bucket")
  val influxdbUrl: String = config.getString("influxdb.url")
  val influxdbMeasurement: String = config.getString("influxdb.measurement")

  val influxClient: InfluxDBClient = InfluxDBClientFactory.create(influxdbUrl, influxdbToken.toCharArray, influxdbOrg)

  val writeApi: WriteApi = influxClient.getWriteApi

  /**
   * get influxdb data points from mqtt
   *
   * @param rdd  : mqtt from spark streaming
   * @param time : time to get the message
   * @return
   */
  def getPoints(rdd: JavaRDD[(String, String)], time: Time): util.List[Point] = {
    // parser mqtt to object
    val msgList = rdd.map(r => {
      val gson = new Gson
      val jsonStr = r._2.slice(0, r._2.length - 1) + s""","topic":"${r._1}"}"""
      if (r._1.contains("/energy")) {
        gson.fromJson(jsonStr, classOf[MessageMultiValues])
      } else {
        gson.fromJson(jsonStr, classOf[MessageSingleValue])
      }
    }).collect.toList

    // create influxdb point list (Point is not serializable in spark)
    val linePoints = new ListBuffer[Point]()
    msgList.foreach {
      case m: MessageMultiValues =>
        if (influxdbMeasurement == "topic") {
          val point = Point.measurement(m.topic)
            .addTag("subID", m.subID)
            .addTag("unitID", m.unitID)
            .time(time.milliseconds, WritePrecision.MS)
          if (m.input != null) {
            point.addTag("input", m.input)
          }
          for (i <- m.value.indices) {
            point.addField(m.value_units(i), m.value(i))
          }
          linePoints += point
        } else {
          for (i <- m.value.indices) {
            val point = Point.measurement(m.value_units(i))
              .addField("value", m.value(i))
              .addTag("topic", m.topic)
              .addTag("subID", m.subID)
              .addTag("unitID", m.unitID)
              .time(time.milliseconds, WritePrecision.MS)
            if (m.input != null) {
              point.addTag("input", m.input)
            }
            linePoints += point
          }
        }

      case m: MessageSingleValue =>
        if (m.value_units != null) {
          if (influxdbMeasurement == "topic") {
            val point = Point.measurement(m.topic)
              .addTag("subID", m.subID)
              .addTag("unitID", m.unitID)
              .addField(m.value_units, m.value)
              .time(time.milliseconds, WritePrecision.MS)
            if (m.input != null) {
              point.addTag("input", m.input)
            }
            linePoints += point
          } else {
            val point = Point.measurement(m.value_units)
              .addTag("topic", m.topic)
              .addTag("subID", m.subID)
              .addTag("unitID", m.unitID)
              .addField("value", m.value)
              .time(time.milliseconds, WritePrecision.MS)
            if (m.input != null) {
              point.addTag("input", m.input)
            }
            linePoints += point
          }
        }
      case _ => null
    }
    linePoints.toList.asJava
  }

  /**
   * insert into influxdb
   *
   * @param points : data points to write into influxdb bucket
   */
  def writePoints(points: util.List[Point]): Unit = {
    if (points.size() > 0) {
      // write into influx
      writeApi.writePoints(influxdbBucket, influxdbOrg, points)
    }
  }

  /**
   * insert mqtt into influxdb
   *
   * @param rdd  : mqtt from spark streaming
   * @param time : time to get the message
   * @return
   */
  def writeMqtt(rdd: JavaRDD[(String, String)], time: Time): Try[util.List[Point]] = {
    try {
      val points = getPoints(rdd, time)
      writePoints(points)
      println((new Gson).toJson(points))
      Success(points)
    } catch {
      case e: Exception =>
        log.error("Error Occurred while inserting mqtt into influxdb: " + e.getMessage)
        Failure(e)
    }
  }
}
