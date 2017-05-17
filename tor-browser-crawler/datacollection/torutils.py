import os
import functools
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import firefox
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import shutil
import socket
from stem import CircStatus, StreamStatus
from stem.control import Controller, EventType
import stem.process
from stem.util import term
import sqlite3
import sys
from httplib import CannotSendRequest
from tld import get_tld
import common as cm
from log import wl_log
from utils import clone_dir_with_timestap
import utils as ut
#added by seoh, beautifulsoup
from bs4 import BeautifulSoup

def _extract_info(self, soup):
        empty_info = {'from': 0, 'to': 0, 'total': 0}
        div_ssb = soup.find('div', id='ssb')
        if not div_ssb:
            self._maybe_raise(ParseError, "Div with number of results was not found on Google search page", soup)
            return empty_info
        p = div_ssb.find('p')
        if not p:
            self._maybe_raise(ParseError, """<p> tag within <div id="ssb"> was not found on Google search page""", soup)
            return empty_info
        txt = ''.join(p.findAll(text=True))
        txt = txt.replace(',', '')
        matches = re.search(r'%s (\d+) - (\d+) %s (?:%s )?(\d+)' % self._re_search_strings, txt, re.U)
        if not matches:
            return empty_info
        return {'from': int(matches.group(1)), 'to': int(matches.group(2)), 'total': int(matches.group(3))}

class TorController(object):
    def __init__(self, torrc_dict, tbb_version, tor_log='/dev/null'):
        self.torrc_dict = torrc_dict
        self.controller = None
        self.tbb_version = tbb_version
        self.tmp_tor_data_dir = None
        self.tor_process = None
        self.log_file = tor_log

    def tor_log_handler(self, line):
        wl_log.info(term.format(line))

    def restart_tor(self):
        """Kill current Tor process and run a new one."""
        self.kill_tor_proc()
        self.launch_tor_service(self.log_file)

    def kill_tor_proc(self):
        """Kill Tor process."""
        if self.tor_process:
            wl_log.info("Killing tor process")
            self.tor_process.kill()
        if self.tmp_tor_data_dir and os.path.isdir(self.tmp_tor_data_dir):
            wl_log.info("Removing tmp tor data dir")
            shutil.rmtree(self.tmp_tor_data_dir)
    def scan(controller, path):
          """
          Fetch check.torproject.org through the given path of relays, providing back
          the time it took.
          """
        
          circuit_id = self.controller.new_circuit(path, await_build = True)
        
          def attach_stream(stream):
            if stream.status == 'NEW':
              self.controller.attach_stream(stream.id, circuit_id)
        
          self.controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
        
          try:
            self.controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
            start_time = time.time()
        
            check_page = query('https://check.torproject.org/')
        
            if 'Congratulations. This browser is configured to use Tor.' not in check_page:
              raise ValueError("Request didn't have the right content")
        
            return time.time() - start_time
          finally:
            self.controller.remove_event_listener(attach_stream)
            self.controller.reset_conf('__LeaveStreamsUnattached')                                                    
    def launch_tor_service(self, logfile='/dev/null'):
        """Launch Tor service and return the process."""
        self.log_file = logfile
        self.tmp_tor_data_dir = ut.clone_dir_with_timestap(
            cm.get_tor_data_path(self.tbb_version))

        self.torrc_dict.update({'DataDirectory': self.tmp_tor_data_dir,
                                'Log': ['INFO file %s' % logfile]})

        wl_log.debug("Tor config: %s" % self.torrc_dict)
        try:
            self.tor_process = stem.process.launch_tor_with_config(
                config=self.torrc_dict,
                init_msg_handler=self.tor_log_handler,
                tor_cmd=cm.get_tor_bin_path(self.tbb_version),
                timeout=18000#270 set longer if needed
                
                )
            self.controller = Controller.from_port()
            self.controller.authenticate()
            ##
            for circ in sorted(self.controller.get_circuits()):
                if circ.status != CircStatus.BUILT:
                  continue
            
                print("")
                print("Circuit %s (%s)" % (circ.id, circ.purpose))
            
                for i, entry in enumerate(circ.path):
                  div = '+' if (i == len(circ.path) - 1) else '|'
                  fingerprint, nickname = entry
            
                  desc = self.controller.get_network_status(fingerprint, None)
                  address = desc.address if desc else 'unknown'
            
                  print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))
                  ##
                  '''
            relay_fingerprints = [desc.fingerprint for desc in self.controller.get_network_statuses()]

            for fingerprint in relay_fingerprints:
                try:
                  time_taken = scan(controller, [fingerprint, EXIT_FINGERPRINT])
                  print('%s => %0.2f seconds' % (fingerprint, time_taken))
                except Exception as exc:
                  print('%s => %s' % (fingerprint, exc))  '''  
            return self.tor_process

        except stem.SocketError as exc:
            wl_log.critical("Unable to connect to tor on port %s: %s" %
                            (cm.SOCKS_PORT, exc))
            sys.exit(1)
        except:
            # most of the time this is due to another instance of
            # tor running on the system
            wl_log.critical("Error launching Tor", exc_info=True)
            sys.exit(1)

        wl_log.info("Tor running at port {0} & controller port {1}."
                    .format(cm.SOCKS_PORT, cm.CONTROLLER_PORT))
        return self.tor_process
     
        
     
    def close_all_streams(self):
        """Close all streams of a controller."""
        wl_log.debug("Closing all streams")
        try:
            ut.timeout(cm.STREAM_CLOSE_TIMEOUT)
            for stream in self.controller.get_streams():
                wl_log.debug("Closing stream %s %s %s " %
                             (stream.id, stream.purpose,
                              stream.target_address))
                self.controller.close_stream(stream.id)  # MISC reason
        except ut.TimeExceededError:
            wl_log.critical("Closing streams timed out!")
        except:
            wl_log.debug("Exception closing stream")
        finally:
            ut.cancel_timeout()


class TorBrowserDriver(webdriver.Firefox, firefox.webdriver.RemoteWebDriver):
    def __init__(self, tbb_binary_path=None, tbb_profile_dir=None,
                 tbb_logfile_path=None,
                 tbb_version=cm.TBB_DEFAULT_VERSION, page_url="",
                 capture_screen=True):
        self.is_running = False
        self.tbb_version = tbb_version
        self.export_lib_path()
        # Initialize Tor Browser's profile
        self.page_url = page_url
        self.capture_screen = capture_screen
        self.profile = self.init_tbb_profile(tbb_version)
        # set homepage to a blank tab
        self.profile.set_preference('browser.startup.page', "0")
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')

        # configure Firefox to use Tor SOCKS proxy
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', cm.SOCKS_PORT)
        if cm.DISABLE_RANDOMIZEDPIPELINENING:
            self.profile.set_preference(
                'network.http.pipelining.max-optimistic-requests', 5000)
            self.profile.set_preference(
                'network.http.pipelining.maxrequests', 15000)
            self.profile.set_preference('network.http.pipelining', False)

        self.profile.set_preference(
            'extensions.torlauncher.prompt_at_startup',
            0)
        # added by seoh, other settings for...
        self.profile.set_preference("places.history.enabled",False)
        self.profile.set_preference("privacy.clearOnShutdown.offlineApps",True)
        self.profile.set_preference("privacy.clearOnShutdown.passwords",True)
        self.profile.set_preference("privacy.clearOnShutdown.siteSettings",True)
        self.profile.set_preference("privacy.sanitize.sanitizeOnShutdown",True)
        self.profile.set_preference("signon.rememberSignons",False)
        # Disable cache - Wang & Goldberg's setting
        self.profile.set_preference('network.http.use-cache', False)
        # added by seoh, if it uses html5 new manifest attribute, set the following:
        self.profile.set_preference('browser.cache.offline.enable', False)
        # added by seoh, disable prefetching:
        self.profile.set_preference('network.dns.disablePrefetch', True)
        self.profile.set_preference('network.prefetch-next', False)
        # added by seoh, for disabling firebug
        self.profile.set_preference("extensions.firebug.netexport.pageLoadedTimeout",10000)
        self.profile.set_preference("extensions.firebug.netexport.showPreview",False)
        self.profile.set_preference("extensions.firebug.netexport.alwaysEnableAutoExport",False)
        self.profile.set_preference("extensions.firebug.DBG_STARTER",False)
        self.profile.set_preference("extensions.firebug.onByDefault",False)
        self.profile.set_preference("extensions.firebug.allPagesActivation","off")
        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        # prevent Tor Browser running it's own Tor process
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference(
            'extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        self.profile.update_preferences()
        # Initialize Tor Browser's binary
        self.binary = self.get_tbb_binary(tbb_version=self.tbb_version,
                                          logfile=tbb_logfile_path)

        # Initialize capabilities
        self.capabilities = DesiredCapabilities.FIREFOX
        self.capabilities.update({'handlesAlerts': True,
                                  'databaseEnabled': True,
                                  'javascriptEnabled': True,
                                  'browserConnectionEnabled': True})

        try:
            super(TorBrowserDriver, self)\
                .__init__(firefox_profile=self.profile,
                          firefox_binary=self.binary,
                          capabilities=self.capabilities)
            self.is_running = True
            #html_source = self.page_source()
            #html_source = webdriver.Firefox.page_source(self)
            #soup = BeautifulSoup(html_source,"lxml")
            #results_info = _extract_info(soup)
            #if results_info['total'] == 0:
                #self.eor = True
            #print 'results_info[total]=',results_info['total']
        except WebDriverException as error:
            wl_log.error("WebDriverException while connecting to Webdriver %s"
                         % error)
        except socket.error as skterr:
            wl_log.error("Error connecting to Webdriver", exc_info=True)
            wl_log.error(skterr.message)
        except Exception as e:
            wl_log.error("Error connecting to Webdriver: %s" % e,
                         exc_info=True)

    def export_lib_path(self):
        os.environ["LD_LIBRARY_PATH"] = os.path.dirname(
            cm.get_tor_bin_path(self.tbb_version))

    def get_tbb_binary(self, tbb_version, binary=None, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = None
        if not binary:
            binary = cm.get_tb_bin_path(tbb_version)
        if logfile:
            tbb_logfile = open(logfile, 'a+')

        # in case you get an error for the unknown log_file, make sure your
        # Selenium version is compatible with the Firefox version in TBB.
	print "tbb_binary_directory", binary
        tbb_binary = FirefoxBinary(firefox_path=binary,
                                   log_file=tbb_logfile)
        return tbb_binary

    def add_canvas_permission(self):
        """Create a permission db (permissions.sqlite) and add

        exception for the canvas image extraction. Otherwise screenshots
        taken by Selenium will be just blank images due to canvas
        fingerprinting defense in TBB."""

        connect_to_db = sqlite3.connect  # @UndefinedVariable
        perm_db = connect_to_db(os.path.join(self.prof_dir_path,
                                             "permissions.sqlite"))
        cursor = perm_db.cursor()
        # http://mxr.mozilla.org/mozilla-esr31/source/build/automation.py.in
        cursor.execute("PRAGMA user_version=3")
        cursor.execute("""CREATE TABLE IF NOT EXISTS moz_hosts (
          id INTEGER PRIMARY KEY,
          host TEXT,
          type TEXT,
          permission INTEGER,
          expireType INTEGER,
          expireTime INTEGER,
          appId INTEGER,
          isInBrowserElement INTEGER)""")

        domain = get_tld('http://www.google.com')#(self.page_url)
        wl_log.debug("Adding canvas/extractData permission for %s" % domain)
        qry = """INSERT INTO 'moz_hosts'
        VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % domain
        cursor.execute(qry)
        perm_db.commit()
        cursor.close()

    def init_tbb_profile(self, version):
        profile_directory = cm.get_tbb_profile_path(version)
	print "profile_directory is:", profile_directory

        self.prof_dir_path = clone_dir_with_timestap(profile_directory)
        if self.capture_screen and self.page_url:
            self.add_canvas_permission()
        try:
            tbb_profile = webdriver.FirefoxProfile(self.prof_dir_path)
        except Exception:
            wl_log.error("Error creating the TB profile", exc_info=True)
        else:
            return tbb_profile

    def quit(self):
        """
        Overrides the base class method cleaning the timestamped profile.

        """
        self.is_running = False
        try:
            wl_log.info("Quit: Removing profile dir")
            shutil.rmtree(self.prof_dir_path)
            super(TorBrowserDriver, self).quit()
        except CannotSendRequest:
            wl_log.error("CannotSendRequest while quitting TorBrowserDriver",
                         exc_info=False)
            # following is copied from webdriver.firefox.webdriver.quit() which
            # was interrupted due to an unhandled CannotSendRequest exception.

            # kill the browser
            self.binary.kill()
            # remove the profile folder
            try:
                shutil.rmtree(self.profile.path)
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
            except Exception as e:
                print(str(e))
        except Exception:
            wl_log.error("Exception while quitting TorBrowserDriver",
                         exc_info=True)
            
