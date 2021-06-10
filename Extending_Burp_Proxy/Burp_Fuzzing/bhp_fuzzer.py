#!/bin/python3
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator

from java.util import List, ArrayList

import random

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        callbacks.registerIntruderPayloadGeneratorFactory(self)

        return

    def getGeneratorName(self):
        return "BHP Payload Generator"

    def createNewInstance(self, attack):
        return BHPFuzzer(self, attack)

class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 1000
        self.num_iterations = 0

        return

    def hasMorePayloads(self):
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True

    def getNextPayload(self, current_payload):
        # Converting to String
        payload = "".join(chr(x) for x in current_payload)

        # Call simple mutator to fuzz the POST
        payload = self.mutate_paylod(payload)

        # Increase number of iteration
        self.num_iterations += 1

        return payload

    def reset(self):
        self.num_iterations = 0
        return

    def mutate_payload(self, original_payload):
        picker = random.randint(1,3)

        # Select a random offset
        offset = random.randint(0, len(original_payload) - 1)
        payload = original_payload[:offset]

        # SQL Injection Attempt
        if picker == 1:
            payload += "'"

        # XSS Attempt
        if picker == 2:
            payload += "<script>alert('BHP!');</script>"

        # Repeat a chunk of original payload
        if picker == 3:
            chunk_length = random.randint(len(payload[offset:]), len(payload) - 1)
            repeater = random.randint(1, 10)

            for i in range(repeater):
                payload += original_payload[offset: offset + chunk_length]

        # Remaining Payload
        payload += original_payload[offset:]

        return payload