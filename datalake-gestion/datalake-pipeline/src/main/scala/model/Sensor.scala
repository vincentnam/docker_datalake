package model

case class Sensor(
                   id: String,
                   measuretime: String,
                   topic: String,
                   payloadValue: String,
                   payloadValueUnits: String,
                   payloadInput: String,
                   payloadSubId: String,
                   payloadUnitId: String
                 )
