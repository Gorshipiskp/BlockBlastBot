import datetime
import os
from random import randint


def generate_string(length: int) -> str:
    return "".join([chr(randint(97, 122)) for _ in range(length)])


class Logger:
    def __init__(self, dirname="logs", filename_update_func: callable = None, prefix_log_func: callable = None):
        self.dirname = dirname
        self.filename_update_func = filename_update_func
        self.prefix_log_func = prefix_log_func
        self._cur_filename = None
        self.cur_log_tech_prefix = None

        if not filename_update_func:
            self.filename_update_func = lambda: datetime.datetime.now().strftime("%Y-%m-%d")

        if not prefix_log_func:
            self.prefix_log_func = lambda: datetime.datetime.now().strftime("%H:%M:%S – ")

    @property
    def cur_filename(self):
        os.makedirs(self.dirname, exist_ok=True)

        old_filename = self._cur_filename
        self.cur_filename = f"LOG_{self.filename_update_func()}.log"

        if old_filename != self._cur_filename:
            if os.path.exists(os.path.join(self.dirname, self._cur_filename)):
                with open(os.path.join(self.dirname, self._cur_filename), "r", encoding="UTF-8") as f:
                    self.cur_log_tech_prefix = f.readlines()[0].strip()
            else:
                with open(os.path.join(self.dirname, self._cur_filename), "w+", encoding="UTF-8") as f:
                    self.cur_log_tech_prefix = generate_string(4)
                    f.write(f"{self.cur_log_tech_prefix}")

        return self._cur_filename

    @cur_filename.setter
    def cur_filename(self, value):
        self._cur_filename = value

    def log(self, message):
        with open(os.path.join(self.dirname, self.cur_filename), "a+", encoding="UTF-8") as f:
            f.write(f"\n{self.cur_log_tech_prefix}_{self.prefix_log_func()}{message}")
