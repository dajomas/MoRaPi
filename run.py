okIgnore = -999
errNoValue = -1000
errValueError = -1001
errIndexError = -1002

class run_train(object):
    def check_option(self, options, optnr, dofloat=False):
        retval = errNoValue
        oldval = errNoValue
        try:
            if dofloat:
                retval = float(options[optnr])
            else:
                retval = int(options[optnr])
        except ValueError:
            retval = errValueError
            oldval = options[optnr]
        except IndexError:
            retval = errIndexError
        return [retval,oldval]

    def verify_program(self, cmd_line_options, debug):
        cmd_list = {'ERRORS': [], 'CMDS': []}
        cmd_line = 0
        for cmd in cmd_line_options:
            cmd_line += 1
            if len(cmd) == 0:
                continue
            if debug > 1:
                print("Processing command:")
                print(cmd)
            if cmd[0] in cmd_list['CMDS']:
                cmd_list['ERRORS'].append(str(cmd_line)+': Order '+str(cmd[0])+' already exists.')
            else:
                cmd_list['CMDS'].append(cmd[0])
                __point = [okIgnore,okIgnore]
                __track = [okIgnore,okIgnore]
                __speed = [okIgnore,okIgnore]
                __direction = [okIgnore,okIgnore]
                __duration = [okIgnore,okIgnore]
                __switch = [okIgnore,okIgnore]
                __count = [okIgnore,okIgnore]
                if cmd[1] == 'set_track':
                    __track = self.check_option(cmd,2,False)
                elif cmd[1] == 'set_speed':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                elif cmd[1] == 'run_for':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                    __duration = self.check_option(cmd,4)
                elif cmd[1] == 'run_until':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                    __switch = self.check_option(cmd,4)
                    __count = self.check_option(cmd,5)
                elif cmd[1] == 'pause':
                    __duration = self.check_option(cmd,2,True)
                elif cmd[1] == 'wait_for_switch':
                    __switch = self.check_option(cmd,2)
                    __count = self.check_option(cmd,3)
                elif cmd[1] == "point_state_0" or cmd[1] == "point_state_1" or cmd[1] == "point_toggle":
                    __point = self.check_option(cmd,2)
                elif cmd[1] not in ['stop']:
                    cmd_list['ERRORS'].append(str(cmd_line)+': Unknwon command '+str(cmd[1])+'.')

                if __track[0] in [errIndexError,errNoValue] :
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for TRACK is missing')
                elif __track[0] == errValueError or (__track[0] != okIgnore and __track[0] < 0):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for TRACK.'+str(__track[1]))

                if __speed[0] in [errIndexError,errNoValue] :
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for SPEED is missing')
                elif __speed[0] == errValueError or (round(__speed[0],0) != okIgnore and not(round(__speed[0],3) >= 0 and round(__speed[0],3) <= 1)):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for SPEED.'+str(__speed[1]))

                if __direction[0] in [errIndexError,errNoValue]:
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for DIRECTION is missing')
                elif __direction[0] == errValueError or (__direction[0] != okIgnore and __direction[0] != -1 and __direction[0] != 0 and __direction[0] != 1):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for DIRECTION '+str(__direction[1]))

                if __duration[0] in [errIndexError,errNoValue]:
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for DURATION is missing')
                elif __duration[0] == errValueError or (__duration[0] != okIgnore and __duration[0] < 0):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for DURATION '+str(__duration[1]))

                if __switch[0]in [errIndexError,errNoValue]:
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for SWITCH is missing')
                elif __switch[0] == errValueError or (__switch[0] != okIgnore and __switch[0] < 0):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for SWITCH '+str(__switch[1]))

                if __count[0] in [errIndexError,errNoValue]:
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for COUNT is missing')
                elif __count[0] == errValueError or (__count[0] != okIgnore and __count[0] < 0):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for COUNT '+str(__count[1]))

                if __point[0]in [errIndexError,errNoValue]:
                    cmd_list['ERRORS'].append(str(cmd_line)+': value for POINT is missing')
                elif __point[0] == errValueError or (__point[0] != okIgnore and __point[0] < 0):
                    cmd_list['ERRORS'].append(str(cmd_line)+': invalid value for POINT '+str(__switch[1]))

        return cmd_list['ERRORS']

    def run_program(self, t, cmd_line_options, debug):
        cmd_line = 0
        for cmd in sorted(cmd_line_options, key=lambda x:x[0]):
            if debug > 0:
                print("Executing command: "+" ".join(str(x) for x in cmd))
            cmd_line += 1
            if cmd[1] == 'set_track':
                __track = self.check_option(cmd,2,False)[0]
                t.set_track(__track)
            elif cmd[1] == 'set_speed':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                t.set_speed(__speed, __direction)
            elif cmd[1] == 'run_for':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                __duration = self.check_option(cmd,4)[0]
                t.run_for(__speed, __direction, __duration)
            elif cmd[1] == 'run_until':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                __switch = self.check_option(cmd,4)[0]
                __count = self.check_option(cmd,5)[0]
                t.run_until(__speed, __direction, __switch, __count)
            elif cmd[1] == 'pause':
                __duration = self.check_option(cmd,2,True)[0]
                t.pause(__duration)
            elif cmd[1] == 'wait_for_switch':
                __switch = self.check_option(cmd,2)[0]
                __count = self.check_option(cmd,3)[0]
                t.wait_for_switch(__switch, __count)
            elif cmd[1] == 'stop':
                t.stop()
            elif cmd[1] == "point_state_0":
                __point = self.check_option(cmd,2)[0]
                t.point_state_0(__point) 
            elif cmd[1] == "point_state_1":
                __point = self.check_option(cmd,2)[0]
                t.point_state_1(__point) 
            elif cmd[1] == "point_toggle":
                __point = self.check_option(cmd,2)[0]
                t.point_toggle(__point) 
        return True

    def process_commands(self, t, cmd_options, debug):
        error_list = self.verify_program(cmd_options, debug)
        if len(error_list) > 0:
            print("Errors found in commands:")
            for Err in error_list:
                print(Err)
            return False
        else:
            return self.run_program(t, cmd_options, debug)

if __name__ == '__main__':
    print("This Python script can not be used standalone.")
