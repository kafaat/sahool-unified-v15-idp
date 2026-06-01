@echo off
title SAHOOL Kong LAN Proxy - 192.168.0.154:8000
echo Starting SAHOOL Kong LAN Proxy...
echo Phone connects to: http://192.168.0.154:8000
echo.
python scripts\kong-lan-proxy.py --lan-ip 192.168.0.154 --port 8000
pause
