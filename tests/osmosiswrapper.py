import tempfile
import subprocess
import shutil
import socket
import solventwrapper
import logging


class LocalAndOfficial:
    def __init__(self):
        self.local = Server()
        self.official = Server()
        self.conf = tempfile.NamedTemporaryFile(suffix=".solvent.conf")
        self._writeConfig()
        solventwrapper.configurationFile = self.conf.name

    def exit(self):
        self.local.exit()
        self.official.exit()

    def _writeConfig(self):
        self.conf.write("LOCAL_OSMOSIS: localhost:%d\n" % self.local.port())
        self.conf.write("OFFICIAL_OSMOSIS: localhost:%d\n" % self.official.port())
        self.conf.flush()


class Server:
    def __init__(self):
        self._port = self._freePort()
        self._path = tempfile.mkdtemp()
        self._log = tempfile.NamedTemporaryFile()
        self._proc = subprocess.Popen([
            "osmosis", "server", "--objectStoreRootPath=" + self._path,
            "--serverTCPPort=%d" % self._port], close_fds=True, stdout=self._log, stderr=self._log)

    def exit(self):
        self._proc.terminate()
        shutil.rmtree(self._path, ignore_errors=True)

    def readLog(self):
        with open(self._log.name, "r") as f:
            return f.read()

    def port(self):
        return self._port

    def client(self):
        return Client(self)

    def _freePort(self):
        sock = socket.socket()
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('localhost', 0))
            return sock.getsockname()[1]
        finally:
            sock.close()


class Client:
    def __init__(self, server):
        self._server = server

    def checkout(self, path, label):
        return self._run("checkout", path, label)

    def listLabels(self, regex=None):
        args = []
        if regex is not None:
            args.append(regex)
        result = self._run("listlabels", * args)
        labels = result.strip().split("\n")
        if "" in labels:
            labels.remove("")
        return labels

    def _run(self, *args):
        try:
            return subprocess.check_output(
                ["osmosis", "--serverTCPPort=%d" % self._server.port()] + list(args),
                close_fds=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logging.exception("\n\n\nClientOutput:\n" + e.output)
            logging.error("\n\n\nServerOutput:\n" + self._server.readLog())
            raise
