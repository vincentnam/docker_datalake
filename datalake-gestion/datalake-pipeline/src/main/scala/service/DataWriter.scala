package service

import config.Configuration
import org.javaswift.joss.client.factory.{AccountFactory, AuthenticationMethod}
import org.javaswift.joss.model.StoredObject

import java.io.ByteArrayInputStream
import scala.util.{Failure, Success, Try}

class DataWriter(conf: Configuration) {
  @transient lazy val log = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val account = new AccountFactory()
    .setAuthenticationMethod(AuthenticationMethod.BASIC)
    .setUsername(conf.swiftUser)
    .setPassword(conf.swiftPwd)
    .setAuthUrl("http://"+ conf.swiftHost +":"+ conf.swiftPort + "/auth/v1.0")
    .createAccount()

  /**
   *
   * @param containerName
   * @param id id to get from Mongo
   * @param blob data to be stored
   */
  def put(containerName: String, id: String, blob: Array[Byte]): Try[StoredObject] = {
    log.info(s"Writing into Openstack Swift container $containerName")

    // get or create container
    val container = account.getContainer(containerName)
    if(!container.exists()) {
      container.create()
    }

    val inputStream = new ByteArrayInputStream(blob)
    val obj = container.getObject(id)

    try {
      obj.uploadObject(inputStream)
      Success(obj)
    } catch {
      case e: Exception => {
        log.error("Error Occurred while inserting object to Openstack Swift")
        Failure(e)
      }
    }
  }

  /**
   *
   * @param containerName
   * @param id
   * @return
   */
  def get(containerName: String, id: String) = {
    val container = account.getContainer(containerName)
    val obj = container.getObject(id)

    obj
  }
}
