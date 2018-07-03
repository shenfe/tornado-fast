# coding: utf8

import sys

import os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httpclient
import tornado.log
from tornado.options import define, options
import signal
import segment


MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 5

define("port", default=8888, help="server port", type=int)


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

tornado.options.parse_command_line()

application = tornado.web.Application([
    (r"/greet", HelloHandler)
])

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(options.port)
print("start...")


def shutdown():
    tornado.log.app_log.info("stop server...")
    http_server.stop()

    tornado.log.app_log.info("server will stop in %d seconds" % MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    import time
    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN


    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
    stop_loop()


def sig_handler(sig, frame):
    """
    graceful shutdown tornado web server
    
    reference:
        https://gist.github.com/mywaiting/4643396
    """
    tornado.log.app_log.warning("caught signal: %s", sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


signal.signal(signal.SIGTERM, sig_handler)

tornado.ioloop.IOLoop.current().start()
tornado.log.app_log.info("exit...")
