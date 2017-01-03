#!/usr/bin/env python3

from invoke import Program, Collection
import actions

program = Program(version='0.0.1',namespace=Collection.from_module(actions))

if __name__ == '__main__':
    program.run()
