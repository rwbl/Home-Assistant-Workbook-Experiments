B4R=true
Group=Default Group
ModulesStructureVersion=1
Type=StaticCode
Version=4
@EndOfDesignText@
' File:		MQTTMod.bas
' Brief:	MQTT (Message Queue Telemetry Transport) methods.

Private Sub Process_Globals
	'These global variables will be declared once when the application starts.
	'Public variables can be accessed from all modules.

	' Logging flag
	Private LOGGING As Boolean = False

	' Types
	Type TMQTTMessage(topic As String, payload As String)

	' MQTT
	Private MQTT As MqttClient

	Private MQTT_USERNAME As String		= "<USERNAME>"
	Private MQTT_PASSWORD As String		= "<PASSWORD>"
	Private MQTT_BROKER_IP () As Byte 	= Array As Byte(NNN, NNN, NNN, NNN)
	Private MQTT_BROKER_PORT As UInt 	= 1883

	Private MQTT_RETRIES As Byte		= 10
	Private MQTTRetryCounter As Byte	= 0

	Public MQTT_DELAY As ULong			= 500
	Public Connected As Boolean			= False
End Sub


' Initialize module.
' TODO: Consider enhancing with parameter username As String, password As String, ip() As Byte, port As UInt.
Public Sub Initialize(ClientId As String, stream As Stream)
	MQTT.Initialize(stream, MQTT_BROKER_IP, MQTT_BROKER_PORT, ClientId, "MQTT_MessageArrived", "MQTT_Disconnected")
End Sub

#Region MQTT
' Check if connected to mqtt. if not, then try again after 1 sec.
' This sub can not return true or false, because used by callsubplus. Therefor global connected.
' unused - Mandatory parameter as used for the callsubplus retry
Public Sub Connect(tag As Byte)
	Dim mqttopt As MqttConnectOptions
	mqttopt.Initialize(MQTT_USERNAME, MQTT_PASSWORD)

	Connected = MQTT.Connect2(mqttopt)

	If Connected = False Then
		Log(Millis, "[MQTTMod Connect][ERROR] Trying to connect again...Retry #", MQTTRetryCounter)
		MQTTRetryCounter = MQTTRetryCounter + 1
		If MQTTRetryCounter <= MQTT_RETRIES Then
			CallSubPlus("Connect", 10000, 0)
			Return 'False
		Else
			Log(Millis, "[MQTTMod Connect][ERROR] Can not connect to the broker. Retries #", MQTTRetryCounter)
			Return 'False
		End If
	End If
	
	' MQTT connected. Reset the retrycounter
	MQTTRetryCounter = 0
	Log(Millis, "[MQTTMod Connect][OK]")
	Delay(1000)

	Return 'True
End Sub

' MQTT disconnected.
' If the server is nor reachable, then MQTT is disconnected.
' After 5 seconds, retry to connect again.
Private Sub MQTT_Disconnected
	Log(Millis, "[MQTTMod MQTT_Disconnected] MQTT disconnected > start retrying.")
	Connected = False
	MQTT.Close

	' Retry MQTT connection after delay (e.g. 10 seconds)
	CallSubPlus("Connect", 10000, 0)
End Sub

' Handle MQTT Message arrived.
' IMPORTANT: In main the event must be created MQTT_MessageArrived(topic, payload)
Private Sub MQTT_MessageArrived(Topic As String, Payload() As Byte)
	' Log(Millis, "[MQTT_MessageArrived] Topic=", Topic, ", Payload=", Payload)
	Main.MQTT_MessageArrived(Topic, Payload)
End Sub

' Subscribe to the topics publsihed. Ensure to set QoS to 1 and NOT 0.
' topics - Array with topics.
Public Sub Subscribe(topics() As String)
	If Not(Connected) Then
		Log(Millis, "[MQTTMod Subscribe][ERROR] MQTT is not connected.")
		Return
	End If

	' Loop over the topics and add
	For Each Topic As String In topics
		MQTT.Subscribe(Topic, 1)		
	Next
End Sub

' Publish sensor values to the MQTT broker
' messages - Array with messages.
Public Sub Publish(topics() As String, payloads() As String)
	' Leave if not connected
	If Not(Connected) Then
		Log(Millis, "[MQTTMod Publish][ERROR] MQTT is not connected.")
		Return
	End If

	For i = 0 To topics.Length - 1
		If LOGGING Then Log(Millis, "[MQTTMod Publish] message topic=", topics(i), ",payload=", payloads(i))
		PublishChunked(topics(i), payloads(i).GetBytes, True)
		' HINT
		' Publish2 can be used if payload length < 128		
	Next
	'If LOGGING Then Log(Millis, "[MQTTMod Publish] Done")
End Sub

' Remove topics permanent.
' topics - Array with topics.
Public Sub Remove(topics() As String)
	' Leave if not connected
	If Not(Connected) Then
		Log(Millis, "[MQTTMod Remove][ERROR] MQTT is not connected.")
		Return
	End If
	
	' Empty payload to remove the autodiscovery config topic
	Dim b() As Byte = Array As Byte()

	For i = 0 To topics.Length - 1
		If LOGGING Then Log(Millis, "[MQTTMod Publish] message topic=", topics(i))
		MQTT.Publish2(topics(i), b, True)
	Next
	If LOGGING Then Log(Millis, "[MQTTMod Remove] Done")
End Sub

' Sends a large MQTT message in chunks
' Parameters:
'   topic - the topic string (e.g. "homeassistant/sensor/xyz/config")
'   payload() - the payload as a byte array
'   retain - whether to retain the message on the broker
Private Sub PublishChunked(topic As String, payload() As Byte, retain As Boolean)
	Dim length As Int = payload.Length
	Dim result As Boolean
	Dim CHUNK_SIZE As Int = 32
	Dim buffer(CHUNK_SIZE) As Byte

	If LOGGING Then 
		Log(Millis, "[MQTTMod PublishChunked] topic=", topic, ", payload length=", length)
	End If

	If MQTT.BeginPublish(topic, length, retain) = False Then
		Log(Millis, "[MQTTMod PublishChunked][ERROR] BeginPublish failed")
		Return
	End If

	Dim i As Int
	Do While i < length
		Dim remaining As Int = length - i
		Dim thisChunkSize As Int = Min(CHUNK_SIZE, remaining)

		' Copy this chunk into the buffer
		For j = 0 To thisChunkSize - 1
			buffer(j) = payload(i + j)
		Next

		' Create an exact-size array to pass
		Dim actualChunk(thisChunkSize) As Byte
		For j = 0 To thisChunkSize - 1
			actualChunk(j) = buffer(j)
		Next

		result = MQTT.WriteChunk(actualChunk)
		If result = False Then
			Log(Millis, "[MQTTMod PublishChunked][ERROR] WriteChunk failed at offset ", i)
			MQTT.EndPublish
			Return
		End If

		i = i + thisChunkSize
	Loop

	result = MQTT.EndPublish
	If LOGGING Then Log(Millis, "[MQTTMod PublishChunked] result=", result)
End Sub
#End Region
