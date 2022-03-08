import com.typesafe.config.{Config, ConfigFactory}
import jobs.InsertMqttDataJob
import org.apache.spark.SparkConf
import org.apache.spark.sql.{Dataset, Row, SparkSession}
import org.apache.spark.streaming.Durations
import org.apache.spark.streaming.api.java.JavaStreamingContext
import service.StreamGetter
import org.apache.spark.streaming.Seconds

object Main {
  //  System.setProperty("hadoop.home.dir", "C:/hadoop")
  val config: Config = ConfigFactory.load()

  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()

    val sparkConf: SparkConf = new SparkConf()
      .setMaster("local[*]")
      .setAppName("StreamingMQTT")
      .set("spark.driver.allowMultipleContexts", "true")

    val batchDuration = config.getInt("mqtt.batchDuration")
    val jssc = new JavaStreamingContext(sparkConf, Seconds(batchDuration))

    val streamGetter: StreamGetter = new StreamGetter(config)
    val configCollectionStatus: Dataset[Row] = streamGetter.getAllStreams()

    for (configFlux <- configCollectionStatus.rdd.collect()) {
      println(configFlux)

      val thread = new Thread {
        InsertMqttDataJob.start(configFlux, jssc)
      }
      thread.start()
    }
    jssc.start()
    jssc.awaitTermination()
  }

}
