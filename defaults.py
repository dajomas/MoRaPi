dir_rev = ["-1","r","reverse","b","back","backward"]
dir_stop = ["0","s","stop"]
dir_fwd = ["1","f","forward"]

valid_direction = dir_rev+dir_stop+dir_fwd

help_text = '''--script and --program command format:
    <ORDER> <COMMAND> <OPTION> [<OPTION> ...]
    Where:
        <ORDER>     Number to designate the order of execution,
                    execution will run from the lowest to the highest number
        <COMMAND>   One of the comands:
                        set_speed, run_for, run_until, 
                        pause, wait_for_sensor, 
                        point_state_0, point_state_1, point_toggle or 
                        stop
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
                    Where:
                        SPEED       0 - 1
                        DIRECTION   -1,back,b,reverse,r (backwards), 
                                    0,s,stop (stop) or 
                                    1,f,forward (forward)
                        FORCE       True/False if False, gradually change speed
                        DURATION    number of seconds
                        SENSOR      sensor number as defined by the --sensor options.
                                    0-based so the first --sensor option is sensor 0
                        POINT       Point number as defined by the --point options.
                                    0-based so the first --point option is POINT 0
                        COUNT       Number of times the sensor should be triggered'''