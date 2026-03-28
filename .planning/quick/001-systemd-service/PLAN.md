<task type="auto">
<name>Create systemd unit for XANDER operator</name>
<files> /etc/systemd/system/xander-operator.service </files>
<action>
Create a systemd service file that runs the operator in loop mode with proper environment variables (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID optional). Enable and start it.
</action>
<verify>
systemctl status xander-operator shows active (running)
</verify>
<done>Service installed, enabled, and running</done>
</task>
