package service

import com.typesafe.config.Config
//import org.apache.log4j.Logger
import org.apache.spark.streaming.Time
import org.javaswift.joss.client.factory.{AccountFactory, AuthenticationMethod, AccountConfig}
import org.javaswift.joss.model.{Account, StoredObject}

import java.io.ByteArrayInputStream
import scala.collection.mutable.ListBuffer
import scala.jdk.CollectionConverters.mapAsJavaMapConverter
import scala.util.{Failure, Success, Try}

class SwiftWriter(config: Config) {
//  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val configAccount = new AccountConfig()
  configAccount.setUsername(config.getString("swift.user"))
  configAccount.setPassword(config.getString("swift.pass"))
  configAccount.setAuthUrl(config.getString("swift.authUrl"))
  //configAccount.setDisableSslValidation(true)

  val swiftAccount: Account = new AccountFactory(configAccount)
    .setAuthenticationMethod(AuthenticationMethod.BASIC)
    .createAccount()

  def put(containerName: String, id: String, text: String, contentType: String): Try[StoredObject] = {
    // log.info(s"Inserting object into Openstack Swift Container: $containerName")

    // get or create container
    val container = swiftAccount.getContainer(containerName)
    if (!container.exists()) {
      container.create()
    }

    // convert string to byte array
    val inputStream = new ByteArrayInputStream(text.getBytes("UTF-8"))
    val obj = container.getObject(id)

    try {
      // upload object to swift
      obj.uploadObject(inputStream)
      obj.setContentType(contentType)
      val metadata: Map[String, AnyRef] = Map("source" -> "mqtt")
      obj.setMetadata(metadata.asJava)
      Success(obj)
    } catch {
      case e: Exception =>
//        log.error("Error Occurred while inserting object to Openstack Swift: " + e)
        Failure(e)
    }
  }

  /**
   * get swift object
   *
   * @param containerName swift container name
   * @param id            swift object id
   * @return swift object
   */
  def get(containerName: String, id: String): StoredObject = {
    val container = swiftAccount.getContainer(containerName)
    val obj = container.getObject(id)

    obj
  }

  def writeMqtt(data: List[(String, String)], time: Time, mongoWriter: MongoWriter, swiftContainer: String): ListBuffer[String] = {
    val swift_object_ids = new ListBuffer[String]()
    data.foreach(r => {
      val topic = r._1
      val message = r._2
      val id = mongoWriter.putIntoStatsAndGetSwiftId()
      val contentType = "application/json"
      val inserted = put(swiftContainer, id.toString, message, contentType)
      // handle atomic insertion & failure
      inserted match {
        case Success(_) =>
          // insert metadata into mongoDB
          mongoWriter.putIntoSwiftDB(contentType, config.getString("swift.user"), swiftContainer, id.toString,
            "Swift", "default",
            s"Insert MQTT into Swift, topic: ${topic}",
            s"mqtt_${topic.replace('/', '_')}_${time.milliseconds}.json",
            topic
          )
          swift_object_ids += id.toString
        case Failure(exception) =>
//          log.error(s"Execption Occured while inserting data into data lake. Reseting swift Id : $exception")
          mongoWriter.resetLastSwiftId()
      }
    })
    swift_object_ids
  }
}
