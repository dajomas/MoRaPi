okIgnore = -999
errNoValue = -1000
errValueError = -1001
errIndexError = -1002

class run_train(object):
    def check_option(self, options, optnr, dofloat=False, doBool=False):
        retval = errNoValue
        oldval = errNoValue
        try:
            if dofloat:
                retval = float(options[optnr])
            elif doBool:
                retval = bool(options[optnr])
            else:
                retval = int(options[optnr])
        except ValueError:
            retval = errValueError
            oldval = options[optnr]
        except IndexError:
            retval = errIndexError
        if retval in [errIndexError,errNoValue] and doBool:
            retval = False
        return [retval,oldval]

    def check_value(self, cmd_list, cmd_line, value, type):
        __type = str(type).upper()
        Err = ''
        if self.__debug > 1:
            print("Checking value for cmd_line ("+str(cmd_line)+") ("+type+"): ")
            print(value)
        if value[0] in [errIndexError,errNoValue]:
            Err = ': value for '+__type+': is missing'
        else:
            if value[0] == errValueError:
                Err = ': invalid value for '+__type+': '+str(value[1])
            elif __type == 'SPEED':
                if (round(value[0],0) != okIgnore and not(round(value[0],3) >= 0 and round(value[0],3) <= 1)):
                    Err = ': invalid value for '+__type+': '+str(value[0])
            elif __type == 'DIRECTION':
                if (value[0] != okIgnore and value[0] != -1 and value[0] != 0 and value[0] != 1):
                    Err = ': invalid value for '+__type+': '+str(value[0])
            else:
                if (value[0] != okIgnore and value[0] < 0):
                    Err = ': invalid value for '+__type+': '+str(value[0])
        if Err != '':
            cmd_list.append(str(cmd_line)+str(Err))
        return cmd_list

    def verify_program(self, cmd_line_options):
        cmd_list = {'ERRORS': [], 'CMDS': []}
        cmd_line = 0
        for cmd in cmd_line_options:
            cmd_line += 1
            if len(cmd) == 0:
                continue
            if self.__debug > 1:
                print("Processing command:")
                print(cmd)
            if cmd[0] in cmd_list['CMDS']:
                cmd_list['ERRORS'].append(str(cmd_line)+': Order '+str(cmd[0])+' already exists.')
            else:
                cmd_list['CMDS'].append(cmd[0])
                __point = [okIgnore,okIgnore]
                __track = [okIgnore,okIgnore]
                __force = [okIgnore,okIgnore]
                __speed = [okIgnore,okIgnore]
                __direction = [okIgnore,okIgnore]
                __duration = [okIgnore,okIgnore]
                __sensor = [okIgnore,okIgnore]
                __count = [okIgnore,okIgnore]
                if cmd[1] == 'set_track':
                    __track = self.check_option(cmd,2,False)
                elif cmd[1] == 'set_speed':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                    __force = self.check_option(cmd,4,doBool=True)
                elif cmd[1] == 'run_for':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                    __duration = self.check_option(cmd,4)
                elif cmd[1] == 'run_until':
                    __speed = self.check_option(cmd,2,True)
                    __direction = self.check_option(cmd,3)
                    __sensor = self.check_option(cmd,4)
                    __count = self.check_option(cmd,5)
                elif cmd[1] == 'pause':
                    __duration = self.check_option(cmd,2,True)
                elif cmd[1] == 'wait_for_sensor':
                    __sensor = self.check_option(cmd,2)
                    __count = self.check_option(cmd,3)
                elif cmd[1] == "point_state_0" or cmd[1] == "point_state_1" or cmd[1] == "point_toggle":
                    __point = self.check_option(cmd,2)
                elif cmd[1] not in ['stop']:
                    cmd_list['ERRORS'].append(str(cmd_line)+': Unknwon command '+str(cmd[1])+'.')

                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__track,'TRACK')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__speed,'SPEED')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__direction,'DIRECTION')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__duration,'DURATION')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__sensor,'SENSOR')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__count,'COUNT')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__point,'POINT')
                cmd_list['ERRORS'] = self.check_value(cmd_list['ERRORS'],cmd_line,__force,'FORCE')

        return cmd_list['ERRORS']

    def run_program(self, t, cmd_line_options):
        cmd_line = 0
        for cmd in sorted(cmd_line_options, key=lambda x:x[0]):
            if self.__debug > 0:
                print("Executing command: "+" ".join(str(x) for x in cmd))
            cmd_line += 1
            if cmd[1] == 'set_track':
                __track = self.check_option(cmd,2,False)[0]
                t.set_track(__track)
            elif cmd[1] == 'set_speed':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                __force = self.check_option(cmd,4,doBool=True)[0]
                t.set_speed(__speed, __direction, __force)
            elif cmd[1] == 'run_for':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                __duration = self.check_option(cmd,4)[0]
                t.run_for(__speed, __direction, __duration)
            elif cmd[1] == 'run_until':
                __speed = self.check_option(cmd,2,True)[0]
                __direction = self.check_option(cmd,3)[0]
                __sensor = self.check_option(cmd,4)[0]
                __count = self.check_option(cmd,5)[0]
                t.run_until(__speed, __direction, __sensor, __count)
            elif cmd[1] == 'pause':
                __duration = self.check_option(cmd,2,True)[0]
                t.pause(__duration)
            elif cmd[1] == 'wait_for_sensor':
                __sensor = self.check_option(cmd,2)[0]
                __count = self.check_option(cmd,3)[0]
                t.wait_for_sensor(__sensor, __count)
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
        self.__debug = debug
        error_list = self.verify_program(cmd_options)
        if len(error_list) > 0:
            print("Errors found in commands:")
            for Err in error_list:
                print(Err)
            return False
        else:
            return self.run_program(t, cmd_options)

if __name__ == '__main__':
    print("This Python script can not be used standalone.")
