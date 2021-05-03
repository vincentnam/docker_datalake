package service

import org.javaswift.joss.client.factory.{AccountFactory, AuthenticationMethod}

import java.io.ByteArrayInputStream

object DataWriter {
  val account = new AccountFactory()
    .setAuthenticationMethod(AuthenticationMethod.BASIC)
    .setUsername("test:tester")
    .setPassword("testing")
    .setAuthUrl("http://10.200.156.252:8080/auth/v1.0")
    .createAccount()
  println(account.list().size())

  /**
   *
   * @param containerName
   * @param id id to get from Mongo
   * @param blob data to be stored
   */
  def put(containerName: String, id: String, blob: Array[Byte]) = {
    // get or create container
    val container = account.getContainer(containerName)
    if(!container.exists()) {
      container.create()
    }

    val inputStream = new ByteArrayInputStream(blob)
    val obj = container.getObject(id)

    obj.uploadObject(inputStream)
  }

  def get(containerName: String, id: String) = {
    val container = account.getContainer(containerName)
    val obj = container.getObject(id)

    obj
  }
}
