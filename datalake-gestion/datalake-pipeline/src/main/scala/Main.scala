import jobs.InsertMqttDataJob

object Main {

//  System.setProperty("hadoop.home.dir", "C:/hadoop")

  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()
    InsertMqttDataJob.start()
  }
}
