import socket
import threading
import logging
import time

logger = logging.getLogger(__name__)

class ActiveDefense:
    """
    Spawns lightweight 'Honeyports' to detect scanners.
    """
    def __init__(self, ports=[8080, 2222, 2121], banner=b"Internal Service Error 500: Check Logs\n"):
        self.ports = ports
        self.banner = banner
        self.active_listeners = []
        self.running = False

    def start(self):
        self.running = True
        for port in self.ports:
            t = threading.Thread(target=self._listen, args=(port,))
            t.daemon = True
            t.start()
            self.active_listeners.append(t)
        logger.info(f"Active Defense Initialized on ports: {self.ports}")

    def _listen(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.listen(5)
            while self.running:
                conn, addr = s.accept()
                logger.warning(f"[ACTIVE DEFENSE] ALERT: Connection to HONEYPORT {port} from {addr}")
                # Fake banner to confuse attacker
                try:
                    conn.sendall(self.banner)
                    conn.close()
                except:
                    pass
        except Exception as e:
            logger.error(f"Failed to bind honeyport {port}: {e}")

    def stop(self):
        self.running = False
