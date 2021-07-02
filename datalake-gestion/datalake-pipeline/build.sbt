name := "Datalake"

version := "0.1"

scalaVersion := "2.12.10"

// https://mvnrepository.com/artifact/org.apache.spark/spark-core
libraryDependencies += "org.apache.spark" %% "spark-core" % "3.1.0" // % "provided"

// https://mvnrepository.com/artifact/org.apache.spark/spark-sql
libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.1.0" // % "provided"

// https://mvnrepository.com/artifact/org.mongodb.spark/mongo-spark-connector
libraryDependencies += "org.mongodb.spark" %% "mongo-spark-connector" % "3.0.1"

// https://mvnrepository.com/artifact/org.javaswift/joss
libraryDependencies += "org.javaswift" % "joss" % "0.10.4"

// https://mvnrepository.com/artifact/commons-io/commons-io
libraryDependencies += "commons-io" % "commons-io" % "2.8.0"

libraryDependencies += "org.scala-lang" % "scala-reflect" % "2.12.8"

// https://mvnrepository.com/artifact/com.google.code.gson/gson
libraryDependencies += "com.google.code.gson" % "gson" % "2.8.6"

libraryDependencies += "com.typesafe" % "config" % "1.4.1"

// https://mvnrepository.com/artifact/org.apache.spark/spark-streaming
libraryDependencies += "org.apache.spark" %% "spark-streaming" % "3.1.1" // % "provided"

// https://mvnrepository.com/artifact/org.apache.bahir/spark-streaming-mqtt
libraryDependencies += "org.apache.bahir" %% "spark-streaming-mqtt" % "2.4.0"

// https://mvnrepository.com/artifact/com.influxdb/influxdb-client-scala
libraryDependencies += "com.influxdb" %% "influxdb-client-scala" % "2.3.0"
