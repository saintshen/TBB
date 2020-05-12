import argparse
import brickpi3
import time

BP = brickpi3.BrickPi3()

def Walk(speed=20):
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, -speed)
    time.sleep(1)
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, 0)

def _main():
    parser = argparse.ArgumentParser(description='Movement brickpi3 motor')
    parser.add_argument('--speed', type=int, default=20)
    args = parser.parse_args()
    Walk(speed=args.speed)

if __name__ == '__main__':
    _main()