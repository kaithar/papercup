import logging, time, traceback, os, sys, pprint

class handler(logging.Handler):
    host = None
    ident = None
    def __init__(self, ident):
        logging.Handler.__init__(self)
        self.host = os.uname()[1]
        self.ident = ident
    def emit(self, record):
        """
        Emit a record.
            args        ()
            created     1444647841.880585
            exc_info    None
            exc_text    None
            filename    'main.py'
            funcName    '<module>'
            getMessage  <bound method LogRecord.getMessage of <logging.LogRecord object at 0x7f2574375c90>>
            levelname   'INFO'
            levelno     20
            lineno      25
            module      'main'
            msecs       880.5849552154541
            msg         {'test': 1}
            name        'screwy'
            pathname    'main.py'
            process     24867
            processName 'MainProcess'
            relativeCreated 0.8308887481689453
            thread      139798841562880
            threadName 'MainThread'
        """
        msg = record.getMessage()
        if msg:
            out = "%s.%03d [%s%s"%(
                time.strftime("%Y%m%d %H:%M:%S", time.localtime(record.created)),
                int(record.msecs),
                ("%-18s"%record.name) if record.name != 'root' else record.filename,
                (" L%-4s"%record.lineno) if record.levelname == 'DEBUG' else "")
            if (record.threadName != "MainThread"):
                out += "|%s" % record.threadName
            out += "|%s] "%record.levelname
            if ("\n" in msg):
                out += "\n|\n| "
            if msg[-1] == '\n':
                msg = msg[:-1]
            out += msg.replace("\n", "\n| ")+"\n"
            if ("\n" in msg):
                out += "\\\n"
            sys.stdout.write(out)
        else:
            sys.stdout.write("\n")

        if (record.exc_info):
            e = traceback.format_exception(*record.exc_info)
            e = "".join(e)
            if e[-1] == '\n':
                e = e[:-1]
            sys.stdout.write("| "+e.replace("\n", "\n| ")+"\n\\\n")
        sys.stdout.flush()
