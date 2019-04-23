#!/usr/bin/env python

from __future__ import print_function

import logging

__version__ = "0.1"

class GCodeParser(object):
    def __init__(self, infile, axis_limits):
        self.infile = infile
        self.logger = logging.getLogger("GCodeParser")
        self.limits = axis_limits
        self.valid_g_codes = {
            "00": "Rapid positioning",
            "01": "Linear interpolation",
            "28": "Return to home position"
        }
        self.instructions = self.read_gfile()
        
    def read_gfile(self):
        commands = []
        self.logger.info("Checking validity of g-code file.")
        with open(self.infile) as inf:
            for i, line in enumerate(inf):
                if line.startswith("%"):
                    continue
                code_blocks = []
                elements = line.rstrip().split(" ")
                for ele in elements:
                    prefix = ele[0]
                    val = ele[1:]
                    code_blocks.append((prefix, val))
                response_code, msg = self.validate(code_blocks)
                if response_code == 200:
                    commands.append(code_blocks)
                else:
                    raise ValueError("Invalid Instruction in line {} of {}:\n ---> {}".format(i+1, self.infile, msg))
        self.logger.info("Loaded {} instructions".format(len(commands)))
        return commands
                
    def validate(self, code_blocks):
        for (prefix, val) in code_blocks:
            if prefix == "N":
                val = int(val)
                if val < 0:
                    return (100, "N value below zero")
            elif prefix == "G":
                if val not in self.valid_g_codes:
                    return (101, "Invalid operation")
            elif prefix == "X":
                val = float(val)
                x_min, x_max = self.limits[prefix]
                if val < x_min or val > x_max:
                    return (102, "X value not in range ({}, {}): {}".format(x_min, x_max, val))
            elif prefix == "Y":
                val = float(val)
                y_min, y_max = self.limits[prefix]
                if val < y_min or val > y_max:
                    return (103, "Y value not in range ({}, {}): {}".format(y_min, y_max, val))
            elif prefix == "Z":
                val = float(val)
                z_min, z_max = self.limits[prefix]
                if val > z_min or val < z_max:
                    return (104, "Z value not in range ({}, {}): {}".format(z_min, z_max, val))
        return (200, "Ok")