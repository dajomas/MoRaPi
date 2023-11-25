# ModelRailway for Pi controller (MoRaPi)

For detailed documentation, see the wiki at https://github.com/dajomas/MoRaPi/wiki

Prerequisites:
 * Raspberry Pi
   * pigpiod (https://abyz.me.uk/rpi/pigpio/)
   * An H-Bridge connected to te RPi (any L298N will work. I used the MotorShield from SB Components: https://shop.sb-components.co.uk/products/motorshield-for-raspberry-pi)
   * Optionally: A Relay board (like this https://www.amazon.com/4-channel-relay-module/s?k=4+channel+relay+module) if you want to use automated points
 * gpiozero (https://gpiozero.readthedocs.io/en/latest) installed on the machine from which you run the Python scripts (can be the RPi but can also be a remote machine)

First, let's give credit where credit is due. I started this project after following this page: https://www.penguintutor.com/projects/modelrailwayautomation and its accompanying Github repository https://github.com/penguintutor/model-railway/tree/main. I took it a bit further and here we are: MoRaPi

Installation is really simple.
1. On you RPi, run the following commands:
```bash
sudo apt install -y pigpio
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```
2. On the machine from which you will be running the Python3 scripts:
  a. ensure you have Python 3 running (```python3 --version```) If you don't have Python3 running, please check you OS documentation for help
  b. ensure gpiozero is installed (see https://gpiozero.readthedocs.io/en/latest/installing.html)
  c. ensure git is installed (```sudo apt install -y git``` or ```sudo yum install -y git``` are the most common ways but check your OS documentation if you are unsure)
  d. clone the MoRaPi repository: ```cd ~ && git clone https://github.com/dajomas/MoRaPi.git```
    * This will clone the repository into ~/MoRaPi
 
And that's it. Head over to the Wiki for detailed info on how to use MoRaPi

Have Fun (And please leave me some feedback, I am really looking forward to it!)
