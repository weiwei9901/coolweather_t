"""

命令分发器

"""


def cmds_dispatch():
    command = {}

    def register(name):
        def _wrapper(fn):
            command[name] = fn

            return fn
        return _wrapper

    def default():
        print('unknown command')

    def dispatch():
        while True:
            cmd = input('>>>')
            if cmd.strip() == "q":
                break
            command.get(cmd, default)()

    return register, dispatch


reg , dispatch = cmds_dispatch()


@reg('com1')
def fool():
    print('this is fool1')


dispatch()