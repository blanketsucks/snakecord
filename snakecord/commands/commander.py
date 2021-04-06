class CommandInvokeEvent:
    def __init__(self, commander, message, parser, prefix):
        self.commander = commander
        self.message = message
        self.parser = parser
        self.prefix = prefix
        self.args = []
        self.kwargs = {}
        self.command = None
        self.invoker = self.message.author
        self.channel = self.message.channel
        self.guild = self.message.guild
        self.send = self.channel.send

        try:
            cmd = parser.get_argument()
        except EOFError:
            return
        for name, command in commander.commands.items():
            if cmd == name or cmd in command.aliases:
                self.command = command
    
    def invoke(self):
        if self.command is not None:
            self.command.invoke(self)

class CommandInvokeHandler:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, commander, evnt, *args, **kwargs):
        self.commander = commander
        self.evnt = evnt
        self.args = args
        self.kwargs = kwargs
        return self
