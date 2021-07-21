package util

import org.apache.commons.io.output.ByteArrayOutputStream

import java.io.ObjectOutputStream

object Serialization {

  /**
   *
   * @param input
   * @return
   */
  def serialization(input: Any): Array[Byte] = {
    val stream: ByteArrayOutputStream = new ByteArrayOutputStream()
    val outputStream = new ObjectOutputStream(stream)

    outputStream.writeObject(input)
    outputStream.close()

    stream.toByteArray
  }

}
