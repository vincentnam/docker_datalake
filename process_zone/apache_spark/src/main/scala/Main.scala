import com.typesafe.config.{Config, ConfigFactory}
import jobs.InsertMqttDataJob
import org.apache.spark.SparkConf
import org.apache.spark.streaming.api.java.JavaStreamingContext
import service.StreamGetter
import org.apache.spark.streaming.Seconds


object Main {
  //  System.setProperty("hadoop.home.dir", "C:/hadoop")
  val config: Config = ConfigFactory.load()


  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()

    val sparkConf = new SparkConf()
      .setMaster("local[*]")
      .setAppName("StreamingMQTT")
      .set("spark.driver.allowMultipleContexts", "true")

    val batchDuration = config.getInt("mqtt.batchDuration")

    val t = new java.util.Timer()
    val task = new java.util.TimerTask {

      def run() = {
        val jssc = new JavaStreamingContext(sparkConf, Seconds(batchDuration))
        val streamGetter = new StreamGetter(config)
        val configCollectionStatus = streamGetter.getAllStreams()
        println(configCollectionStatus)
        for (configFlux <- configCollectionStatus.rdd.collect()) {
          val thread = new Thread {
            InsertMqttDataJob.start(configFlux, jssc)
          }
          thread.start()
        }
        jssc.start()
        jssc.awaitTerminationOrTimeout(config.getLong("jssc.timeout"))
        jssc.stop(stopSparkContext = true)
      }
    }
    t.scheduleAtFixedRate(task, 0, config.getLong("time.periode"))
  }
}
