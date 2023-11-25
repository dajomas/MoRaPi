import textwrap
from cmd import Cmd
from run import run_train

class iTrain(Cmd):
    prompt = "iTrain> "
    intro = "Welcome to the Interactive Train operations! Type ? to list commands, or show_help for extensive help"
    def __init__(self, completekey='tab', stdin=None, stdout=None, track=None, debug=0):
        super(iTrain, self).__init__(completekey, stdin, stdout)

        self.track = track
        self.track.bind_switches(self.__switch_callback)
        self.debug = debug
        self.__run = run_train()

    def __switch_callback(self,press):
        pin = int(str(press.pin)[4:])
        print("\n* Passing switch: "+str(self.track.switch_id(pin=pin))+" ("+str(press.pin)+")")

    def __process_command(self, inp, cmd):
        cmd_list = inp.split(" ")
        cmd_list.insert(0, 0)
        cmd_list.insert(1, cmd)
        cmd_list = [cmd_list]
        if self.debug > 1:
            print(cmd_list)
        self.__run.process_commands(self.track, cmd_list, self.debug)

    def do_exit(self, inp):
        print("\nChoo Choo, Bey Bey...\n")
        return True

    def do_on(self, inp):
        if self.track.use_enable_pin:
            self.track.on()

    def do_off(self, inp):
        if self.track.use_enable_pin:
            self.track.off()

    def do_set_speed(self,inp):
        self.__process_command(inp,"set_speed")

    def do_set_track(self,inp):
        self.__process_command(inp,"set_track")

    def do_set(self,inp):
        l_inp = inp.split(" ")
        if len(l_inp) > 0:
            inp = " ".join(l_inp[1:])
            if l_inp[0] == "speed":
                self.__process_command(inp, "set_speed")
            elif l_inp[0] == "track":
                self.__process_command(inp, "set_track")
            else:
                print("\nInvalid command.\n")
                self.do_show_help(inp)
        else:
            print("\nInvalid command.\n")
            self.do_show_help(inp)

    def do_run(self,inp):
        l_inp = inp.split(" ")
        if len(l_inp) > 0:
            inp = " ".join(l_inp[1:])
            if l_inp[0] == "for":
                self.__process_command(inp, "run_for")
            elif l_inp[0] == "until":
                self.__process_command(inp, "run_until")
            elif l_inp[0] == "script":
                self.do_run_script(inp)
            else:
                print("\nInvalid command.\n")
                self.do_show_help(inp)
        else:
            print("\nInvalid command.\n")
            self.do_show_help(inp)

    def do_run_for(self,inp):
        self.__process_command(inp,"run_for")

    def do_run_until(self,inp):
        self.__process_command(inp,"run_until")

    def do_pause(self,inp):
        self.__process_command(inp,"pause")

    def do_wait_for_switch(self,inp):
        self.__process_command(inp,"wait_for_switch")

    def do_wait(self,inp):
        l_inp = inp.split(" ")
        if len(l_inp) > 1:
            inp = " ".join(l_inp[2:])
            if l_inp[0] == "for" and l_inp[1] == "switch":
                self.__process_command(inp, "wait_for_switch")
            else:
                print("\nInvalid command.\n")
                self.do_show_help(inp)
        else:
            print("\nInvalid command.\n")
            self.do_show_help(inp)

    def do_stop(self,inp):
        self.__process_command(inp,"stop")

    def do_run_script(self,inp):
        script = open(inp,'r')
        script_content = script.read()
        script.close()
        script_list = script_content.split('\n')
        cmd_list = []
        for line in script_list:
            if len(line.split()) > 0 and line[0] != '#':
                cmd_list.append(line.split())
        self.__run.process_commands(self.track, cmd_list, self.debug)

    def default(self,inp):
        if inp in ['x','q']:
            return self.do_exit(inp)
        else:
            print("\nInvalid command: "+inp.split()[0]+"\n")
            self.do_show_help(inp)

    def do_point_state_0(self,inp):
        self.__process_command(inp,"point_state_0")
        
    def do_point_state_1(self,inp):
        self.__process_command(inp,"point_state_1")
        
    def do_point_toggle(self,inp):
        self.__process_command(inp,"point_toggle")
        
    def do_point(self,inp):
        l_inp = inp.split(" ")
        if len(l_inp) > 2:
            inp = " ".join(l_inp[2:])
            if len(l_inp) > 2:
                if l_inp[0] == "state":
                    if l_inp[1] == "0":
                        self.do_point_state_0(inp)
                    elif l_inp[1] == "1":
                        self.do_point_state_1(inp)
        else:
            inp = " ".join(l_inp[1:])
            if l_inp[0] == "toggle":
                self.do_point_toggle(inp)
    
    def do_show(self,inp):
        l_inp = inp.split(" ")
        if len(l_inp) > 0:
            inp = " ".join(l_inp[1:])
            if l_inp[0] == "settings" or l_inp[0] == "status":
                self.do_show_settings(inp)
            elif l_inp[0] == "help":
                self.do_show_help(inp)
            elif l_inp[0] == "train" and len(l_inp) > 1 and l_inp[1] == "help":
                self.do_show_train_help(inp)
            else:
                print("\nInvalid command.\n")
                self.do_show_help(inp)
        else:
            print("\nInvalid command.\n")
            self.do_show_help(inp)

    def do_show_status(self,inp):
        self.track.show_settings()

    def do_show_settings(self,inp):
        self.track.show_settings()

    def do_show_help(self,inp):
        print(textwrap.dedent('''\
            <COMMAND> <OPTION> [<OPTION> ...]\n
            Where:
                <COMMAND>   One of the comands:
                                set_speed, run_for, run_until, 
                                pause, wait_for_switch, 
                                point_state_0, point_state_1, point_toggle or  
                                stop
                            Space may be used in stead of underscores in the command names
                <OPTION>    Each command requires specific options:
                            set_speed:          <SPEED> <DIRECTION> <FORCE>
                            run_for:            <SPEED> <DIRECTION> <DURATION>
                            run_until:          <SPEED> <DIRECTION> <SWITCH> <COUNT>
                            pause:              <DURATION>
                            wait_for_switch:    <SWITCH> <COUNT>
                            point_state_0:      <POINT>
                            point_state_1:      <POINT>
                            point_switch:       <POINT>
                            stop:               no options
                            Where:
                                SPEED       0 - 1
                                DIRECTION   -1 (backwards) or 1 (forward)
                                FORCE       True/False if False, gradually change speed
                                DURATION    number of seconds
                                SWITCH      Switch number as defined by the --switch options.
                                            0-based so the first --switch option is SWITCH 0
                                POINT       Point number as defined by the --point options.
                                            0-based so the first --point option is POINT 0
                                COUNT       Number of times the switch should be triggered
            '''))

    def do_show_train_help(self,inp):
        self.track.help()

    def help_exit(self):
        print('exit the application. Shorthand: exit, x, q or Ctrl-D.')

    def help_set(self):
        print("set_speed and set_track can also be used with a space instead of an underscore")

    def help_run(self):
        print("run_for, run_until and run_script can also be used with a space instead of an underscore")

    def help_show(self):
        print("show_settings/show_status, show_help and show_train_help can also be used with a space instead of an underscore")

    def help_point(self):
        print("point_state_0/point_state_1, point_toggle can also be used with a space instead of an underscore")
    def help_wait(self):
        print("wait_for_switch can also be used with a space instead of an underscore")

    def help_set_speed(self):
        print("set_speed <SPEED> <DIRECTION>")

    def help_set_track(self):
        print("set_track <TRACK NR>")

    def help_show_help(self):
        print("show extensive help")

    def help_show_train_help(self):
        print("show help from the track class")

    def help_show_settings(self):
        print("Show current track settings and stats")

    def help_show_status(self):
        print("Synonym for show_settings")

    def help_run_for(self):
        print("run_for <SPEED> <DIRECTION> <DURATION>")

    def help_run_until(self):
        print("run_until <SPEED> <DIRECTION> <SWITCH> <COUNT>")

    def help_pause(self):
        print("pause <DURATION>")

    def help_wait_for_switch(self):
        print("wait_for_switch <SWITCH>")

    def help_on(self):
        print("Turn the current track on if the enable pin is used")

    def help_off(self):
        print("Turn the current track off if the enable pin is used")

    def help_stop(self):
        print("stop")

    def help_point_state_0(self):
        print("point_state_0 <POINT>")
        
    def help_point_state_1(self):
        print("point_state_1 <POINT>")
        
    def help_point_toggle(self):
        print("point_toggle <POINT>")
        
    def help_run_script(self):
        print("run_script <SCRIPTFILE>")
    do_EOF = do_exit
    help_EOF = help_exit

if __name__ == '__main__':
    print("This Python script can not be used standalone.")
