dir_rev = ['-1','r','reverse','b','back','backward']
dir_stop = ['0','s','stop']
dir_fwd = ['1','f','forward']

valid_direction = dir_rev+dir_stop+dir_fwd

help_text = """--script and --program command format:
    <ORDER> <COMMAND> <OPTION> [<OPTION> ...]
    Where:
        <ORDER>     Number to designate the order of execution,
                    execution will run from the lowest to the highest number
        <COMMAND>   One of the comands:
                        set_speed, run_for, run_until,
                        pause, wait_for_sensor,
                        point_state_0, point_state_1, point_toggle or
                        stop
                        add_track, add_sensor, add_point
        <OPTION>    Each command requires specific options:
                    set_speed:          <SPEED> <DIRECTION> <FORCE>
                    run_for:            <SPEED> <DIRECTION> <DURATION>
                    run_until:          <SPEED> <DIRECTION> <SENSOR> <COUNT>
                    pause:              <DURATION>
                    wait_for_sensor:    <SENSOR> <COUNT>
                    point_state_0:      <POINT>
                    point_state_1:      <POINT>
                    point_toggle:       <POINT>
                    stop:               no options
                    add_track           <FORWARD PIN> <REVERSE PIN> [<ENABLE PIN>]
                    add_sensor          <SENSOR PIN>
                    add_point           <POINT PIN>
                    Where:
                        SPEED       float value between 0 (stop) and 1 (full speed)
                        DIRECTION   -1,back,b,reverse,r (backwards),
                                    0,s,stop (stop) or
                                    1,f,forward (forward)
                        FORCE       True/False if False, gradually change speed
                        DURATION    number of seconds
                        SENSOR      sensor number as defined by the --sensor options.
                                    0-based so the first --sensor option is sensor 0
                        POINT       Point number as defined by the --point options.
                                    0-based so the first --point option is POINT 0
                        COUNT       Number of times the sensor should be triggered
                        FORWARD PIN GPIO number of the forward pin
                        REVERSE PIN GPIO number of the reverse pin
                        ENABLE PIN  GPIO number of the enable pin
                        SENSOR PIN  GPIO number of the sensor pin
                        POINT PIN   GPIO number of the point pin
                        """

presets = [
    ['MotorShield Motor A',27,22,17],
    ['MotorShield Motor B',23,24,25],
    ['MotorShield Motor C',9,11,10],
    ['MotorShield Motor D',8,7,12],
]

script_name = 'model_track'
config_file_name = script_name+'.yml'
default_args = {
    'debug': 0,
    'name': 'track',
    'function': 'interactive',
    'host': 'localhost',
    'port': 8888,
    'steps': 10,
    'ctime': 5,
    'list_presets': False,
    'presets': [],
    'pin_fwd': 17,
    'pin_rev': 18,
    'pin_enable': None,
    'tracks': [],
    'sensor_pins': [],
    'point_pins': [],
    'speed': 1,
    'direction': 1,
    'duration': 10,
    'count': 1,
    'script': None,
    'cmd_options': None,
    'file': None
}