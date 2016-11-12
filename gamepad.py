import sdl2
import os

def SDL_JoystickGetGUIDString(guid):
    s = ''
    for g in guid.data:
        s += "{:x}".format(g >> 4)
        s += "{:x}".format(g & 0x0F)
    return s

class GamePad(object):
    def __init__(self, joystick):
        self.js = joystick

        sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER)
        js = sdl2.joystick.SDL_JoystickOpen(self.js.get_id())
        guid = sdl2.joystick.SDL_JoystickGetGUID(js)
        my_guid = SDL_JoystickGetGUIDString(guid)

        self.name = self.js.get_name()
        print 'joystick name:', self.js.get_name(), my_guid

        self.buttons = {}
        self.axis = {}
        numhats = self.js.get_numhats()
        if numhats > 0:
            self.hats = 1
        else:
            self.hats = None

        path = os.path.abspath(__file__)
        path = os.path.dirname(path)
        path = os.path.join(path, 'gamecontrollerdb.txt')

        with open(path) as f:
            for l in f.readlines():
                l = l.strip()
                if l.startswith('#'):
                    continue
                # 341a3608000000000000504944564944,Afterglow PS3 Controller,a:b1,b:b2,back:b8,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,
                #    guide:b12,leftshoulder:b4,leftstick:b10,lefttrigger:b6,leftx:a0,lefty:a1,rightshoulder:b5,rightstick:b11,righttrigger:b7,rightx:a2,righty:a3,start:b9,x:b0,y:b3,platform:Windows,
                tokens = l.split(',')
                #print tokens
                guid = tokens[0]
                if guid != my_guid:
                    continue

                self.guid = guid
                self.name2 = tokens[1]

                for pair in tokens[2:]:
                    pair = pair.strip()
                    if not pair:
                        continue
                    key, val = pair.split(':')
                    if key == 'platform':
                        self.platform = val
                    else:
                        if val.startswith('a'):
                            self.axis[key] = int(val[1:])
                        elif val.startswith('b'):
                            self.buttons[key] = int(val[1:])
                        else:
                            print 'unrecognized pair: ', key, val
                break

        sdl2.SDL_Quit()

        self.dump_definition()

    def dump_definition(self):
        print 'name', self.name
        print 'name2', self.name2
        print 'guid', self.guid
        print self.axis
        print self.buttons

    def dump_state(self):
        ta = "Axis"
        for a, idx in sorted(self.axis.iteritems()):
            ta += ' %s:%s,' % (a, self.js.get_axis(idx))
        tb = "Buttons"
        for b, idx in sorted(self.buttons.iteritems()):
            tb += ' %s[%s]:%s,' % (b, idx, self.js.get_button(idx))
        print ta
        print tb

    def dump_info(self):
        hats_cnt = self.js.get_numhats()
        print "Hats: %d" % hats_cnt

    def is_pressed(self, button, event=None):
        if self.hats and button.startswith('dp'):
            dp = self.js.get_hat(0)
            if button == 'dpup' and dp[1] == 1:
                return True
            elif button == 'dpdown' and dp[1] == -1:
                return True
            elif button == 'dpleft' and dp[0] == -1:
                return True
            elif button == 'dpright' and dp[0] == 1:
                return True
            return False

        idx = self.buttons[button]
        if event:
            return event.button == idx
        else:
            return self.js.get_button(idx)

    def get_axis(self, axis):
        idx = self.axis[axis]
        return self.js.get_axis(idx)


if __name__ == '__main__':
    import pygame
    import time
    pygame.init()
    pygame.joystick.init()
    cnt = pygame.joystick.get_count()
    print 'joystick count:', cnt
    if cnt > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        gp = GamePad(joystick)
        gp.dump_info()
        while True:
            pygame.event.pump()
            gp.dump_state()
            time.sleep(0.1)
