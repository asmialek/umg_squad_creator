class Logger:
    def __init__(self, printer=True):
        self.printer = printer

    def log(self, msg):
        if self.printer:
            print(msg)