# Translate
from base import Effect
from PIL import Image
from fade import fadeImage
import random

#####################
## Force Functions ##
#####################
class drift(object):
    """ Brownian Motion Generator """
    def __init__(self, **kwargs):
        self.strength = 0.001

    def __call__(self, particle):
        fx = ((1.0-(2.0*random.random())) * self.strength)
        fy = ((1.0-(2.0*random.random())) * self.strength)
        fz = ((1.0-(2.0*random.random())) * self.strength)
        return fx, fy, fz

class gust(object):
    """ Apply Gusts of Wind """
    def __init__(self, **kwargs):
        self.vx = kwargs.get("vx", 0)
        self.vy = kwargs.get("vy", 0)
        self.vz = kwargs.get("vz", 0)
        self.gustFactor = 0.05

    def __call__(self, particle):
        fx = ((1.0-(2.0*random.random())) * self.strength)
        fy = ((1.0-(2.0*random.random())) * self.strength)
        fz = ((1.0-(2.0*random.random())) * self.strength)
        return fx, fy, fz

class noForce(object):
    """ Default Null Force Function """
    def __init__(self, **kwargs):
        pass

    def __call__(self, particle):
        return 0.0, 0.0, 0.0

######################
##  Main Functions  ##
######################
class Particle:
    """ A single Particle """
    def __init__(self, asset, x, y, z=1.0, **kwargs):
        self.asset = asset
        # Position
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        # Velocity
        self.vx = float(kwargs.get("vx", 0))
        self.vy = float(kwargs.get("vy", 0))
        self.vz = float(kwargs.get("vz", 0))
        # Accelleration
        self.ax = float(kwargs.get("ax", 0))
        self.ay = float(kwargs.get("ay", 0))
        self.az = float(kwargs.get("az", 0))
        # Gravity
        self.gx = float(kwargs.get("gx", 0)) # Gravity / Constant Accelleration Field
        self.gy = float(kwargs.get("gy", 0)) # Gravity / Constant Accelleration Field
        self.gz = float(kwargs.get("gz", 0)) # Gravity / Constant Accelleration Field
        # Attributes
        self.mass = float(kwargs.get("mass", 1))
        self.drag = float(kwargs.get("drag", 0.0)) # Drag Factor = 0.5 * (Drag Coefficient) * (mass density of fluid) * (Reference Area): 0 = no drag
        self.ttl = kwargs.get("ttl", 120) # How long for particle to live.
        self.lock_z = kwargs.get("lock_z", False) # Lock the Z axis - No 3d
        self.perspectiveFactor = 1.0

    def setAccelleration(self, ax, ay, az):
        """ Set Constant Accelleration """
        self.ax = ax
        self.ay = ay
        self.az = az

    def setVelocity(self, vx, vy, vz):
        """ Set Velocity """
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def setGravity(self, gx, gy, gz):
        """ Set Gravity / Constant Accelleration """
        self.gx = gx
        self.gy = gy
        self.gz = gz

    def applyForce(self, fx, fy, fz):
        """ Apply Force to Particle adding Accelleration """
        #Units are per pixel and per frame so accelleration = p/f^2
        # a = F/m
        self.ax += fx/self.mass
        self.ay += fy/self.mass
        self.az += fz/self.mass

    def applyGravity(self):
        """ Apply Gravitational Accelleration to Velocity """
        self.vx += self.gx
        self.vy += self.gy
        self.vz += self.gz

    def applyAccelleration(self):
        """ Apply Accelleration to Velocity """
        self.vx += self.ax
        self.vy += self.ay
        self.vz += self.az

    def applyDrag(self):
        """ Calculate drag and apply force accordingly """
        #print "Current Vector = %f, %f, %f" % (self.vx, self.vy, self.vz)
        fx = self.drag * (self.vx**2)
        fy = self.drag * (self.vy**2)
        fz = self.drag * (self.vz**2)
        #print "Calculated Drag Force = %f, %f, %f" % (fx, fy, fz)
        fx = (-1.0 * fx) if self.vx >= 0 else fx
        fy = (-1.0 * fy) if self.vy >= 0 else fy
        fz = (-1.0 * fz) if self.vz >= 0 else fz
        #print "Calculated Force = %f, %f, %f" % (fx, fy, fz)
        self.applyForce(fx, fy, fz)

    def step(self):
        # S = ut + 1/2at^2, t=1
        #print "Applying Vectors: V: %f, %f, %f, A: %f, %f, %f" % (self.vx, self.vy, self.vz, self.ax, self.ay, self.az),
        #print " -> Before Step = ", self.x, self.y, self.z, "After Step =",
        self.applyDrag()
        self.x += self.vx + 0.5*(self.ax+self.gx)
        self.y += self.vy + 0.5*(self.ay+self.gy)
        self.z += self.vz + 0.5*(self.az+self.gz)
        self.applyGravity()
        self.applyAccelleration()
        self.ttl -= 1
        #print self.x, self.y, self.z

    def getNextFrame(self):
        self.step()
        # Return asset, resized if neccessary
        frame = self.asset.getNextFrame()

        # Scale according to z.
        if self.z > 0.0:
            width = int(round(1.0*frame.size[0]/self.z))
            height = int(round(1.0*frame.size[1]/self.z))
            frame = frame.resize( (int(round(1.0*width*self.z)), int(round(1.0*height*self.z))) )
            #frame = fadeImage(frame, 1.0 / self.z)

        return frame

class Emitter(Effect):
    """ Defines a particle emission field that new particles might emerge from """

    forceFunctions = {
        "drift" : drift,
        "gust" : gust,
        "none" : noForce
    }

    def __init__(self, asset, size, name, **kwargs):
        Effect.__init__(self, asset=asset, size=size, name=name, **kwargs)
        self.sx = kwargs["sx"]
        self.sy = kwargs["sy"]
        self.sz = kwargs["sz"]
        self.ex = kwargs["ex"]
        self.ey = kwargs["ey"]
        self.ez = kwargs["ez"]
        self.rate = kwargs["rate"]
        self.particles = []
        self.emitTimer = 0
        self.particleSettings = kwargs.get("particleSettings", {})
        self.preload = kwargs.get("preload", 0)

        # Initial Velocity Vector
        self.vx = kwargs.get("vx", 0)
        self.vy = kwargs.get("vy", 0)
        self.vz = kwargs.get("vz", 0)

        # Set Constant Accelleration
        self.ax = kwargs.get("ax", 0)
        self.ay = kwargs.get("ay", 0)
        self.az = kwargs.get("az", 0)

        # Force Functions over time.
        self.forceFunction = self.forceFunctions.get(kwargs.get("forceFunction", None), noForce)()

        # Checks and Balances
        assert self.sx <= self.ex
        assert self.sy <= self.ey
        assert self.sz <= self.ez

        # Preload field if required.
        self.logger.debug("Preloading Particles %s with %d steps", self.name, self.preload)
        while self.preload > 0:
            self.logger.debug("Stepping %d", self.preload)
            self.preload -= 1
            self.step()

    def generateParticles(self):
        self.emitTimer += self.rate
        numEmit = int(self.emitTimer)
        self.emitTimer = self.emitTimer % 1
        for n in xrange(numEmit):
            x = random.randint(self.sx, self.ex)
            y = random.randint(self.sy, self.ey)
            z = random.randint(self.sz, self.ez)
            p = Particle(self.asset, x, y, z, **self.particleSettings)
            self.particles.append(p)
            self.logger.debug("Generated Particle at %d, %d, %d", p.x, p.y, p.z)

    def generateForce(self, particle):
        fx, fy, fz = self.forceFunction(particle=particle)
        particle.applyForce(fx, fy, fz)
        return fx, fy, fz

    def step(self):
        self.generateParticles()
        particleList = []
        for particle in self.particles:
            self.generateForce(particle)
            im = particle.getNextFrame()
            # Apparent X/Y is find x,y relative to center, and /self.z
            if particle.z > 0:
                rel_x = particle.x - self.size[0]/2
                rel_y = particle.y - self.size[1]/2
                apparent_x = int(round(self.size[0]/2 + 1.0*rel_x/particle.z))
                apparent_y = int(round(self.size[1]/2 + 1.0*rel_y/particle.z))
                particleList.append((particle.z, im, (apparent_x, apparent_y)))
                self.logger.debug("Particle Position = %f, %f, %f, Rel: %d, %d, App: %d, %d", particle.x, particle.y, particle.z, rel_x, rel_y, apparent_x, apparent_y)
            else:
                self.logger.debug("Particle Position = %f, %f, %f",particle.x, particle.y, particle.z)
                continue

        # Age out particles
        for p in self.particles[:]:
            if p.ttl <0:
                self.particles.remove(p)


        particleList.sort(key=lambda x: x[0], reverse=True)
        return particleList

    def getNextFrame(self):
        """ Generate new Particles, apply forces and move particles """
        frame = Image.new(size=self.size, mode="RGBA", color=(0,0,0,0))
        particleList = self.step()
        self.logger.debug("Processing %d particles", len(particleList))
        for p in particleList:
            im2 = Image.new(size=self.size, mode="RGBA", color = (0,0,0,0))
            im2.paste(p[1], p[2])
            frame = Image.alpha_composite(frame, im2)

        return frame

#####################
##     Testing     ##
#####################
if __name__ == "__main__":
    from MotionPrimative import MotionImage
    test = noForce()
    for i in xrange(10):
        print test()