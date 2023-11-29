from gpiozero import Motor, Button, OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import textwrap

# maximum value is 1
MAX_SPEED = 1.0

class Track(object):

    def __init__(self, name="track",
                 host='localhost', port=8888,
                 pin_enable=None, pin_fwd=17, pin_rev=18, tracks=[],
                 max_speed=1.0, steps=10, ctime=5,
                 sensor_pins=[], point_pins=[],
                 debug=0, help=False):
        if help:
            self.help()
            return
        # private attributes
        self.__track_observers = []
        self.__speed_observers = []
        self.__direction_observers = []
        self.__sensor_observers = []

        self.__name = name
        self.__host = host
        self.__port = port
        self.__set_current_track(None)
        self.__set_current_speed(0)
        self.__set_current_direction(0)

        self.__pin_enable = pin_enable
        self.__pin_fwd = pin_fwd
        self.__pin_rev = pin_rev
        self.__tracks = tracks
        self.__max_speed = max_speed
        self.__steps = steps
        self.__ctime = ctime
        self.__sensor_pins = sensor_pins
        self.__point_pins = point_pins
        self.__debug = debug

        self.__factory = PiGPIOFactory(host=self.__host, port=self.__port)
        self.__reset()
        self.__dirlist = ['backward','stop','forward']
        self.__speed_change = round(self.__max_speed / self.__steps,3)
        self.__acc_delay = round(self.__ctime / self.__steps,3)

        if len(self.__tracks) == 0:
            if self.__pin_enable == None:
                self.__tracks = [[self.__pin_fwd, self.__pin_rev]]
            else:
                self.__tracks = [[self.__pin_fwd, self.__pin_rev, self.__pin_enable]]

        if not self.__verify_pins():
            self.__reset()
            return

        if len(self.__tracks) > 0:
            if not self.__init_tracks():
                self.__reset()
                return
        else:
            self.__reset()
            return
        self.__init_sensors()
        self.__init_points()

        # public attributes
        self.go_forward = 1
        self.go_backward = -1
        self.go_stop = 0
        self.force_stop = 99

    @property
    def name(self) -> str:
        """Return the name of the track"""
        return self.__name

    @property
    def speed(self) -> int:
        return self.__current_speed

    @property
    def direction(self) -> int:
        return self.__current_direction

    @property
    def direction_str(self) -> str:
        return self.__which_direction_is(self.__current_direction)

    @property
    def tracks(self) -> list:
        return self.__tracks

    @property
    def sensors(self) -> list:
        return self.__sensor_pins

    @property
    def points(self) -> list:
        return self.__point_pins

    # Private methods
    def __reset(self):
        self.__choo_choos = []
        self.__on_offs = []
        self.__sensors = []
        self.__points = []
        self.__sensors_gpio = {}
        self.__points_gpio = {}
        self.__choo_choo = None
        self.__on_off = None
        self.use_enable_pin = False

    def __verify_pins(self):
        pins = {}
        ret = True
        for track in self.__tracks:
            for pin in track:
                if str(pin) in pins.keys():
                    self.__debug_print("! Duplicate pins found: GPIO"+str(pin),0)
                    ret = False
                else:
                    pins[str(pin)] = pin
        for pin in  self.__sensor_pins:
            if str(pin) in pins.keys():
                self.__debug_print("! Duplicate pins found: GPIO"+str(pin),0)
                ret = False
            else:
                pins[str(pin)] = pin
        for pin in  self.__point_pins:
            if str(pin) in pins.keys():
                self.__debug_print("! Duplicate pins found: GPIO"+str(pin),0)
                ret = False
            else:
                pins[str(pin)] = pin
        return ret

    def __init_track(self,track,count):
        self.__debug_print("* Initializeing enginge "+str(count)+" on pins GPIO"+str(track[0])+" and GPIO"+str(track[1]),0)
        self.__choo_choos.append(Motor(track[0],track[1],pin_factory=self.__factory, pwm=True))
        if len(track) == 3:
            self.__debug_print("* Initializeing enginge "+str(count)+" enable pin GPIO"+str(track[2]),0)
            self.__on_offs.append(OutputDevice(track[2],pin_factory=self.__factory))
        else:
            self.__on_offs.append(None)

    def __init_tracks(self):
        count = 0
        for track in self.__tracks:
            self.__init_track(track,count)
            count += 1
        return self.set_track(0)

    def __init_sensor(self,sensor_pin,count):
        self.__debug_print("* Initializeing sensor "+str(count)+" on pin GPIO"+str(sensor_pin),0)
        self.__sensors_gpio['GPIO'+str(sensor_pin)] = count
        self.__sensors.append(Button(sensor_pin,pin_factory=self.__factory))
        self.__sensors[count].when_released = self.__sensor_callback

    def __init_sensors(self):
        self.__max_sensors = len(self.__sensor_pins)
        count = 0
        for sensor_pin in self.__sensor_pins:
            self.__init_sensor(sensor_pin,count)
            count += 1

    def __init_point(self,point_pin,count):
        self.__debug_print("* Initializeing point "+str(count)+" on pin GPIO"+str(point_pin),0)
        self.__points_gpio['GPIO'+str(point_pin)] = count
        self.__points.append(OutputDevice(point_pin,pin_factory=self.__factory))

    def __init_points(self):
        self.__max_points = len(self.__point_pins)
        count = 0
        for point_pin in self.__point_pins:
            self.__init_point(point_pin,count)
            count += 1

    def __sensor_callback(self,press):
        if press.value == 0:
            for callback in self.__sensor_observers:
                callback(press)

    def __set_current_track(self, new_track):
        self.__current_track = new_track
        for callback in self.__track_observers:
            callback(self.__current_track)

    def __set_current_speed(self, new_speed):
        self.__current_speed = new_speed
        for callback in self.__speed_observers:
            callback(self.__current_speed)

    def __set_current_direction(self, new_direction):
        self.__current_direction = new_direction
        for callback in self.__direction_observers:
            callback(self.__current_direction)

    def __speed_up (self, new_speed,direction=1, force=False):
        if new_speed > self.__max_speed:
            new_speed = self.__max_speed
        self.__debug_print("Speeding up: going "+self.__which_direction_is(direction)+" to "+str(round(new_speed*100,0))+"%",1)
        speed = self.__current_speed
        while round(speed,3) < round(new_speed,3):
            if force:
                speed = new_speed
            else:
                speed += self.__speed_change
            if speed >= 1:
                speed = 1
            self.set_speed(speed,direction)
            sleep(self.__acc_delay)

    def __slow_down (self, new_speed=0, force=False):
        if new_speed < 0:
            new_speed = 0
        self.__debug_print("Slowing down: going "+self.__which_direction_is(self.__current_direction)+" to "+str(round(new_speed*100,0))+"%",1)
        speed = self.__current_speed
        while round(speed,3) > round(new_speed,3):
            if force:
                speed = new_speed
            else:
                speed -= self.__speed_change
            if speed <= 0 :
                self.set_speed(speed,0)
            else:
                self.set_speed(speed,self.__current_direction)
            sleep(self.__acc_delay)

    def __full_stop(self):
        self.__choo_choo.stop()
        self.__set_current_direction(0)
        self.__set_current_speed(0)

    def __is_enabled(self):
        if self.use_enable_pin != None and self.__on_off.value == 0:
            return False
        else:
            return True

    def __is_valid_sensor(self, sensor_nr):
        if sensor_nr >=0 and sensor_nr < len(self.__sensor_pins):
            return True
        else:
            return False

    def __which_direction_is(self, my_direction) -> str:
        if not self.__is_enabled():
            return self.__dirlist[self.go_stop+1]
        return self.__dirlist[my_direction+1]


    def __debug_print(self, message, dbg_level=0):
        if self.__debug >= dbg_level:
            print(message)

    # Public methods
    def add_track(self,fwd_pin=None,rev_pin=None,enable_pin=None):
        if fwd_pin != None and rev_pin != None:
            if enable_pin != None:
                new_track = [fwd_pin,rev_pin,enable_pin]
            else:
                new_track = [fwd_pin,rev_pin]
            self.__tracks.append(new_track)
            if self.__verify_pins():
                self.__init_track(new_track,len(self.__choo_choos))
            else:
                remove_track = self.__tracks.pop()
        else:
            self.__debug_print("Invalid track definition")

    def add_sensor(self,sensor_pin=None):
        if sensor_pin != None:
            self.__sensor_pins.append(sensor_pin)
            if self.__verify_pins():
                self.__init_sensor(sensor_pin,len(self.__sensors))
            else:
                remove_sensor = self.__sensor_pins.pop()
        else:
            self.__debug_print("No sensor provided to add")

    def add_point(self,point_pin=None):
        if point_pin != None:
            self.__point_pins.append(point_pin)
            if self.__verify_pins():
                self.__init_point(point_pin,len(self.__sensors))
            else:
                remove_sensor = self.__point_pins.pop()
        else:
            self.__debug_print("No point provided to add")

    def sensor_id(self, pin=None):
        if 'GPIO'+str(pin) in self.__sensors_gpio.keys():
            return self.__sensors_gpio['GPIO'+str(pin)]
        else:
            return -1

    def is_ok(self):
        if self.__choo_choo != None:
            return True
        else:
            return False

    def set_track(self, track_nr=0):
        if track_nr < len(self.__choo_choos):
            self.__choo_choo = self.__choo_choos[track_nr]
            if self.__on_offs[track_nr] != None:
                self.use_enable_pin = True
                self.__on_off = self.__on_offs[track_nr]
                self.on()
            else:
                self.use_enable_pin = False
            self.__set_current_track(track_nr)
            return True
        else:
            self.__debug_print("Invalid track number: "+str(track_nr)+". Not changing track.",0)
            return False

    def bind_track(self, callback):
        self.__track_observers.append(callback)

    def bind_sensors(self, callback):
        self.__sensor_observers.append(callback)

    def bind_speed(self, callback):
        self.__speed_observers.append(callback)

    def bind_direction(self, callback):
        self.__direction_observers.append(callback)

    def on(self):
        if self.use_enable_pin != None and self.__on_off.value == 0:
            self.__debug_print("Turn track on", 1)
            self.__on_off.on()

    def off(self):
        if self.use_enable_pin != None and self.__on_off.value == 1:
            self.__debug_print("Turn track off",1)
            self.__on_off.off()

    def set_speed (self, speed=0, direction=1, force=False):
        if not self.__is_enabled():
            return
        if speed < 0:
            speed = 0
        if speed > self.__max_speed:
            speed = self.__max_speed
        self.__debug_print("* new speed = "+str(speed)+" new direction = "+str(direction),3)
        self.__debug_print("* current speed = "+str(self.__current_speed)+" current direction = "+str(self.__current_direction),3)
        if direction != self.__current_direction and direction != 0 and self.__current_direction != 0:
            self.__debug_print("Chaning direction from "+self.__which_direction_is(self.__current_direction)+" to "+self.__which_direction_is(direction),2)
            self.__slow_down()
            self.__set_current_speed(0)
            self.__set_current_direction(direction)
            self.__speed_up(speed, direction)
        elif (round(abs(self.__current_speed-speed),3) > self.__speed_change) and not force:
            self.__debug_print("Speed difference is greater than speed_change ("+str(round(abs(self.__current_speed-speed),3))+" > "+str(self.__speed_change)+")",2)
            if speed > self.__current_speed:
                self.__speed_up(speed,direction)
            elif speed < self.__current_speed:
                self.__slow_down(speed)
        else:
            self.__debug_print("Set speed "+str(round(speed*100,2))+"%; direction: "+str(self.__which_direction_is(direction)),2)
            self.__set_current_direction(direction)
            self.__set_current_speed(speed)
            if (direction == self.go_forward):
                self.__choo_choo.forward(speed)
            elif (direction == self.go_backward):
                self.__choo_choo.backward(speed)
            else:
                self.__full_stop()

    def stop(self,force=0):
        if not self.__is_enabled():
            return
        if force == self.force_stop:
            self.__full_stop()
        else:
            self.__slow_down(0)

    def pause(self, delay):
        self.__debug_print("Wait for "+str(delay)+" second",1)
        sleep(delay)

    def run_for(self, speed=1, direction=1, delay=10):
        if not self.__is_enabled():
            return
        self.set_speed(speed,direction)
        self.pause(delay)
        self.stop()

    def run_until(self, speed=1, direction=1, sensor_nr=0, count=1):
        if not self.__is_enabled():
            return
        if not self.__is_valid_sensor(sensor_nr):
            self.__debug_print("Invalid sensor: "+str(sensor_nr),0)
            return
        self.set_speed(speed,direction)
        self.wait_for_sensor(sensor_nr,count)
        self.stop()

    def wait_for_sensor(self,sensor_nr=0,count=1):
        if not self.__is_enabled():
            return
        if not self.__is_valid_sensor(sensor_nr):
            self.__debug_print("Invalid sensor: "+str(sensor_nr),0)
            return
        if sensor_nr < self.__max_sensors:
            counter = count
            while counter > 0:
                self.__debug_print("sensor "+str(sensor_nr)+" to pass "+str(counter)+" times",1)
                self.__sensors[sensor_nr].wait_for_press()
                self.__sensors[sensor_nr].wait_for_release()
                counter -= 1
                if counter > 0:
                    self.pause(1)

    def point_state_0(self, point_nr):
        self.__debug_print("Point "+str(point_nr)+" to state 0",1)
        if point_nr < self.__max_points:
            if self.__points[point_nr].value == 1:
                self.__points[point_nr].off()

    def point_state_1(self, point_nr):
        self.__debug_print("Point "+str(point_nr)+" to state 1",1)
        if point_nr < self.__max_points:
            if self.__points[point_nr].value == 0:
                self.__points[point_nr].on()

    def point_toggle(self, point_nr):
        self.__debug_print("Point "+str(point_nr)+" to toggle (from state "+str(self.__points[point_nr].value)+")",1)
        if point_nr < self.__max_points:
            self.__points[point_nr].toggle()

    def show_settings(self):
        print("Settings:")
        print("  track name:                        "+self.__name)
        print("  Host:                              "+self.__host)
        print("  Port:                              "+str(self.__port))
        print("  Current track:                     "+str(self.__current_track))
        if self.__current_track != None:
            print("    Forward GPIO pin: "+str(self.__tracks[self.__current_track][0]))
            print("    Reverse GPIO pin: "+str(self.__tracks[self.__current_track][1]))
            if len(self.__tracks[self.__current_track]) == 3:
                print("    Enable GPIO pin:  "+str(self.__tracks[self.__current_track][2]))
                print("    Enable status:    "+str(self.__on_offs[self.__current_track].value))
        print("  Max speed:                         "+str(self.__max_speed))
        print("  Accelleration/Decelleration steps: "+str(self.__steps))
        print("  Accelleration/Decelleration time:  "+str(self.__ctime))
        print("  - Speed change per step:           "+str(round(self.__speed_change,3)))
        print("  - Delay per speed change step:     "+str(round(self.__acc_delay,3)))
        print("  sensor pins:                       "+" ".join(str(x) for x in self.__sensor_pins))
        print("  Debug level:                       "+str(self.__debug))
        print("")
        print("Current stats:")
        print("  Available tracks:")
        count = 0
        for track in self.__tracks:
            print("    track: "+str(count))
            print("      Forward GPIO pin: "+str(track[0]))
            print("      Reverse GPIO pin: "+str(track[1]))
            if len(track) == 3:
                print("      Enable GPIO pin:  "+str(track[2]))
            count += 1
        print("  Available sensore pins:")
        count = 0
        for pin in self.__sensor_pins:
            print("    sensor "+str(count)+" on GPIO"+str(pin))
            count += 1
        print("  Available points:")
        count = 0
        for pin in self.__point_pins:
            print("    Point "+str(count)+" on GPIO"+str(pin)+" (status "+str(self.__points[count].value)+")")
            count += 1
        print("  Current speed:     "+str(round(self.__current_speed,3)))
        print("  Current direction: "+self.__which_direction_is(self.__current_direction))

    def help(self):
        print(textwrap.dedent('''\
            Initialize a track:

            t = track(name, host, port, pin_enable, pin_fwd, pin_rev, tracks, max_speed, steps, ctime, sensor_pins, point_pins debug, help)
            Where:
                name of the instance (default=track)
                host is the system running pigpiod (default=localhost)
                port is the port pigpiod listens to (default=8888)
                pin_enable is the gpio pin# to enable the motor (default=None)
                pin_fwd is the gpio pin# for forward (default=17)
                pin_rev is the gpio pin# for backword (default=18)
                tracks is a list of lists, each sublist contains the forward pin, reverse pin and optionally the enable pin
                    if empty, pin_fwd, pin_rev and pin_enable will be used
                max_speed is the highest allowed speed setting (default=1)
                steps is the number of steps taken to accelerate for 0 to max_speed and
                    to decellerate from max_speed to 0
                ctime is the number of seconds taken to accelerate for 0 to max_speed and
                    to decellerate from max_speed to 0
                sensor_pins is a list of gpio pin numbers that are connected to sensors (default empty)
                point_pins is a list of gpio pin numbers that are connected to point motor relays (default empty)
                if debug is greater than 0 messages are printed (higher number is more messages

            * <direction> can be c.go_forward, c.go_backward or c.go_stop
            > Set track speed and direction
                t.set_speed(<Speed>, <direction>, <force>)
            > Run for a specific time and slow to stop
                t.run_for(<Speed (1)>,<direction (c.go_forward)>,<duration is seconds> (10))
            > Run until a sensor is passed 'count' number of times
                t.run_until(<Speed (1)>,<direction (c.go_forward)>,<sensor# (0)>,<count (1)>
            > slow the track down to stop
                t.stop()
            > emergency stop
                t.stop(t.force_stop)
            > wait for a specific time
                t.pause(<duration in seconds>)

            > Set point to state 0
                t.point_state_0(<point_nr>)
            > Set point to state 1
                t.point_state_1(<point_nr>)
            > Toggle point state
                t.point_toggle(<point_nr>)

            > Add another track, sensor or point after initialization
                t.add_track(<forward pin>, <reverse pin>[, <enable pin>])
                t.add_sensor(<sensor pin>)
                t.add_point(<point pin>)

            > Add callback function to monitor track, sensors, speed and direction. Can be called multiple times to add multiple callback functions.
              Each time speed or direction changes, a different track is activated or a sensor is triggered, all bound functions are called with the new speed or direction, the track number or the sensor object as argument
                t.bind_track(<function>)
                t.bind_sensor(<function>)
                t.bind_speed(<function>)
                t.bind_direction(<function>)

            > Show current settings
                t.show_settings()
            > sensor tracks (if multiple tracks are provided via the tracks parameter)
                t.set_track(<track_nr>)
            > Turn track on if an enable pin is used
                t.on()
            > Turn track off if an enable pin is used
                t.off()
        '''))

