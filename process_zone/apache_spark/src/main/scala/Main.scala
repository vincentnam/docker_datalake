import com.typesafe.config.{Config, ConfigFactory}
import jobs.InsertMqttDataJob
import org.apache.spark.sql.{Row, SparkSession}

object Main {
  //  System.setProperty("hadoop.home.dir", "C:/hadoop")

  def main(args: Array[String]): Unit = {
    //    InsertHistoricalDataJob.start()

    InsertMqttDataJob.start()


  }
}
