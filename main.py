import pyglet
from pyglet.window import key
import numpy as np
import time


from pyglet_particles.particles import ParticleSystem, ParticleSettings

WIDTH = 960
HEIGHT = 540
REFRESH_RATE = 1 / 60
START_OPACITY = 255
END_OPACITY = 0
MIN_START_VEL = np.array([-5, -3], dtype=float) / REFRESH_RATE
MAX_START_VEL = np.array([5, -2], dtype=float) / REFRESH_RATE
MIN_LIFESPAN = 1
MAX_LIFESPAN = 4
MASS_SCALE = 3
MAX_COUNT = 1000
EMISSION_COUNT = 20
SPEED_X = 300
SPEED_Y = SPEED_X * (HEIGHT / WIDTH)
# Amount of seconds until next particle emission
EMISSION_RATE = 1 / 12
timer = time.time()
paused = True


window = pyglet.window.Window(width=WIDTH, height=HEIGHT, vsync=False)
fps_display = pyglet.window.FPSDisplay(window=window)
label = pyglet.text.Label(x=10, y=window.height-40)
paused_label = pyglet.text.Label(
    text="Press [SPACE] to start", x=WIDTH/2, y=HEIGHT/2, anchor_x='center',
    anchor_y='center'
)
batch = pyglet.graphics.Batch()
keys = key.KeyStateHandler()
window.push_handlers(keys)


particle_img = pyglet.image.load("particle.png")
particle_system = ParticleSystem(particle_img, MAX_COUNT)
emission_x = 480
emission_y = 500


def update_particles(dt):
    if paused:
        return
    global emission_x, emission_y, timer
    particle_system.update(dt)
    # Move emitter from input
    if keys[key.LEFT]:
        emission_x -= SPEED_X * dt
    elif keys[key.RIGHT]:
        emission_x += SPEED_X * dt
    if keys[key.UP]:
        emission_y += SPEED_Y * dt
    elif keys[key.DOWN]:
        emission_y -= SPEED_Y * dt
    # Emit particles
    timer += dt
    if timer > EMISSION_RATE:
        timer = 0
        start_color = np.random.randint(0, 255, size=3, dtype=np.uint8)
        end_color = (start_color * 0.25)
        start_m = np.random.uniform(1 / MASS_SCALE, MASS_SCALE)
        end_m = start_m / MASS_SCALE

        particle_settings = ParticleSettings(
            start_color, end_color,
            START_OPACITY, END_OPACITY,
            MIN_LIFESPAN, MAX_LIFESPAN,
            start_m, end_m
        )
        particle_system.emit(
            emission_x, emission_y, EMISSION_COUNT, particle_settings,
            MIN_START_VEL, MAX_START_VEL
        )


@window.event
def on_draw():
    window.clear()
    fps_display.draw()
    label.text = "Number of active particles: {}".format(
        len(particle_system.particles)
    )
    label.draw()
    particle_system.draw()
    if paused:
        paused_label.draw()


def on_key_press(symbol, _):
    global paused
    if symbol == key.SPACE:
        paused = not paused
    elif symbol == key.S:
        pyglet.image.get_buffer_manager().get_color_buffer().save(
            'screenshot.png'
        )


if __name__ == "__main__":
    window.push_handlers(on_key_press=on_key_press)
    pyglet.clock.schedule(update_particles)
    pyglet.app.run()
