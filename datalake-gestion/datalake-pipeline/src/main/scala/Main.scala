import jobs.InsertHistoricalDataJob

object Main {

  System.setProperty("hadoop.home.dir", "C:/hadoop")

  def main(args: Array[String]): Unit = {
    InsertHistoricalDataJob.insert()
  }
}
