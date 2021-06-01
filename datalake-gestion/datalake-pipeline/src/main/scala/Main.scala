import jobs.InsertMqttDataJob

object Main {

//  System.setProperty("hadoop.home.dir", "C:/hadoop")

  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()
    val test_mqtt_topic = "u4/#"
    InsertMqttDataJob.start(test_mqtt_topic)
  }
}
