import serial
import time


class Printer:

    def __init__(self, save_state, descriptor):
        self.printer = None  # type:serial.Serial
        self.GO_ORIGIN = 'G28'
        self.REPORT_TEMP = 'M105'
        self.HOTB = 'M140 S{}'
        self.HOTT = 'M104 S{} T0'
        self.TEMPERATURES = {'B': 60, 'T': 210}
        self.save_state = save_state
        self.descriptor = descriptor

    def connect_printer(self):
        try:
            self.printer = serial.Serial('COM3', 250000)  # type:serial.Serial
            time.sleep(2)
            return True
        except Exception as ex:
            self.descriptor["log"].append("The printer is not connected or other program is using it")
            self.descriptor["log"].append(str(ex))
            self.save_state(self.descriptor)
        return False

    def process_message(self):
        msgs = []
        while True:
            msg_printer = self.printer.read_all().decode("utf-8")
            if msg_printer == '':
                break
            msgs.append(msg_printer)
        return msgs

    def get_temperatures(self):
        temperatures = {}
        self.send_message(self.REPORT_TEMP)
        time.sleep(2)
        outs = self.process_message()
        for out in outs:
            out = self.clean_info(out)
            temps = out.split("-")
            for temp in temps:
                vals = temp.split(":")
                if len(vals) == 2:
                    temperatures[vals[0]] = float(vals[1])
        return temperatures

    def send_message(self, msg):
        print("SEND: {}".format(msg))
        self.log("SEND: {}".format(msg))
        msg_bytes = "{}\n".format(msg).encode('utf-8')
        self.printer.write(msg_bytes)

    def clean_info(self, msg):
        msg = str(msg).replace("ok", "")
        msg = str(msg).replace("echo:", "")
        msg = str(msg).replace("SD init fail", "")
        msg = str(msg).replace("/0.00", "")
        msg = str(msg).replace("@:0", "")
        msg = str(msg).replace("B@:0", "")
        msg = str(msg).replace("B ", "")
        msg = str(msg).replace(" ", "-")
        msg = str(msg).replace("\n", "")
        msg = str(msg).strip()
        return msg

    def close_connection(self):
        self.printer.close()

    def log(self, msg):
        self.descriptor["log"].append(msg)
        self.save_state(self.descriptor)
