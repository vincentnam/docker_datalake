package model


case class MessageSingleValue(topic: String,
                              value: Double,
                              value_units: String,
                              input: String,
                              subID: String,
                              unitID: String)

case class MessageMultiValues(topic: String,
                              value: Array[Double],
                              value_units: Array[String],
                              input: String,
                              subID: String,
                              unitID: String)
