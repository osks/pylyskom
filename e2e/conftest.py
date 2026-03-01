import socket

import pytest


client_name = "pylyskom-e2e"
client_version = "1.0"
username = "pylyskom-e2e"
hostname = socket.getfqdn()
user = username + "%" + hostname
host = "localhost"
port = 4894
person_name = "E2E Test User"
person_password = "testpass123"
