class STOMPTransaction(object):
    def __init__(self, daemon, trans_id):
        self.daemon = daemon
        self.trans_id = trans_id
        self.frames = []

    def __call__(self, frame):
        del frame.headers['transaction']
        if 'receipt' in frame.headers:
            del frame.headers['receipt']
        if frame.action == "COMMIT":
            for f in self.frames:
                self.daemon.commit(f)
            self.daemon.abort(self.trans_id)
        elif frame.action == "ABORT":
            self.daemon.abort(self.trans_id)
        else:
            self.frames.append(frame)