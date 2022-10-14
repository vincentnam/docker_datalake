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

    do {
      var jssc = new JavaStreamingContext(sparkConf, Seconds(batchDuration))
      var streamGetter = new StreamGetter(config)
      val configCollectionStatus = streamGetter.getAllStreams
      println(configCollectionStatus)

      var checkUpdate = streamGetter.changeFlag()

      while (!checkUpdate) {
        for (configFlux <- configCollectionStatus.rdd.collect()) {
          val thread = new Thread {
            InsertMqttDataJob.start(configFlux, jssc)
          }
          thread.start()
        }
        jssc.start()
        println("start")
        jssc.awaitTerminationOrTimeout(config.getLong("jssc.timeout"))
        println("after await")
        checkUpdate = streamGetter.changeFlag()
        println(checkUpdate)
        if (!checkUpdate) {
          jssc.stop(stopSparkContext = false)
          println("stop")
        }
      }
      if(checkUpdate){
        jssc.stop(stopSparkContext = true)
      }
      println("test")
    } while (true)
  }
}
