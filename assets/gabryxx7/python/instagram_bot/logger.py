import os
from datetime import datetime
import time
from pushbullet import PushBullet
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Logger:
    def __init__(self, log_filename, config_data):
        self.log_file = open(log_filename, "w")
        self.pb = None
        if "pushbullet_token" in config_data:
            self.pb = PushBullet(config_data["pushbullet_token"])

    def close(self):
        self.log_file.close()

    def i(self, txt, **kwargs):
        self.log(log_type="i", txt=txt, **kwargs)
    def w(self, txt, **kwargs):
        self.log(log_type="w", txt=txt, **kwargs)
    def e(self, txt, **kwargs):
        self.log(log_type="e", txt=txt, **kwargs)
    def s(self, txt, **kwargs):
        self.log(log_type="s", txt=txt, **kwargs)
    def v(self, txt, **kwargs):
        self.log(log_type="v", txt=txt, **kwargs)

    def log(self, log_type="i", txt="", with_time=True, end="\n", start="", pb_notif=True, to_file=True):
        prefix = ""
        if with_time:
            prefix = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
        color = ""
        send_to_pb = False
        log_type = log_type.lower()
        if log_type in ["i","info","nfo","log"]:
            color = bcolors.OKCYAN
        elif log_type in ["w","f"]:
            color = bcolors.WARNING
            # send_to_pb = True
        elif log_type in ["e","f", "n", "error", "fail", "no"]:
            color = bcolors.FAIL
            # send_to_pb = True
        elif log_type in ["s","success", "ok"]:
            color = bcolors.OKGREEN
            send_to_pb = True

        print(start+prefix+color+txt, end=end)
        if to_file and self.log_file is not None:
            try:
                self.log_file.write(prefix+txt+end)
                self.log_file.flush()
            except Exception as e:
                pass
        if self.pb is not None and pb_notif and send_to_pb:
            try:
                self.pb.push_note("Instagram Bot", f"{prefix}\n{txt}")
            except Exception as e:
                pass

    def wait(seconds, waiting_msg="", end_msg="", log_type="i", pb_notif=False):
        while seconds > 0:
            log(log_type, f"{waiting_msg} {seconds}s... ", end = "\r", start="", pb_notif=pb_notif, to_file=False)
            time.sleep(1)
            seconds = seconds - 1
        log(log_type, f"{waiting_msg} {seconds}s... {end_msg}", end = "\n", start="", pb_notif=pb_notif, to_file=True)
