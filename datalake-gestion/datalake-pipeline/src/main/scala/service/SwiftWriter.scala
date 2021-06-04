package service

import com.typesafe.config.Config
import org.apache.log4j.Logger
import org.javaswift.joss.client.factory.{AccountFactory, AuthenticationMethod}
import org.javaswift.joss.model.{Account, StoredObject}

import java.io.ByteArrayInputStream
import scala.util.{Failure, Success, Try}

class SwiftWriter(conf: Config) {
  @transient lazy val log: Logger = org.apache.log4j.LogManager.getLogger(getClass.getName)

  val swiftAccount: Account = new AccountFactory()
    .setAuthenticationMethod(AuthenticationMethod.BASIC)
    .setUsername(conf.getString("swift.user"))
    .setPassword(conf.getString("swift.pass"))
    .setAuthUrl(conf.getString("swift.authUrl"))
    .createAccount()


  def put(containerName: String, id: String, text: String, contentType: String): Try[StoredObject] = {
    log.info(s"Inserting object into Openstack Swift Container: $containerName")

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
      Success(obj)
    } catch {
      case e: Exception =>
        log.error("Error Occurred while inserting object to Openstack Swift")
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
}
