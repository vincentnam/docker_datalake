package config

import com.typesafe.config.Config

class Configuration(config: Config) extends Serializable {
  val mongoHost = config.getString("mongo.host")
  val mongoPort = config.getString("mongo.port")
  val mongoUser = config.getString("mongo.user")
  val mongoPwd = config.getString("mongo.pass")
  val swiftHost = config.getString("swift.host")
  val swiftPort = config.getString("swift.port")
  val swiftUser = config.getString("swift.user")
  val swiftPwd = config.getString("swift.pass")
}
