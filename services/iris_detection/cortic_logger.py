class CorticLogger:
    def __init__(self, real_stdstream, log_callback):
        self.real_stdstream = real_stdstream
        self.log_callback = log_callback
        self.buf = ""

    def write(self, buf):
        # emit on each newline
        while buf:
            try:
                newline_index = buf.index("\n")
            except ValueError:
                # no newline, buffer for next call
                self.buf += buf
                break
            # get data to next newline and combine with any buffered data
            data = self.buf + buf[: newline_index + 1]
            self.buf = ""
            buf = buf[newline_index + 1 :]
            # perform complex calculations... or just print with a note.
            self.log_callback(data)
            data = data.replace("<cortic_log_info>", "[LOG]")
            data = data.replace("<cortic_log_warning>", "[WARNING]")
            data = data.replace("<cortic_log_error>", "[ERROR]")
            self.real_stdstream.write(data)
