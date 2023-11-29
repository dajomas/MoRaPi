#!/usr/bin/python3
import argparse
import textwrap

from run import run_track
from itrack import iTrack
from railway import Track
from defaults import *

DEBUG = 0

# Demo program - normally import this in which case this won't run
def demo0(e):
    e.run_for(0.2,e.go_forward,5)
    e.run_for(0.3,e.go_forward,5)
    e.run_for(0.9,e.go_forward,5)
    e.run_for(0.5,e.go_forward,5)
    e.run_for(0.5,e.go_backward,5)
    e.run_for(0.4,e.go_backward,5)
    e.run_for(0.2,e.go_backward,5)
    e.run_for(0.9,e.go_backward,5)
    e.run_for(0.5,e.go_backward,5)
    e.stop()

def process_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(help_text))

    parser.add_argument('-v','--v','--verbose', dest='debug', action='count', default=0, help="increase verbosity, more v's is more output (default: 0)")
    parser.add_argument('--name', dest='name', type=str, action='store', default='track', help='Name of the track (default: track)')

    parser.add_argument('-f','--f','--function', choices=['set_speed','run_for','run_until','demo','program','script','interactive'], type=str, dest='function', default='interactive', help='Function to run (default: interactive)')

    parser.add_argument('--host', dest='host', type=str, action='store', default='localhost', help='Name of the host that runs pigpiod (default: localhost)')
    parser.add_argument('--port', dest='port', type=int, action='store', default=8888, help='Port on which pigpio is listening (default: 8888)')

    parser.add_argument('--steps', dest='steps', type=int, action='store', default=10, help='Number of steps to go from MIN/MAX to MAX/MIN (default: 10)')
    parser.add_argument('--ctime', dest='ctime', type=int, action='store', default=5, help='Number of seconds to go from MIN/MAX to MAX/MIN (default: 5)')

    parser.add_argument('--list-presets', dest='list_presets', default=False, action='store_true',help='List all available presets (use the preset number with --preset)')
    parser.add_argument('--preset', dest='presets', action='append', type=int, default=[], help='use predefined presets to configure a track segment (can be used multiple times)')
    parser.add_argument('--fwd', dest='pin_fwd', type=int, action='store', default=17, help='GPIO number of the forward pin (default: 17) (ignored if --track is used)')
    parser.add_argument('--rev', dest='pin_rev', type=int, action='store', default=18, help='GPIO number of the backward pin (default: 18) (ignored if --track is used)')
    parser.add_argument('--enable', dest='pin_enable', type=int, action='store', default=None, help='GPIO number of the enable pin (default: None) (ignored if --track is used)')
    parser.add_argument('--track', nargs='*', type=int, action='append', dest='tracks', default=[], help='Define track as <fwd-pin> <rev-pin> [<enable-pin>]')
    parser.add_argument('-s','--s','--sensor', dest='sensor_pins', type=int, action='append', default=[], help='GPIO number of a sensor, can be specified multiple times, for run_until uses the first sensor, so at least one is required (default: [])')
    parser.add_argument('-p','--p','--point', dest='point_pins', type=int, action='append', default=[], help='GPIO number of a point, can be specified multiple times (default: [])')

    parser.add_argument('--speed', dest='speed', type=float, action='store', default=1, help='for set_speed, run_for and run_until (default: 1)')
    parser.add_argument('--direction', dest='direction', type=str, choices=valid_direction, action='store', default=1, help='-1 is backwards, 1 is forward, for set_speed, run_for and run_until (default: 1)')
    parser.add_argument('--duration', dest='duration', type=int, action='store', default=10, help='duration in seconds, for run_for only (default: 10)')
    parser.add_argument('--count', dest='count', type=int, action='store', default=1, help='Number of time the sensor should be passed before triggering, for run_until only (default: 1)')

    parser.add_argument('--script', dest='script', type=argparse.FileType('r'), help='scriptfile containing a command per line. (See explanation below)')
    parser.add_argument('--program', nargs='*', action='append', dest='cmd_options', help='run set_speed, run_for or run_until with options. (See explanation below)')
    parser.add_argument('--save', dest='file', type=argparse.FileType('w'), help='Save program steps to file (only use with program)')

    return parser.parse_args()

def main():
    args = process_args()

    DEBUG = args.debug

    if args.list_presets:
        count = 0
        for preset in presets:
            if len(preset) == 4:
                enable = preset[3]
            else:
                enable = 'None'
            print(str(count)+' => '+preset[0]+' (fwd: '+str(preset[1])+', rev:'+str(preset[2])+', enable: '+str(enable)+')')
            count += 1
        return

    if len(args.presets) > 0:
        for preset in args.presets:
            args.tracks.append(presets[preset][1:])

    if DEBUG > 1:
        print(args)

    t = Track(name=args.name,
               host=args.host, port=args.port,
               pin_enable=args.pin_enable, pin_fwd=args.pin_fwd, pin_rev=args.pin_rev,
               tracks=args.tracks,
               steps=args.steps, ctime=args.ctime,
               sensor_pins=args.sensor_pins, point_pins=args.point_pins,
               debug=args.debug)

    if not t.is_ok():
        print('Failed to initialize. Exiting...')
    elif args.function == 'demo':
        if DEBUG > 0:
            print('Starting demo')
        demo0(t)
    elif args.function == 'set_speed':
        if DEBUG > 0:
            print('Set speed to '+str(round(args.speed,3))+' going '+t.which_direction_is(args.direction))
        t.set_speed(args.speed, args.direction)
    elif args.function == 'run_for':
        if DEBUG > 0:
            print('Set speed to '+str(round(args.speed,3))+' going '+t.which_direction_is(args.direction)+' and run for '+str(args.duration)+' seconds')
        t.run_for(args.speed, args.direction, args.duration)
    elif args.function == 'run_until':
        if len(args.sensor_pins) == 0:
            print('At least one sensor should be define if you use the run_until function')
            args.print_help()
        else:
            if DEBUG > 0:
                print('Set speed to '+str(round(args.speed,3))+' going '+t.which_direction_is(args.direction)+' and the sensor at GPIO pin '+str(args.sensor_pins[0])+' triggers '+str(args.count)+' times')
            t.run_until(args.speed, args.direction, sensor_nr=args.sensor_pins[0], count=args.count)
    elif args.function == 'program':
        run = run_track()
        if run.process_commands(t, args.cmd_options, DEBUG) and args.file is not None:
            args.file.write('\n'.join([' '.join(map(str,one_cmd)) for one_cmd in args.cmd_options]))
            args.file.write('\n')
            args.file.close()
    elif args.function == 'script':
        script_content = args.script.read()
        args.script.close()
        script_list = script_content.split('\n')
        cmd_list = []
        for line in script_list:
            if len(line.split()) > 0 and line[0] != '#':
                cmd_list.append(line.split())
        if DEBUG > 1:
            print('Read commands from file:')
            print(cmd_list)
        run = run_track()
        run.process_commands(t, cmd_list, DEBUG)
    elif args.function == 'interactive':
        iTrack(track=t, debug=DEBUG).cmdloop()

    # demo0()

#Run the main function when this program is run
if __name__ == '__main__':
    main()