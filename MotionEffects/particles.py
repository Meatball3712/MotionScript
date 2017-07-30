# Translate
from base import Effect
from PIL import Image
from fade import fadeImage
import numpy as np
import random, math

#####################
## Force Functions ##
#####################
class drift(object):
    """ Brownian Motion Generator """
    def __init__(self, **kwargs):
        self.strength = kwargs.get("strength", 0.001)
        self.mass = kwargs.get("mass", 1.0)

    def __call__(self, particles):
        field = np.random.rand(len(particles),3)
        field += np.full(field.shape, -0.5)
        field *= np.full(field.shape, self.strength/self.mass)
        return field

class gust(object):
    """ Apply Gusts of Wind """
    def __init__(self, **kwargs):
        self.fx = 0
        self.fy = 0
        self.fz = 0
        self.harshness = kwargs.get("harshness", 24) # Random Time to wait before changing thrust vector
        self.strength = kwargs.get("strength", 1.0)
        self.timer = 0

        # Checks
        assert self.harshness > 0

    def __call__(self, particles):
        if self.timer == 0:
            random.randint(0,self.harshness)
            self.fx = ((1.0-(2.0*random.random())) * self.strength)
            self.fy = ((1.0-(2.0*random.random())) * self.strength)
            self.fz = ((1.0-(2.0*random.random())) * self.strength)
        return self.fx, self.fy, self.fz

class noForce(object):
    """ Default Null Force Function """
    def __init__(self, **kwargs):
        pass

    def __call__(self, particles):
        field = np.zeros([len(particles),3])
        return field

######################
##  Main Functions  ##
######################
class Particle:
    """ A single Particle """
    def __init__(self, asset, **kwargs):
        self.asset = asset

    def getNextFrame(self):
        frame = self.asset.getNextFrame()
        return frame

class Emitter(Effect):
    """ Defines a particle emission field that new particles might emerge from """

    forceFunctions = {
        "drift" : drift,
        "gust" : gust,
        "none" : noForce,
        "default" : noForce
    }

    def __init__(self, asset, size, name, **kwargs):
        Effect.__init__(self, asset=asset, size=size, name=name, **kwargs)
        self.focalLength = float(kwargs.get("focalLength", 3000)) # Distance from chair to screen in what your pixel is equivilent of
        self.sx = kwargs["sx"]
        self.sy = kwargs["sy"]
        self.sz = kwargs["sz"]+self.focalLength
        self.ex = kwargs["ex"]
        self.ey = kwargs["ey"]
        self.ez = kwargs["ez"]+self.focalLength
        self.rate = float(kwargs["rate"])
        self.drag = float(kwargs.get("drag", 0))
        self.particles = []
        self.emitTimer = 0.0
        self.preload = kwargs.get("preload", 0)

        # Initial Velocity Vector
        self.vx = float(kwargs.get("vx", 0))
        self.vy = float(kwargs.get("vy", 0))
        self.vz = float(kwargs.get("vz", 0))

        # Physical Settings
        self.ttl = int(kwargs.get("ttl", 120)) # time to live = How long a particle exists
        self.ttd = int(kwargs.get("ttd", 0)) # time to die = linger particles for ttd while they die/fade out.
        self.ttc = int(kwargs.get("ttc", 0)) # Time to create = for fade in affect
        self.mass = float(kwargs.get("mass", 1.0))
        self.scale = float(kwargs.get("scale", 1.0))

        # Set Constant Accelleration
        self.gx = float(kwargs.get("gx", 0))
        self.gy = float(kwargs.get("gy", 0))
        self.gz = float(kwargs.get("gz", 0))

        # Force Functions over time.
        forceFunctionParameters = kwargs.get("forceFunctionParameters", {})
        forceFunctionParameters["mass"] = self.mass
        self.forceFunction = self.forceFunctions[kwargs.get("forceFunction", "default")](**forceFunctionParameters)

        # Checks and Balances
        assert self.sx <= self.ex, "sx must be less than or equal to ex"
        assert self.sy <= self.ey, "sy must be less than or equal to ey"
        assert self.sz <= self.ez, "sz must be less than or equal to ez"
        assert self.sz > 0, "FocalLength + sz must be greater than zero"
        assert self.ez > 0, "FocalLength + ez must be greater than zero"

        # Preload field if required.
        self.logger.debug("Preloading Particles %s with %d steps", self.name, self.preload)

        numpar = int(math.ceil((self.preload + self.end - self.start) * self.rate))
        # Particle = x, y, z, vx, vy, vz, scale)
        self.particleArray = np.zeros([numpar,8]) # Pre Build every array slot we'd need.
        while self.preload > 0:
            self.logger.debug("Stepping %d", self.preload)
            self.preload -= 1
            self.step()
        self.current = 0

    def generateParticles(self):
        self.emitTimer += self.rate
        numEmit = int(self.emitTimer)
        self.emitTimer = self.emitTimer % 1
        for n in xrange(numEmit):
            z = random.randint(self.sz, self.ez)
            asx = int(round(((self.sx - self.size[0]/2) * z/self.focalLength) + self.size[0]/2))
            aex = int(round(((self.ex - self.size[0]/2) * z/self.focalLength) + self.size[0]/2))
            asy = int(round(((self.sy - self.size[1]/2) * z/self.focalLength) + self.size[1]/2))
            aey = int(round(((self.ey - self.size[1]/2) * z/self.focalLength) + self.size[1]/2))
            self.logger.debug("@ z=%d, bounds are %d, %d, %d, %d", z, asx, aex, asy, aey)
            x = random.randint(asx, aex)
            y = random.randint(asy, aey)
            
            p = Particle(self.asset)
            # Particle = X, Y, Z, vx, vy, vz, scale, ttl
            pa = np.array((x,y,z,self.vx,self.vy,self.vz,self.scale,self.ttl))

            # Set array at index if possible, else append (rebuilding the array)
            if len(self.particleArray) >= len(self.particles):
                self.logger.debug("Adding particle to index %d", len(self.particles))
                self.particleArray[len(self.particles)] = pa
            else:
                self.logger.debug("Particle Array was insufficent. Appending")
                self.particleArray = np.append(self.particleArray, pa, axis=0)
            self.particles.append(p)
            
            self.logger.debug("Generated Particle at %d, %d, %d (%d,%d,%d)", pa[0], pa[1], pa[2],x,y,z)

    def generateForces(self):
        # Get Accellerations of force for alive particles
        live = np.argwhere(self.particleArray[:len(self.particles),7]>0)
        if len(live) == 0:
            return []
        else:
            live = live[0][0]
        workingSlice = self.particleArray[live:len(self.particles)]
        accellerationArray = self.forceFunction(workingSlice[:])

        #Add Gravity
        gravityArray = np.empty(accellerationArray.shape)
        gravityArray[:,0].fill(self.gx)
        gravityArray[:,1].fill(self.gy)
        gravityArray[:,2].fill(self.gz)
        # Apply Gravity
        np.add(accellerationArray,gravityArray, out=accellerationArray)
        
        # Calculate drag and apply force accordingly
        #print "Current Vector = %f, %f, %f" % (self.vx, self.vy, self.vz)
        dragArray = (self.drag * (np.power(workingSlice[:,3:6], 2))) / self.mass
        #print "Drag:", np.greater_equal(workingSlice[:,3:6], np.zeros([pCount-ttl, 3])).shape
        np.multiply(dragArray, -1.0, where=np.greater_equal(workingSlice[:,3:6], np.zeros([workingSlice.shape[0],3])), out=dragArray)
        accellerationArray += dragArray
        return accellerationArray

    def step(self):
        #print "Start = ", self.particleArray[0,0:3]
        # Age particles by one.
        live = np.argwhere(self.particleArray[:len(self.particles),7]>0)
        if len(live) > 0:
            self.particleArray[live[0][0]:len(self.particles),7] -= 1
        
        self.generateParticles()

        live = np.argwhere(self.particleArray[:len(self.particles),7]>0)
        if len(live) == 0:
            self.logger.debug("Step - No particles found - skipping")
            return []
        else:
            live = live[0][0]

        workingSlice = self.particleArray[live:len(self.particles)]
        self.logger.debug("Working slice = %d, %d", live, len(self.particles))

        #print "After Generate = ", self.particleArray[0,0:3]
        accellerationArray = self.generateForces()
        #print "After Forces = ", self.particleArray[0,0:3]
        # Move particles.
        # Particle = x, y, z, vx, vy, vz, scale
        # S += vx + 1/2a
        # print  "Check:", 
        # print workingSlice[:,:]
        # print accellerationArray
        # print ttl, pCount
        workingSlice[:,0:3] += (workingSlice[:,3:6] + accellerationArray*0.5)
        workingSlice[:,3:6] += accellerationArray

        #print "Calculating Scale"
        #print self.particleArray[0,6]
        #print np.full([pCount,1], self.focalLength)
        #print "divider = ", np.full([pCount], self.focalLength)
        #print "divisor = ", workingSlice[:,2]
        #print "equals = ", np.power(workingSlice[:,2], -1) * self.focalLength 
        workingSlice[:,6] = np.power(workingSlice[:,2], -1) * self.focalLength
        #print self.particleArray[0,6]
        #print "After Move Particle = ", self.particleArray[0,0:3]
        
        # Get Draw Order
        indexes = np.argsort(workingSlice[:,2])
        #print "After argsort = ", self.particleArray[0,0:3]
        #print indexes
        # ax = (x - width/2) * scale = scale*x - scale*width/2
        apparentCoords = np.copy(workingSlice[:,0:2])
        apparentCoords[:,0] -= self.size[0]/2 # Relative to Center
        apparentCoords[:,1] -= self.size[1]/2 # Relative to Center
        apparentCoords[:,0] *= workingSlice[:,6]
        apparentCoords[:,1] *= workingSlice[:,6]
        apparentCoords[:,0] += self.size[0]/2 # Relative to TopLeft Corner.
        apparentCoords[:,1] += self.size[1]/2 # Relative to TopLeft Corner.
        #print "After apparent Coords = ", self.particleArray[0,0:3]
        particleList = []
        for index in indexes:
            #print self.particleArray[0,0:3]
            #print "Particle at Index %d = %s" % (index, str(self.particleArray[index,:]))
            p = self.particles[index]
            x = workingSlice[index,0]
            y = workingSlice[index,1]
            z = workingSlice[index,2]
            if z <= 0: continue
            ax = int(round(apparentCoords[index,0]))
            ay = int(round(apparentCoords[index,1]))
            scale = workingSlice[index,6]
            ttl = workingSlice[index,7]
            self.logger.debug("Drawing Particle (%d, %d, %d) @ (%d, %d, %d, %d, %d)", x,y,z,ax, ay, z, scale, ttl)
            if ax > 0 and ay > 0 and ax < self.size[0]*1.5 and ay<self.size[1]*1.5 and workingSlice[index,6]>0:
                im = p.getNextFrame()
                if scale != 1.0:
                    w, h = im.size
                    w = int(round(w*scale))
                    h = int(round(h*scale))
                    im = im.resize((w,h))

                # Fade in at creation and fade out near death
                if self.ttl>0 and self.ttc > 0 and self.ttl-ttl < self.ttc:
                    opacity = (1.0*(self.ttl-ttl))/self.ttc
                    self.logger.debug("Particle Birthing, opacity=%d, ttl=%d, ttd=%d, index=%d, len=%d, im.size=%s" %( opacity, self.ttl, self.ttd, index, len(self.particles), str(im.size)))
                    bands = list(im.split())
                    bands[3] = bands[3].point(lambda x: x*opacity)
                    im = Image.merge(im.mode, bands)
                elif self.ttl>0 and self.ttd > 0 and ttl < self.ttd:
                    # Time to Die
                    opacity = (1.0*ttl)/self.ttd
                    self.logger.debug("Particle Dying, opacity=%d, ttl=%d, ttd=%d, index=%d, len=%d, im.size=%s" %( opacity, self.ttl, self.ttd, index, len(self.particles), str(im.size)))
                    bands = list(im.split())
                    bands[3] = bands[3].point(lambda x: x*opacity)
                    im = Image.merge(im.mode, bands)

                particleList.append((im, (ax, ay)))


        self.current += 1
        return particleList

    def alphaComposite(self, particleList):
        frame = Image.new(size=(self.size[0]*2,self.size[1]*2) , mode="RGBA", color=(0,0,0,0))
        frameArray = np.array(frame)
        particleList = self.step()
        self.logger.debug("Processing %d particles", len(particleList))
        for p in particleList:
            # if p[1][0]-p[0].size[0]/2.0 > self.size[0] or p[1][1]-p[0].size[1]/2.0 > self.size[1]:
            #     return False

            im_array = np.array(p[0])
            #print "Image Array=", im_array.shape, p[0].size, p[1]
            box = [
                (self.size[1]+p[1][1]-int(math.ceil(p[0].size[1]/2.0))),
                (self.size[1]+p[1][1]+int(math.floor(p[0].size[1]/2.0))),
                (self.size[0]+p[1][0]-int(math.ceil(p[0].size[0]/2.0))),
                (self.size[0]+p[1][0]+int(math.floor(p[0].size[0]/2.0)))
            ]
            # #print "Calculated Box", box
            # if box[0] < 0:
            #     # Chopped off the lhs - truncate by box[0]
            #     #print "Truncation Top", box[0]*-1
            #     im_array = im_array[box[0]*-1:,...]
            #     box[0] = 0

            # elif box[1] > self.size[1]:
            #     # Chopped off the rhs - truncate by box[1]
            #     #print "Truncation Bottom", (p[0].size[0]-(box[1]-self.size[1]))
            #     im_array = im_array[:(p[0].size[0]-(box[1]-self.size[1])),...]
            #     box[1] = self.size[1]

            # if box[2] < 0:
            #     #print "Truncation LHS", box[2]*-1
            #     im_array = im_array[:,box[2]*-1:,:]
            #     box[2] = 0

            # elif box[3] > self.size[0]:
            #     #print "Truncation RHS", (p[0].size[0]-(box[3]-self.size[0]))
            #     im_array = im_array[:,:(p[0].size[0]-(box[3]-self.size[0])),:]
            #     box[3] = self.size[0]

            section = frameArray[box[0]:box[1], box[2]:box[3],:]
            
            #print "Section = ", frameArray.shape, box, section.shape
            # Calculate New Alpha
            # A = srcA + dstA(1-srcA)
            #print "TESTING1:", section.shape
            srcA = im_array[:,:,3]/255.0
            dstA = section[:,:,3]/255.0
            #print "TESTING2:", section.shape, srcA.shape, dstA.shape
            A = srcA + dstA * ((srcA*-1.0+1.0))

            # Expand Arrays to contain alpha for RGB
            srcA = np.expand_dims(srcA, axis=2)
            srcA = np.repeat(srcA, 3, axis=2)
            dstA = np.expand_dims(dstA, axis=2)
            dstA = np.repeat(dstA, 3, axis=2)
            newA = np.expand_dims(A, axis=2)
            newA = np.power(np.repeat(newA, 3, axis=2), -1) # Get Inverse (1/A)
            #print "TESTING3:", srcA.shape, dstA.shape
            # Composite weighted average of colours
            # C = ( srcC*A + dstC*A(1-srcA) ) / A
            srcRGB = im_array[:,:,:3]
            dstRGB = section[:,:,:3]
            dstRGB = np.multiply((srcRGB*srcA + dstRGB*dstA*(srcA*-1.0+1.0)), newA, where=np.isfinite(newA))

            # Set Alpha
            section[:,:,3] = A

        return Image.fromarray(frameArray)

    def PILAlphaComposite(self, particleList):
        frame = Image.new(size=self.size, mode="RGBA", color=(0,0,0,0))
        frameArray = np.array(frame)
        self.logger.debug("Processing %d particles", len(particleList))
        for p in particleList:
             im2 = Image.new(size=self.size, mode="RGBA", color = (0,0,0,0))
             im2.paste(p[0], p[1])
             frame = Image.alpha_composite(frame, im2)
        return frame


    def getNextFrame(self):
        """ Generate new Particles, apply forces and move particles """
        particleList = self.step()
        #frame = alphaComposite(particleList)
        frame = self.PILAlphaComposite(particleList)
        return frame

#####################
##     Testing     ##
#####################
if __name__ == "__main__":
    from MotionPrimative import MotionImage
    test = noForce()
    for i in xrange(10):
        print test()
