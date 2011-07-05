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


import sys
import time
import argparse
import random
import string
import irclib


DEFAULT_server = 'chat.freenode.net'
DEFAULT_port   = 6667
DEFAULT_target = 'orcittest'


quit_command    = '/QUIT'
quit_message    = 'bye'
loop_sleeping_time = 1


random_string_charset = string.ascii_uppercase + string.ascii_lowercase + string.digits
random_string_length  = 10

def random_string( N=random_string_length ):
    return ''.join(random.sample(random_string_charset,N))


def parse_arguments():
    global server 
    global port
    global nick
    global target

    parser = argparse.ArgumentParser(description='Private messaging through IRC')
    parser.add_argument('--irc-server',     type=str, help='IRC server name ["'+str(DEFAULT_server)+'"]')
    parser.add_argument('--irc-port',       type=int, help='IRC server port ["'+str(DEFAULT_port)+'"]')
    parser.add_argument('--nick',           type=str, help='IRC local  nick [random string]')
    parser.add_argument('--target',         type=str, help='IRC remote nick [random string]')

    namespace = parser.parse_args()
    
    server    = namespace.irc_server or DEFAULT_server
    port      = namespace.irc_port   or DEFAULT_port  
    nick      = namespace.nick       or random_string(6)
    target    = namespace.target     or DEFAULT_target


class irc_client(irclib.SimpleIRCClient):

    def __init__(self, target = None):
        irclib.SimpleIRCClient.__init__(self)
        self.target = target
        self.logged_in = False

    def on_welcome(self, connection, event):
        self.logged_in = True
        print '### I am listening. My nick is %s. Press "%s" to leave ###' % (nick, quit_command)

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def on_privmsg(self, connection, event):
        print '### Received private message: %s' % event.arguments()

    def readline(self):
        line = sys.stdin.readline()
        if line == quit_command :
            self.connection.quit(quit_message)
        else: 
            self.connection.privmsg(self.target, line)


def main():

    parse_arguments()
    # print server, port, nick, target

    if irclib.is_channel(target):
        print '### FATAL ERROR: I only do private messaging and cannot join channels!'
        sys.exit(1)

    ic = irc_client(target)
    try:
        ic.connect(server, port, nick)
    except irclib.ServerConnectionError, IRCErrorMessage:
        print IRCErrorMessage
        sys.exit(1)
  # ic.ircobj.process_forever()
    while True :
        ic.ircobj.process_once()
        if ic.logged_in : ic.readline()
        time.sleep(loop_sleeping_time)


if __name__ == "__main__":
    main()
