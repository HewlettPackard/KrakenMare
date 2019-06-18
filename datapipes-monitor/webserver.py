# coding=utf-8
import pathlib
import cherrypy
import hashlib
import pytoml
import time
import logging

class CherryServer(object):
    # ---------------------------------- GENERIC : WEB ERROR MANAGEMENT (CLASS LEVEL) ----------------------------------
    @staticmethod
    def _error_page(status, message, traceback, version):
        print("HTTP ERR = %s | %s | %s | %s" % (str(status), str(message), str(version), str(traceback)[:5]))
        return "<html><body>Error %s</body></html>" % str(status)
    @staticmethod
    def _handle_error():
        cherrypy.response.status = 500
        cherrypy.response.body = b"Error 500"

    # ---------------------------------- GENERIC : CREDENTIALS MANAGEMENT (CLASS LEVEL) ----------------------------------
    _theusers = { }
    @staticmethod
    def _init_users(dico):
        """Read users from a dict and implement the class variable.
        :param dico: dict() of login : pwd ALREADY HASHED
        :return: None
        """
        CherryServer._theusers = dict(dico)
    @staticmethod
    def _validate_password(realm='localhost', username='', password=''):
        if 3 < len(username) < 20 and 3 < len(password) < 20:
            userh = hashlib.sha256(str(username).encode('utf-8')).hexdigest()
            passh = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
            if userh in CherryServer._theusers and CherryServer._theusers[userh] == passh:
                return True
        print("LOGIN ERROR WITH %s | %s | %s" % (str(realm), str(username), str(password)))
        return False

    # ---------------------------------- CONFIGS DEFAULT (CLASS LEVEL) ----------------------------------
    # http://docs.cherrypy.org/en/latest/advanced.html#securing-your-server
    _conf_defaut_users  = {}
    _conf_defaut_server = {
        "server.socket_host"            : "0.0.0.0" ,
        "server.socket_port"            : 80 ,
        "server.socket_queue_size"      : 10 ,  # The "backlog" argument to socket.listen(); specifies the maximum number of queued connections (default 5).
        "server.socket_timeout"         : 10 ,  # The timeout in seconds for accepted connections (default 10).
        "server.accepted_queue_size"    : 60 ,  # The maximum number of requests which will be queued up before the server refuses to accept it (default -1, meaning no limit).
        "server.thread_pool"            : 5  ,  # The number of worker threads to start up in the pool.
        "server.thread_pool_max"        : 40 ,  # The maximum size of the worker-thread pool. Use -1 to indicate no limit.
        'logging.screen'       : False ,
        'logging.access_file'  : '' ,
        'logging.error_file'   : '',
        'engine.autoreload.on' : False,
        }

    # ---------------------------------- STATIC TO START & STOP (CLASS LEVEL) ----------------------------------
    @staticmethod
    def web_server_stop():
        cherrypy.engine.exit()

    @staticmethod
    def web_server_start(configServer=None, configUsers=None):
        retour = True
        # ------ Config Server
        CherryServer._conf_defaut_server['error_page.default']     = CherryServer._error_page
        CherryServer._conf_defaut_server['request.error_response'] = CherryServer._handle_error
        conf_server = dict(CherryServer._conf_defaut_server)

        conf_server['server.socket_host'] = configServer.get('host') or '0.0.0.0'
        conf_server['server.socket_port'] = configServer.get('port') or 80

        conf_users = dict(CherryServer._conf_defaut_users)
        conf_users.update(configUsers)

        # ------------ CONFIG DE L'APPLI WEB ------------
        WebAppli_root_url = "/"
        WebAppli_config = {
            # --- Static files : Serving 1 single static file = the icon of the website
            '/images/favicon.ico' : {
                'tools.staticfile.on'       : True,
                'tools.staticfile.filename' : pathlib.Path().cwd().joinpath("www").joinpath("images").joinpath("favicon.gif").as_posix()
                },
            # --- Service website and application
            '/': {
                # ----- Authentication -----
                'tools.auth_basic.on'            : False,
                'tools.auth_basic.realm'         : 'localhost',
                'tools.auth_basic.checkpassword' : CherryServer._validate_password,
                # ----- Static files : Serving A WHOLE DIRECTORY -----
                'tools.staticdir.on'     : True,
                'tools.staticdir.dir'    : pathlib.Path().cwd().joinpath("www").as_posix(),
                'tools.staticdir.index'  : "index.html",
                # ----- Sessions -----
                'tools.sessions.on'       : False,
                'tools.sessions.secure'   : True,
                'tools.sessions.httponly' : False,
                }
            }

        # ------------ LAUNCH WEB SERVER ------------
        try :
            # ------ CHERRYPY SERVER CONFIGURATION
            InstanceWebServ = CherryServer()
            CherryServer._init_users(conf_users)
            cherrypy.config.update(conf_server)

            # ------ CHERRYPY LAUNCH
            cherrypy.tree.mount(InstanceWebServ, WebAppli_root_url, WebAppli_config)
            # ------ Loglevel CherryPy
            for log_mgt in logging.Logger.manager.loggerDict.keys():
                if "cherrypy.access" in log_mgt or "PIL" in log_mgt or "cherrypy.error" in log_mgt :
                    logging.getLogger(log_mgt).setLevel(logging.WARNING)
            # ------ Launch
            cherrypy.engine.start()
            print("Now serving on {:s}:{:d}".format(conf_server.get("server.socket_host") or "PROBLEM", conf_server.get("server.socket_port") or 0))
        except Exception as E3 :
            retour = False
            print("Cannot start cherrypy server : {}".format(str(E3)))

        return retour

    # ---------------------------------- THE WEB APP = INSTANCE FUNCTIONS----------------------------------
    def __init__(self, ):
        self._jsondb_sizemax        = 500
        self._jsondb_data           = dict()
        self._jsondb_ts_last_access = dict()


# ======================================== NOTHING TO CHANGE BELOW ========================================
if __name__ == '__main__':

    conf = dict()
    try :
        with open('webserver.toml', mode='r', encoding='utf-8', errors='backslashreplace') as the_file:
            conf = pytoml.load(the_file)
    except :
        conf = dict()

    print("-- Web-Server is starting --")
    print("Config : {:s}".format(str(conf)))
    OK_servWeb = CherryServer.web_server_start(configServer=conf, configUsers={})

    # -- LOOP Signal trap
    if OK_servWeb :
        while True :
            time.sleep(3)
    try :
        print("Stopping CherryPy")
        CherryServer.web_server_stop()
    except :
        pass
    print("-- Web-Server finished --")
