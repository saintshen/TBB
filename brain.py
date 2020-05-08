from aiy.board import Board, Led
from aiy.voice.tts import say
import serial

arduino = serial.Serial("/dev/ttyACM0",9600)
arduino.baudrate=9600

def say_hello():
    say("hello")

def say_something(something):
    say(something)

def go_forward():
    print("Go Forward\n")
    arduino.write(b'Go Forward\n')

def main():
    print('Test is running(Ctrl-C for exit).')
    say_hello()
    with Board() as board:
        board.button.when_released = go_forward
        while True:
            msg=arduino.readline().decode('ascii').strip()
            say_something(msg)
            if (msg == 'Hello From Arduino!'):
                board.led.state = Led.ON
            board.button.wait_for_press()

if __name__ == '__main__':
    main()

