<div align="center">

<img src="lan_broadcaster/images/logo.svg" alt="LAN Broadcaster Logo" width="200">
<h1>LAN Broadcaster</h1>

</div>

### A quick and easy way to send broadcast messages in your LAN. Uses the Windows "msg" function.

Note: You may need to enable Remote Procedure Call (RPC) on the client's machine for this to work over your LAN. **PLEASE DO SO AT YOUR OWN RISK.**

This setting can be found at HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server, then AllowRemoteRPC. This value is default to 0 and needs to be 1 for RPC to be enabled. (Can all be done through regedit). Again there are risks to enabling this setting.

More extensive testing currently being done.

---