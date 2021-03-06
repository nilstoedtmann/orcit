#!/usr/bin/python -u

# Copyright (C) 2011  Nils Toedtmann  http://nils.toedtmann.net/
# 
# This file is part of orcit.
# 
# orcit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# orcit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with orcit. If not, see 
# <http://www.gnu.org/licenses/gpl-2.0.html>


PROGRAM_NAME    = 'orcit'
PROGRAM_VERSION = '0.1'
PROGRAM_LICENCE = 'GPLv2+'
PROGRAM_AUTHOR  = 'Nils Toedtmann http://nils.toedtmann.net/'


import sys
from   time     import sleep
from   argparse import ArgumentParser
from   random   import sample
from   string   import ascii_uppercase, ascii_lowercase, digits 
import irclib2
from   fcntl    import fcntl, F_GETFL, F_SETFL
from   os       import O_NONBLOCK

DEFAULT_server      = 'irc.oftc.net'
DEFAULT_port        = 6667
DEFAULT_target      = 'orcittest'
DEFAULT_socksserver = 'localhost'
DEFAULT_socksport   = 9050   # SOCKS5 port of tor

quit_command        = 'QUIT'
quit_message        = 'bye'
loop_sleeping_time  = 1


random_string_charset = ascii_uppercase + ascii_lowercase + digits
random_string_length  = 10

def random_string( N=random_string_length ):
    return ''.join(sample(random_string_charset,N))


def parse_arguments():
    global server 
    global port
    global nick
    global target
    global socksserver
    global socksport

    parser = ArgumentParser(description='Private messaging through IRC')
    parser.add_argument('--irc-server',     type=str, help='IRC server name ["'+str(DEFAULT_server)+'"]')
    parser.add_argument('--irc-port',       type=int, help='IRC server port ["'+str(DEFAULT_port)+'"]')
    parser.add_argument('--nick',           type=str, help='IRC local  nick [random string]')
    parser.add_argument('--target',         type=str, help='IRC remote nick [random string]')
    parser.add_argument('--socks-server',   type=str, help='SOCKS5 server ["'+str(DEFAULT_socksserver)+'"]')
    parser.add_argument('--socks-port',     type=int, help='SOCKS5 server ["'+str(DEFAULT_socksport)+'"]')
    parser.add_argument('--without-socks',  action='store_true', help="equivalent to \"--socks-server None\"")
   #parser.add_argument('--echo',     action='store_true', help="Activate low level debug printing [Off]")

    namespace = parser.parse_args()
    
    server      = namespace.irc_server   or DEFAULT_server
    port        = namespace.irc_port     or DEFAULT_port  
    nick        = namespace.nick         or random_string(6)
    target      = namespace.target       or DEFAULT_target
    socksserver = namespace.socks_server or DEFAULT_socksserver
    socksport   = namespace.socks_port   or DEFAULT_socksport 

    if socksserver.upper() == 'NONE' or namespace.without_socks : socksserver = None


class irc_client(irclib2.SimpleIRCClient):

    def __init__(self, input_handle = sys.stdin, remote_nick = None):
        irclib2.SimpleIRCClient.__init__(self)
        self.target = remote_nick
        self.logged_in = False

        # make input file handle non-blocking, see 
        # http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python 
        fd = input_handle.fileno()
        fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK)

    def on_welcome(self, connection, event):
        self.logged_in = True
        print 'registered'
        print '### Remote nick is  "%s". Remote side could use this command to speak to us: ' % (nick)
        print '###        %s --nick %s  --target %s  [--without-socks]\n###' % (PROGRAM_NAME, target, nick)
        print '### You can type you message now. Use "%s" to exit.\n'   % (quit_command)

    def on_disconnect(self, connection, event):
        print '### Exiting.'
        sys.exit(0)

    def on_privmsg(self, connection, event):
        for message in event.arguments():
            print '\n### Received private message: ==>%s<=='  % message

    def readline(self):
        line = ''
        try: line = sys.stdin.readline().rstrip('\n')
        except: return

        if line :
            if line == quit_command :
                print '### Received exit command. Cleaning up ...'
                self.connection.quit(quit_message)
            else:
                print '### Sending  private message: ==>%s<==' % line 
                self.connection.privmsg(self.target, line)

    def loop(self):
        while True :
            self.ircobj.process_once()
            if self.logged_in : self.readline()
            sleep(loop_sleeping_time)


def main():

    print '### Welcome to %s %s. This software is licenced under %s\n###' % (PROGRAM_NAME, PROGRAM_VERSION, PROGRAM_LICENCE) 

    parse_arguments()
    # print server, port, nick, target

    if irclib2.is_channel(target):
        print '### FATAL ERROR: I only do private messaging and cannot join channels!'
        sys.exit(1)

    ic = irc_client(input_handle = sys.stdin, remote_nick = target)
    try:
        if socksserver :
            print '### Connecting to %s:%s via SOCKS5 proxy %s:%s ...' % (server, port, socksserver, socksport),
        else:    
            print '### Connecting to %s:%s ...' % (server, port),
        ic.connect(server, port, nick, socksserver=socksserver, socksport=socksport)
        print 'connected' 
        print '### Registering nick "%s" ...' % (nick),
    except irclib2.ServerConnectionError, IRCErrorMessage:
        print IRCErrorMessage
        sys.exit(1)
    ic.loop()


if __name__ == "__main__":
    main()
