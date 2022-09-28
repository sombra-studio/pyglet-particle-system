from dataclasses import dataclass
import numpy as np
import pyglet
import time


# Local modules
from physics import State


@dataclass
class ParticleSettings:
    """
    Settings for a particle including color, opacity, lifespan and mass ranges

    Attributes:
        start_color (ndarray): Color the particles have at the beginning
        end_color (ndarray): Color at the end of the lifespan RGB in 0-255
        start_opacity (float): Opacity the particles have at the beginning
        end_opacity (float): Opacity value at the end of the lifespan
        min_lifespan (float): Minimum life duration in seconds
        max_lifespan (float): Maximum life duration in seconds
        start_m (float): Mass of the particles at the beginning
        end_m (float): Mass of the particles at the end of lifespan
    """
    start_color: np.ndarray
    end_color: np.ndarray
    start_opacity: float
    end_opacity: float
    min_lifespan: float
    max_lifespan: float
    start_m: float
    end_m: float


class Particle:
    """
    Particle that represents a unit of a particle system and displays a
    sprite.

    Attributes:
        sprite (Sprite): Sprite that represents the particle
        state (State): Object that stores the physical state
        creation_time (float): Time when the particle was created
        settings (ParticleSettings): A collection of settings for a particle
        dead (bool): If this particle reached its lifespan
        lifespan (float): Life duration of the particle in seconds
    """
    def __init__(self, sprite, state, creation_time, settings):
        self.sprite = sprite
        self.state = state
        self.creation_time = creation_time
        self.settings = settings
        self.dead = False
        self.lifespan = np.random.uniform(
            settings.min_lifespan, settings.max_lifespan
        )
        self.sprite.color = settings.start_color

    def update(self, dt, current_time, forces):
        """
        Update if the particle is dead, its physical state and color

        Args:
            dt (float): Seconds since the last update
            current_time (float): Current time in seconds
            forces (list[float]): List of forces acting on the particle
        """
        # Set dead particles
        elapsed_time = current_time - self.creation_time
        if elapsed_time > self.lifespan:
            self.dead = True
            return
        # Life time interpolation value value
        t = elapsed_time / self.lifespan
        # Update physical state
        self.state.m = (
            (1 - t) * self.settings.start_m + t * self.settings.end_m
        )
        self.state.pos += self.state.v * dt
        self.sprite.update(x=self.state.pos[0], y=self.state.pos[1])
        for force in forces:
            a = force / self.state.m
            self.state.v += a * dt
        # Update color
        self.sprite.color = (
            (1 - t) * self.settings.start_color + t * self.settings.end_color
        )
        self.sprite.opacity = (
            (1 - t) * self.settings.start_opacity +
            t * self.settings.end_opacity
        )


class ParticleSystem:
    """
    System that can emit particles.

    Attributes:
        img (Image): Image to use for each particle
        max_count (int): Maximum number of particles allowed in the system
        forces (list[float]): Forces that will affect the system in N
        particles (list[Particle]): Particles that belong to the system
        batch (Batch): A batch object that groups sprites in a single draw call
    """
    def __init__(self, img, max_count):
        self.img = img
        self.max_count = max_count
        self.forces = []
        self.particles = []
        self.batch = pyglet.graphics.Batch()

    def emit(self, x, y, num, settings, min_start_velocity, max_start_velocity):
        """
        Create the given number of particles.

        Args:
            x (float): Position of the emission in the x-axis
            y (float): Position of the emission in the y-axis
            num (int): Number of particles to create
            settings (ParticleSettings): Settings for the particles
            min_start_velocity (ndarray): Minimum velocity at start (velocity is
                set randomly between the minimum and maximum)
            max_start_velocity (ndarray): Maximum velocity at start

        Returns:
            list[Particles]: The new particles created
        """
        creation_time = time.time()
        new_particles = []
        for i in range(num):
            # if limit was reached break
            if len(self.particles) + i == self.max_count:
                break
            sprite = pyglet.sprite.Sprite(self.img, x, y, batch=self.batch)
            pos = np.array([x, y], dtype=float)
            v = np.zeros(len(min_start_velocity))
            for i in range(len(min_start_velocity)):
                v[i] = np.random.uniform(
                    min_start_velocity[i], max_start_velocity[i]
                )
            state = State(pos, v, settings.start_m)
            particle = Particle(sprite, state, creation_time, settings)
            new_particles.append(particle)
        # add new particles to the list
        self.particles.extend(new_particles)
        return new_particles

    def emit_rect(
        self, x, y, num, settings, min_start_velocity, max_start_velocity,
        width=5, height=5
    ):
        """
        Emit particles as rectangles instead of sprites.

        Args:
            x (float): Position of the emission in the x-axis
            y (float): Position of the emission in the y-axis
            num (int): Number of particles to create
            settings (ParticleSettings): Settings for the particles
            min_start_velocity (ndarray): Minimum velocity at start (velocity is
                set randomly between the minimum and maximum)
            max_start_velocity (ndarray): Maximum velocity at start
            width (int): Width of rectangles in pixels
            height (int): Height of rectangles in pixels

        Returns:
            list[Particles]: The new particles created
        """
        creation_time = time.time()
        new_particles = []
        for i in range(num):
            # if limit was reached break
            if len(self.particles) + i == self.max_count:
                break
            rect = pyglet.shapes.Rectangle(
                x, y, width, height, batch=self.batch
            );
            pos = np.array([x, y], dtype=float)
            v = np.zeros(len(min_start_velocity))
            for i in range(len(min_start_velocity)):
                v[i] = np.random.uniform(
                    min_start_velocity[i], max_start_velocity[i]
                )
            state = State(pos, v, settings.start_m)
            particle = Particle(rect, state, creation_time, settings)
            new_particles.append(particle)
        # add new particles to the list
        self.particles.extend(new_particles)
        return new_particles

    def update(self, dt):
        """
        Update the system after dt seconds have passed

        Args:
            dt (float): Amount of seconds since the last update
        """
        current_time = time.time()
        for particle in self.particles:
            particle.update(dt, current_time, self.forces)
        # Remove dead particles
        for particle in filter(lambda l: l.dead, self.particles):
            self.particles.remove(particle)
            particle.sprite.delete()

    def draw(self):
        self.batch.draw()
