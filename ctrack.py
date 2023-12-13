import curses
import string
import threading
from time import sleep

from defaults import *
from run import run_track

class cTrack(object):

    def __init__(self, track=None, debug=0):
        self.__screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set( 0 )

        self.__track = track
        self.debug = debug
        self.__track.bind_sensors(self.__sensor_callback)
        self.__track.bind_debug(self.__writelog)

        self.__do_run = (self.__track != None)

        self.__run = run_track()

        self.__prefix = "_cTrack"
        self.__screen.keypad( 1 )
        self.__screen.refresh()

        self.__stat_win = self.__mk_win(1,1,1,1)
        self.__cmds_win = self.__mk_win(1,1,1,1)
        self.__outp_win = self.__mk_win(1,1,1,1)

        self.__do_resize()

        self.__msgs = []

    def __mk_win(self,h,w,y,x):
        win = curses.newwin(h,w,y,x)
        win.clear()
        win.box()
        win.border( 0 )
        win.refresh()
        return win

    def __paint_wins(self):
        self.__stat_win.border( 0 )
        self.__stat_win.addstr(0,2,"| Status |")
        self.__stat_win.refresh()
        self.__cmds_win.border( 0 )
        self.__cmds_win.addstr(0,2,"| Command |")
        self.__cmds_win.refresh()
        self.__outp_win.border( 0 )
        self.__outp_win.addstr(0,2,"| Output |")
        self.__outp_win.refresh()
        self.__screen.refresh()

    def __do_resize(self):
        y, x = self.__screen.getmaxyx()
        w = []
        extra = 0 if int(y/2)*2 == y else 1
        w.append({'x': int((x/3)*2)-2, 'y': int((y/2)-2+extra)})
        w.append({'x': int((x/3)*2)-2, 'y': int((y/2)-2)})
        w.append({'x': x-(int((x/3)*2)-2)-4, 'y': y-3})
        self.__screen.clear
        self.__screen.refresh()

        self.__stat_win.mvwin(1,1)
        self.__stat_win.resize(w[0]['y'], w[0]['x'])

        self.__cmds_win.mvwin(w[0]['y']+2,1)
        self.__cmds_win.resize(w[1]['y'],w[1]['x'])

        self.__outp_win.mvwin(1,w[0]['x']+3)
        self.__outp_win.resize(w[2]['y'],w[2]['x'])

        self.__paint_wins()

    def __writelog(self, inmessage):
        y,x = self.__outp_win.getmaxyx()
        msg = inmessage.splitlines()
        for message in msg:
            if len(self.__msgs) > y-5:
                z = self.__msgs.pop(0)
            self.__msgs.append(message)
        count = 0
        while count < len(self.__msgs):
            self.__outp_win.addstr(count+2,2, self.__msgs[count])
            self.__outp_win.clrtoeol()
            count += 1
        self.__outp_win.border(0)
        self.__outp_win.refresh()

    def __display_status(self):
        while self.__do_run:
            self.__stat_win.addstr(1,2,"Track   Speed  Direction   Reverse   S   Forward")
            self.__stat_win.addstr(2,2,"-------------------------  ---------------------")
            lcnt = 0
            for one_track in self.__track.tracks:
                speed_graph="*"*int(one_track['speed']*10)
                if one_track['direction'] == -1:
                    speed_graph = speed_graph.rjust(10)+"|"+str(" "*10)
                elif one_track['direction'] == 1:
                    speed_graph = str(" "*10)+"|"+speed_graph.ljust(10)
                else:
                    speed_graph = str(" "*10)+"|"+str(" "*10)
                self.__stat_win.addstr(lcnt+3,2, str(lcnt).rjust(3).ljust(5)+str(str(one_track['speed']*100)+"%").rjust(8).ljust(10)+one_track['direction_str'].ljust(10)+"  "+speed_graph)
                lcnt += 1
            self.__paint_wins()
            sleep(1)

    def __wait_for_key(self, text):
        y,x = self.__cmds_win.getmaxyx()
        self.__cmds_win.addstr(y-2,1, text)
        self.__cmds_win.clrtoeol()
        return self.__cmds_win.getkey(y-2,len(text)+2)

    def __process_command(self, cmd, args):
        cmd_list = [0, cmd]
        cmd_list = [cmd_list + args]
        if self.debug > 1:
            print(cmd_list)
        self.__run.process_commands(self.__track, cmd_list, self.debug)

    def __sensor_callback(self,press):
        pin = int(str(press.pin)[4:])
        self.__writelog('* Passing sensor: '+str(self.__track.sensor_id(pin=pin))+' ('+str(press.pin)+')')

    # Set speed
    def __do_r(self):
        self.__writelog("Setting speed")
        d = self.__wait_for_key("Direction (Forward/Stop/Reverse)").lower()
        if d in ['f','r']:
            self.__writelog(" * Direction: "+d)
            s = self.__wait_for_key("Speed (1 (10%) - 0 (100%))")
            if s in ['0','1','2','3','4','5','6','7','8','9']:
                speed = 1 if s == '0' else int(s)/10
                self.__writelog(" * Speed: "+str(speed*100)+"%")
                self.__process_command('set_speed',[speed, d])
        elif d.lower() == 's':
            self.__writelog(" * Stopping")
            self.__process_command('stop',[])

    def __do_switch(self,msgs=[], min_cnt=0, prop=None, cmd=""):
        self.__writelog(msgs[0])
        s_cnt = len(prop)
        if s_cnt > min_cnt:
            s_lst = []
            for s_num in range(s_cnt):
                s_lst.append(str(s_num))
            s = self.__wait_for_key(msgs[1]+" ("+"/".join(s_lst)+")").lower()
            if s in s_lst:
                self.__writelog(msgs[2]+t)
                self.__process_command(cmd,[t])
        else:
            self.__writelog(msgs[3])

    def main_loop(self):
        display_stats = threading.Thread(target=self.__display_status)
        display_stats.start()

        while self.__do_run:
            c = self.__wait_for_key("Command:").lower()
            self.__writelog("YOU HAVE PRESSED:\n * " + str(c))
            if c == 410 or c == "key_resize":
                self.__do_resize()
            elif c in set(string.ascii_lowercase + string.digits):
                if c in ['x','q']:
                    self.__do_run = False
                elif c in ['0','1','2','3','4','5','6','7','8','9']:
                    speed = 1 if c == '0' else int(c)/10
                    self.__writelog("Set speed: "+str(speed*100)+"%")
                    self.__process_command('set_speed',[speed, 1 if self.__track.direction == 0 else self.__track.direction])
                elif c == "d":
                    self.__writelog("Toggle direction")
                    self.__process_command('set_speed',[speed, self.__track.direction*-1])
                elif c == "s":
                    self.__writelog("Stop")
                    self.__process_command('stop',[])
                elif c == "t":
                    self.__do_switch(["Switch track", "Select track", " * set track: ", "No other tracks to switch to."], 1, self.__track.tracks, 'set_track')
                elif c == "p":
                    self.__do_switch(["Toggle point", "Select point", " * toggle point: ", "No points to toggle."], 0, self.__track.points, 'point_toggle')
                else:
                    cmd_str = self.__prefix+'__do_'+c
                    cmd = getattr(self,cmd_str, None)
                    if cmd != None:
                        if callable(cmd):
                            self.__writelog("Calling function: "+cmd_str)
                            cmd()
                    else:
                        self.__writelog("Unknown command: "+c)

            self.__paint_wins()

        display_stats.join()
        curses.endwin()

if __name__ == '__main__':
    x = cTrack()
    x.main_loop()