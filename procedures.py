import printer
import time


class Procedures:

    def __init__(self, save_state, descriptor):
        self.save_state = save_state
        self.descriptor = descriptor

    def print_model(self, p_printer, file):
        self.prepare_temperatures(p_printer)
        self.execute_gcode('gcodes/init.gcode', p_printer)
        time.sleep(5)
        self.execute_gcode(file, p_printer)
        time.sleep(5)
        self.execute_gcode('gcodes/finish.gcode', p_printer)

    def prepare_temperatures(self, p_printer):
        self.log("prepare_temperatures")
        prepare = False
        printer_instance = p_printer  # type: printer.Printer
        printer_instance.send_message(printer_instance.HOTB.format(printer_instance.TEMPERATURES['B']))
        printer_instance.send_message(printer_instance.HOTT.format(printer_instance.TEMPERATURES['T']))
        try:
            while not prepare:
                temps = printer_instance.get_temperatures()
                count_prepares = 0
                for temp in temps:
                    if temp in printer_instance.TEMPERATURES:
                        actual = temps[temp]
                        expected = printer_instance.TEMPERATURES[temp]
                        self.log("{} actual temp {}  expected {}".format(temp, actual, expected))
                        if actual >= expected:
                            count_prepares += 1
                if count_prepares == 2:
                    prepare = True
        except Exception as ex:
            print(str(ex), "sending 0 to temps printer")
            self.log("sending 0 to temps printer error: {}".format(str(ex)))
            printer_instance.send_message(printer_instance.HOTB.format(0))
            printer_instance.send_message(printer_instance.HOTT.format(0))
            return False
        self.log("prepare_temperatures finished")
        return True

    def execute_gcode(self, file, p_printer):
        printer_instance = p_printer  # type: printer.Printer
        with open(file, encoding='utf-8') as infile:
            count = 0
            for line in infile:
                if not line.startswith(";"):
                    printer_instance.send_message(line)
                    self.is_next(printer_instance)
                self.log("line {} msg: {}".format(count, line))
                count += 1

    def is_next(self, printer_instance):
        next = False
        msgs = []
        while not next:
            msgs += printer_instance.process_message()
            msg_final = ''.join(msgs)
            if msg_final != '':
                print(msg_final)
                if 'ok' in msg_final:
                    self.log("next")
                    next = True
            if "\n" in msgs:
                msgs = []

    def log(self, msg):
        self.descriptor["log"].append(msg)
        self.save_state(self.descriptor)
