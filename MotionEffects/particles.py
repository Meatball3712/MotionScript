# Translate
from base import Effect
from PIL import Image
import random

class Particle:
    """ A single Particle """
    def __init__(self, x, y, z=0, vx=0, vy=0, vz=0, mass=1, ax=0, ay=0, az=0, drag=0):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.ax = ax
        self.ay = ay
        self.az = az
        self.drag = drag # Drag Factor = 0.5 * (Drag Coefficient) * (mass density of fluid) * (Reference Area): 0 = no drag

    def applyForce(self, fx, fy, fz):
        """ Move particle according to force vector """
        #Units are per pixel and per frame so accelleration = p/f^2
        # a = F/M
        self.ax += fx/self.mass
        self.ay += fy/self.mass
        self.az += fz/self.mass

    def applyAccelleration(self, ax, ay, az):
        """ Apply additional accelleration """
        self.ax += ax
        self.ay += ay
        self.az += az

    def setAccelleration(self, ax, ay, az):
        """ Set Constant Accelleration """
        self.ax = ax
        self.ay = ay
        self.az = az

    def setVelocity(self, vx, vy, vz):
        """ Set Velocity """
        self.ax

    def applyDrag(self):
        """ Calculate drag and apply force accordingly """
        fx = -1.0 * self.drag * (self.vx**2)
        fy = -1.0 * self.drag * (self.vy**2)
        fz = -1.0 * self.drag * (self.vz**2)
        self.applyForce(fx, fy, fz)

    def step(self):
        # S = ut + 1/2at^2, t=1
        self.x = int(round(self.vz + 0.5*self.ax))
        self.Y = int(round(self.vy + 0.5*self.ay))
        self.z = int(round(self.vz + 0.5*self.az))
        self.vx += self.ax
        self.vx += self.ax
        self.vx += self.ax

class Emitter(Effect):
    """ Defines a particle emission field that new particles might emerge from """

    def __init__(self, sx, sy, sz, ex, ey, ez, rate, vx=0, vy=0, vz=0, ax=0, ay=0, az=0, preload=0, **kwargs):
        self.sx = sx 
        self.sy = sy
        self.sz = sz
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.rate = rate
        self.particles = []
        self.emitTimer = 0

        # Initial Velocity Vector
        self.vx = vx
        self.vy = vy
        self.vz = vz

        # Set Constant Accelleration
        self.ax = ax
        self.ay = ay
        self.az = az

        # Force Functions over time.
        if(kwargs.has_key("applyForceFunction")):
            #parse a trio of functions to apply for force
            self.fn_fx = kwargs["fn_fx"]
            self.fn_fy = kwargs["fn_fx"]
            self.fn_fz = kwargs["fn_fx"]
        else:
            self.fn_fx = kwargs

        # Checks and Balances
        assert self.sx <= self.ex
        assert self.sy <= self.ey
        assert self.sz <= self.ez

        # Preload field if required.
        while self.preload > 0:
            self.generateParticles()
            self.getNextFrame()


    def generateParticles(self):
        self.emitTimer + self.rate
        numEmit = int(self.emitTimer)
        self.emitTimer = self.emitTimer % 1
        for n in xrange(numEmit):
            x = random.randint(self.sx, self.ex)
            p = Particle()

    def generateForce(self, particle, fx=0, fy=0, fz=0):
        return fx, fy, fz

    def step(self):
        """ Apply any force functions """
        pass

    def getNextFrame(self):
        """ Generate new Particles, apply forces and move particles """
        pass

"""
class Null(Effect):
    #Move an image around the screen
    def __init__(self, **kwargs):
        Effect.__init__(self, effectName="Pan", **kwargs)
        self.start_pos = kwargs.get("start_pos", [0,0])
        self.end_pos = kwargs.get("end_pos", [0,0])
        self.current_pos = self.start_pos

    def getNextFrame(self):
        asset = self.asset.getNextFrame()
        if (self.duration) > 0:
            ef = self.getEasingFactor() if self.applyEasing else 1.0
            X = int(round(self.start_pos[0] + 1.0*((self.end_pos[0] - self.start_pos[0])/self.duration) * self.current * ef))
            Y = int(round(self.start_pos[1] + 1.0*((self.end_pos[1] - self.start_pos[1])/self.duration) * self.current * ef))
            self.logger.debug("%s Pan Calculations: X=%d, Y=%d, ef=%f, current=%d", self.name, X, Y, ef, self.current)
            newAsset = Image.new(size=self.size, mode="RGBA", color=(0,0,0,0))
            newAsset.paste(asset, (X,Y))
            asset = newAsset
        self.current = (self.current+1)%(self.duration+1) if self.loop and self.duration > 0 else self.current+1
        assert isinstance(asset, Image.Image), "asset is type %s" % type(asset)
        return asset
"""

# Decorators
class drift(object):
    def __init__(self, f):
        self.fn = f
        self.fx = 0.0
        self.fy = 0.0
        self.fz = 0.0
        self.strength = 0.05


    def __call__(self, *args):
        fx, fy, fz = self.fn(*args)

        self.fx += ((1.0-(2.0*random.random())) * self.strength)
        self.fy += ((1.0-(2.0*random.random())) * self.strength)
        self.fz += ((1.0-(2.0*random.random())) * self.strength)

        fx += self.fx
        fy += self.fy
        fz += self.fz
        
        return fx, fy, fz
    
if __name__ == "__main__":

    @drift
    def test(fx, fy, fz):
        return fx,fy,fz

    for i in xrange(10):
        print test(0,0,0)

