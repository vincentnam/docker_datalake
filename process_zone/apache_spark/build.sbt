name := "Datalake"

version := "0.1"

scalaVersion := "2.12.16"

// https://mvnrepository.com/artifact/org.apache.spark/spark-core
libraryDependencies += "org.apache.spark" % "spark-core_2.12" % "3.3.0" // % "provided"

// https://mvnrepository.com/artifact/org.apache.spark/spark-sql
libraryDependencies += "org.apache.spark" % "spark-sql_2.12" % "3.3.0" // % "provided"

// https://mvnrepository.com/artifact/org.mongodb.spark/mongo-spark-connector
libraryDependencies += ("org.mongodb.spark" % "mongo-spark-connector_2.12" % "3.0.2")

// https://mvnrepository.com/artifact/org.javaswift/joss
libraryDependencies += "org.javaswift" % "joss" % "0.10.4"

// https://mvnrepository.com/artifact/commons-io/commons-io
libraryDependencies += "commons-io" % "commons-io" % "2.11.0"

// https://mvnrepository.com/artifact/org.scala-lang/scala-reflect
libraryDependencies += "org.scala-lang" % "scala-reflect" % "2.12.16"

// https://mvnrepository.com/artifact/com.google.code.gson/gson
libraryDependencies += "com.google.code.gson" % "gson" % "2.9.0"

// https://mvnrepository.com/artifact/com.typesafe/config
libraryDependencies += "com.typesafe" % "config" % "1.4.2"

// https://mvnrepository.com/artifact/org.apache.spark/spark-streaming
libraryDependencies += "org.apache.spark" % "spark-streaming_2.12" % "3.3.0" // % "provided"

// https://mvnrepository.com/artifact/org.apache.bahir/spark-streaming-mqtt
libraryDependencies += "org.apache.bahir" % "spark-streaming-mqtt_2.12" % "2.4.0"

// https://mvnrepository.com/artifact/com.influxdb/influxdb-client-scala
libraryDependencies += "com.influxdb" % "influxdb-client-scala_2.12" % "6.3.0"