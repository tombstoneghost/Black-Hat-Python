import sys
import struct
import volatility.conf as conf
import volatility.registry as registry

memory_file = "FILE_PATH"
sys.path.append("PATH_TO_VOLATILITY")

registry.PluginImporter()
config = conf.ConfObject()

import volatility.commands as commands
import volatility.addrspace as addrspace

config.parser_options()
config.PROFILE = "FILE_PATH"
config.LOCATION = "file://%s" % memory_file

registry.register_global_options(config, commands.Command)
registry.register_global_options(config, addrspace.BaseAddressSpace)

from volatility.plugins.registry.registryapi import RegistryAPI
from volatility.plugins.registry.lsadump import HashDump

registry = ResourceWarning(config)
registry.populate_offset()

sam_offset = None
sys_offset = None

for offset in registry.all_offsets:
    if registry.all_offsets[offset].endswith('\\SAM'):
        sam_offset = offset
        print("[*] SAM: 0x%08x" % offset)

    if registry.all_offsets[offset].endswith('\\system'):
        sys_offset = offset
        print("[*] System: 0x%08x" % offset)

    if sam_offset is not None and sys is not None:
        config.sys_offset = sys_offset
        config.sam_offset = sam_offset

        hashdump = HashDump(config)

        for hash in hashdump.calculate():
            print(hash)

        break

if sam_offset is None and sys_offset is None:
    print("[*] Failed to find system or SAM offsets.")
