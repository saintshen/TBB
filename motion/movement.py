import argparse
import brickpi3
import time

BP = brickpi3.BrickPi3()

def Move(speed, steer=0, m_time=1):
    
    BP.set_motor_power(BP.PORT_A, -speed+steer)
    BP.set_motor_power(BP.PORT_D, -speed-steer)
    time.sleep(m_time)
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, 0)

def _main():
    parser = argparse.ArgumentParser(description='Movement brickpi3 motor')
    parser.add_argument('--speed', type=int, default=20)
    parser.add_argument('--steer', type=int, default=0)
    parser.add_argument('--time', type=int, default=1)
    args = parser.parse_args()
    Move(speed=args.speed, steer=args.steer, m_time=args.time)

if __name__ == '__main__':
    _main()