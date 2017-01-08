#!/usr/bin/env python3

from invoke import Program, Collection
import actions
import health_actions

ns = Collection.from_module(actions)
ns.add_collection(health_actions,name='health')


program = Program(version='0.0.1',namespace=ns)

if __name__ == '__main__':
    program.run()
