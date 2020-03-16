import Infrastructure.s3 as s3
import Infrastructure.thread_runner as thread_runner
import Infrastructure.log as log
import printer
import procedures
import datetime

logger = log.get_logger("process")


class GcodeProcessor:
    def __init__(self):
        self.config = {}
        self.config['accessKey'] = 'AKIAS56KQ64LZOCK6L4E'
        self.config['secretKey'] = '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'
        self.config['bucketName'] = 'printer.candylero.com'
        self.thread_runner = thread_runner.Runner()

    def run(self):
        descriptor = {
            "name": "chappie",
            "seconds": 10,
            "is_running": False,
            "log": [],
            "error": ""
        }
        self.thread_runner.set_interval(self.run_printer, 10, "chappie", descriptor)

    def run_printer(self, descriptor, sec, t1):
        if not descriptor["is_running"]:
            try:
                self.s3_client = s3.S3Client(self.config)
                descriptor["is_running"] = True
                descriptor["started_date"] = str(datetime.datetime.now())
                self.process(descriptor)
            except Exception as ex:
                logger.error(ex)
            finally:
                descriptor["is_running"] = False

    def process(self, descriptor):
        files = self.s3_client.get_pending_files("GCODES/TOPRINT", ".gcode")
        file = files[0] if len(files) > 0 else None
        try:
            if file:
                local_file, file_name = self.s3_client.download_file(file, "gcodes")
                descriptor["name"] = file_name
                printer_instance = printer.Printer(self.save_state, descriptor)
                procedure = procedures.Procedures(self.save_state, descriptor)
                self.save_state(descriptor)
                connected = printer_instance.connect_printer()

                if connected:
                    printer_instance.process_message()
                    procedure.print_model(printer_instance, local_file)
        except Exception as ex:
            logger.error(ex)
            descriptor["error"] = str(ex)
        finally:
            self.s3_client.move_file(file, str(file).replace("TOPRINT", "PRINTED"))
            descriptor["end_date"] = str(datetime.datetime.now())
            self.save_state(descriptor)

    def save_state(self, descriptor):
        self.s3_client.upload_json("GCODES/PRINTERSTATE", "{}.json".format(descriptor["name"]), descriptor)
