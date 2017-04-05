import struct
import json
msg = json.dumps("Alon")
m = struct.pack("i", len(msg))

print m