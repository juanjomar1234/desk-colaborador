#!/usr/bin/env python3
import sys
import os

print("Content-Type: text/html\n")
print("""
<!DOCTYPE html>
<html>
<head>
    <title>Debug Info</title>
</head>
<body>
    <h1>Python Debug Info</h1>
    <pre>
""")

print("Python Version:", sys.version)
print("\nPython Path:", sys.path)
print("\nEnvironment Variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

print("""
    </pre>
</body>
</html>
""") 