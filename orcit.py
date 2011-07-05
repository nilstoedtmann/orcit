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
import irclib
import time

#server = 'chat.freenode.net'
server = 'pratchett.freenode.net'
port   = 6667
nick   = 'akjwefkjaewhfb'
target = 'aleumhxlaehfxl'

quit_message = 'bye'
quit_command = '/QUIT'

class irc_client(irclib.SimpleIRCClient):

    def __init__(self, target = None):
        irclib.SimpleIRCClient.__init__(self)
        self.target = target
        self.logged_in = False

    def on_welcome(self, connection, event):
        self.logged_in = True
        print '### I am listening. Press "%s" to leave ###' % quit_command

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
        print "Logged in? %s" % ic.logged_in
        if ic.logged_in : 
            ic.readline()
        time.sleep(1)


if __name__ == "__main__":
    main()
