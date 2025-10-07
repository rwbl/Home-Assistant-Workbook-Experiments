﻿B4R=true
Group=Default Group
ModulesStructureVersion=1
Type=StaticCode
Version=4
@EndOfDesignText@
' File:		WiFiMod.bas
' Brief:	WiFi methods.
' Notes:
' There is a 15 seconds timeout in the synchronous Connect methods. This is implemented in the library code (rESP8266WiFi.cpp - line 33 - 41)
' There is no similar timeout in the async method. It simply polls the connection state.

Private Sub Process_Globals
	'These global variables will be declared once when the application starts.
	'Public variables can be accessed from all modules.

	' WiFi
	Private SSID As String		= "<SSID>"
	Private Password As String	= "<PASSWORD>"
	Private WiFi As ESP8266WiFi
	
	' Public vars
	Public Connected As Boolean	= False
	Public Client As WiFiSocket
End Sub

' Connect to the WiFi network
' Return Boolean
' Retval True connected
' Retval False connection failed
Public Sub Connect As Boolean
	If WiFi.Connect2(SSID, Password) Then
		Log("[WiFiMod.Connect][I] OK, ip=", WiFi.LocalIp)
		Return True
	Else
		Log("[WiFiMod.Connect][E] Can not connect to the network.")
		Return False
	End If
End Sub


