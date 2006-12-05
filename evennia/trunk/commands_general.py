import settings
import time
import functions_general
import functions_db
from ansi import *

"""
Generic command module. Pretty much every command should go here for
now.
"""   

def cmd_look(cdat):
   """
   Handle looking at objects.
   """
   session = cdat['session']
   pobject = session.pobject
   args = cdat['uinput']['splitted'][1:]
   
   if len(args) == 0:   
      target_obj = session.pobject.location
   else:
      results = functions_db.local_and_global_search(pobject, ''.join(args))
      
      if len(results) > 1:
         session.msg("More than one match found (please narrow target):")
         for result in results:
            session.msg(" %s(#%s)" % (result.name, result.id,))
      elif len(results) == 0:
         session.msg("I don't see that here.")
      else:
         target_obj = results[0]
   
   retval = "%s%s%s(#%i)%s\r\n%s" % (
      ansi["normal"],
      ansi["hilite"], 
      target_obj.name,
      target_obj.id,
      ansi["normal"],
      target_obj.description,
   )
   session.msg(retval)
   
   con_players = []
   con_things = []
   con_exits = []
   
   for obj in target_obj.get_contents():
      if obj.is_player:
         if obj != session.pobject:
            con_players.append(obj)
      elif obj.is_exit:
         con_exits.append(obj)
      else:
         con_things.append(obj)
   
   if con_players:
      session.msg("%sPlayers:%s" % (ansi["hilite"], ansi["normal"],))
      for player in con_players:
         session.msg('%s(#%s)' %(player.name, player.id,))
   if con_things:
      session.msg("%sThings:%s" % (ansi["hilite"], ansi["normal"],))
      for thing in con_things:
         session.msg('%s(#%s)' %(thing.name, thing.id,))
   if con_exits:
      session.msg("%sExits:%s" % (ansi["hilite"], ansi["normal"],))
      for exit in con_exits:
         session.msg('%s(#%s)' %(exit.name, exit.id,))
   
def cmd_quit(cdat):
   """
   Gracefully disconnect the user as per his own request.
   """
   session = cdat['session']
   session.msg("Quitting!")
   session.handle_close()
   
def cmd_who(cdat):
   """
   Generic WHO command.
   """
   session_list = cdat['server'].get_session_list()
   session = cdat['session']
   
   retval = "Player Name        On For Idle   Room    Cmds   Host\n\r"
   for player in session_list:
      delta_cmd = time.time() - player.cmd_last
      delta_conn = time.time() - player.conn_time

      retval += '%-16s%9s %4s%-3s#%-6d%5d%3s%-25s\r\n' % \
         (player.name, \
         # On-time
         functions_general.time_format(delta_conn,0), \
         # Idle time
         functions_general.time_format(delta_cmd,1), \
         # Flags
         '', \
         # Location
         player.pobject.location.id, \
         player.cmd_total, \
         # More flags?
         '', \
         player.address[0])
   retval += '%d Players logged in.' % (len(session_list),)
   
   session.msg(retval)

def cmd_say(cdat):
   """
   Room-based speech command.
   """
   session_list = cdat['server'].get_session_list()
   session = cdat['session']
   speech = ''.join(cdat['uinput']['splitted'][1:])
   players_present = [player for player in session_list if player.pobject.location == session.pobject.location and player != session]
   
   retval = "You say, '%s'" % (speech,)
   for player in players_present:
      player.msg("%s says, '%s'" % (session.name, speech,))
   
   session.msg(retval)
   
def cmd_version(cdat):
   """
   Version info command.
   """
   session = cdat['session']
   retval = "-"*50 +"\n\r"
   retval += "Evennia %s\n\r" % (settings.EVENNIA_VERSION,)
   retval += "-"*50
   session.msg(retval)

def cmd_time(cdat):
   """
   Server local time.
   """
   session = cdat['session']
   session.msg('Current server time : %s' % (time.strftime('%a %b %d %H:%M %Y (%Z)', time.localtime(),)))
   
def cmd_uptime(cdat):
   """
   Server uptime and stats.
   """
   session = cdat['session']
   server = cdat['server']
   start_delta = time.time() - server.start_time
   session.msg('Current server time : %s' % (time.strftime('%a %b %d %H:%M %Y (%Z)', time.localtime(),)))
   session.msg('Server start time   : %s' % (time.strftime('%a %b %d %H:%M %Y', time.localtime(server.start_time),)))
   session.msg('Server uptime       : %s' % functions_general.time_format(start_delta, style=2))