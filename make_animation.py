import time
import sys
import os


class CurrentPositions:
    def __init__(self, buoy_init, piston_init, wave_init):
        self.buoy_y = buoy_init
        self.buoy_y_scaled = 0
        self.piston_y = piston_init
        self.piston_y_scaled = 0
        self.wave_y = wave_init
        self.wave_y_scaled = 0

    def update_scaled(self):
        self.buoy_y_scaled = self.buoy_y * run_data.scale_factor
        self.piston_y_scaled = self.piston_y * run_data.scale_factor
        self.wave_y_scaled = self.wave_y * run_data.scale_factor

    def update_base(self, buoy_init, piston_init, wave_init):
        self.buoy_y = buoy_init
        self.piston_y = piston_init
        self.wave_y = wave_init


class Circle:
    def __init__(self, y, radius, colour=(0, 0, 0), thickness=0):
        self.colour = colour
        self.thickness = thickness
        self.y = y
        self.radius = radius

    def display(self):
        pygame.draw.circle(run_data.screen, self.colour, (settings.screen_width/2, self.y), self.radius, self.thickness)


class Line:
    def __init__(self, start_point, end_point, colour=(0, 0, 0), thickness=0):
        self.start_point = start_point
        self.end_point = end_point
        self.thickness = thickness
        self.colour = colour

    def display(self):
        pygame.draw.line(run_data.screen, self.colour, self.start_point, self.end_point, self.thickness)


class Rectangle:
    # drawn from centre
    def __init__(self, rect_size, y, colour=(0, 0, 0), thickness=0, rectangle_x=None):
        self.width, self.height = rect_size
        self.x = settings.screen_width / 2 if isinstance(rectangle_x, type(None)) else rectangle_x
        self.y = y
        self.thickness = thickness
        self.colour = colour
        self.rect = (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)

    def display(self):
        self.rect = (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)
        pygame.draw.rect(run_data.screen, self.colour, self.rect, 0)


class Buoy:
    def __init__(self, floater, tube):
        self.floater = floater
        self.tube = tube

    def display(self):
        self.floater.display()
        self.tube.display()


class Tube:
    def __init__(self, radius, length, y, thickness, colour=(0, 0, 0)):
        self.radius = radius
        self.length = length
        self.thickness = thickness
        self.y = y
        self.sidex = self.radius + self.thickness / 2
        self.colour = colour

        self.sides = [
            Line([(settings.screen_width / 2) - self.sidex, y + (self.length / 2)], [(settings.screen_width / 2) - self.sidex, y - (self.length / 2)],
                 colour=self.colour, thickness=self.thickness),
            Line([(settings.screen_width / 2) + self.sidex, y + (self.length / 2)], [(settings.screen_width / 2) + self.sidex, y - (self.length / 2)],
                 colour=self.colour, thickness=self.thickness)]

    def display(self):
        self.sidex = self.radius + self.thickness / 2

        for [i, _] in enumerate(self.sides):
            self.sides[i].thickness = self.thickness
            if i == 0:
                self.sides[i].start_point[0] = settings.screen_width/2 - self.sidex
                self.sides[i].end_point[0] = settings.screen_width/2 - self.sidex
            else:
                self.sides[i].start_point[0] = settings.screen_width/2 + self.sidex
                self.sides[i].end_point[0] = settings.screen_width/2 + self.sidex

            self.sides[i].start_point[1] = self.y - (self.length / 2)
            self.sides[i].end_point[1] = self.y + (self.length / 2)
            self.sides[i].display()


class Piston:
    def __init__(self, radius, y, length, shaft_thickness=2, plunger_thickness=4, colour=(0, 0, 0)):
        self.radius = radius
        self.y = y
        self.length = length
        self.shaft_thickness = shaft_thickness
        self.plunger_thickness = plunger_thickness
        self.colour = colour
        self.plunger = Line([(settings.screen_width / 2) - self.radius, self.y], [(settings.screen_width / 2) + self.radius, self.y],
                            thickness=self.plunger_thickness, colour=self.colour)
        self.shaft = Line([settings.screen_width / 2, self.y - self.length], [settings.screen_width / 2, self.y], thickness=self.shaft_thickness, colour=self.colour)

    def display(self):
        self.plunger.start_point = [(settings.screen_width / 2) - self.radius*0.95, self.y]
        self.plunger.end_point = [(settings.screen_width / 2) + self.radius*0.95, self.y]
        self.shaft.start_point = [settings.screen_width / 2, self.y - self.length]
        self.shaft.end_point = [settings.screen_width / 2, self.y]

        self.plunger.display()
        self.shaft.display()


class Button:
    def __init__(self, text, rect_size, pos, font, padding=20, colour=(0, 0, 0), on_click=None):
        self.text = text
        self.rect_size = rect_size
        self.x, self.y = pos
        self.shape = Rectangle(self.rect_size, self.y, rectangle_x=self.x, colour=colour)
        self.on_click = on_click
        self.font = font
        self.base_colour = colour
        self.hover_colour = tuple([x*0.8 for x in list(self.base_colour)])
        self.flash_colour = tuple([x*1.2 for x in list(self.base_colour)])
        self.padding = padding
        self.clicking = False
        self.hovering = False
        self.mouse_is_down = False
        self.click_counter = run_data.speed / 10

    def display(self):
        if self.clicking:
            self.shape.colour = self.flash_colour
            self.click_counter -= 1
            if self.click_counter <= 0:
                self.clicking = False
        elif self.mouse_is_down:
            self.shape.colour = self.flash_colour
        elif self.hovering:
            self.shape.colour = self.hover_colour
        else:
            self.shape.colour = self.base_colour
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.display()
        surf = self.font.render(self.text, True, (0, 0, 0))
        rect = surf.get_rect(center=(self.x, self.y))
        run_data.screen.blit(surf, rect)

    def get_font_size(self):
        surf = self.font.render(self.text, False, (0, 0, 0))
        return surf.get_rect().size

    def resize_rect(self):
        size = self.get_font_size()
        self.padding = size[0] * 0.1

        self.shape.width = size[0] + self.padding
        self.shape.height = size[1] + self.padding

        self.rect_size = (self.shape.width, self.shape.height)

    def resize(self, size):
        self.shape.width = size[0]
        self.shape.height = size[1]
        self.rect_size = (self.shape.width, self.shape.height)

    def click(self, mouse):
        if not isinstance(self.on_click, type(None)):
            self.click_counter = run_data.speed / 10
            if self.x - self.rect_size[0] / 2 < mouse[0] < self.x + self.rect_size[0] / 2 and \
                    self.y - self.rect_size[1] / 2 < mouse[1] < self.y + self.rect_size[1] / 2:
                if self.mouse_is_down:
                    self.clicking = True
                    self.on_click()
                self.mouse_is_down = False
            else:
                self.clicking = False
                self.mouse_is_down = False

    def mouse_down(self, mouse):
        if self.x - self.rect_size[0] / 2 < mouse[0] < self.x + self.rect_size[0] / 2 and \
                self.y - self.rect_size[1] / 2 < mouse[1] < self.y + self.rect_size[1] / 2:
            self.mouse_is_down = True
        else:
            self.mouse_is_down = False

    def hover(self, mouse):
        if self.x - self.rect_size[0] / 2 < mouse[0] < self.x + self.rect_size[0] / 2 and \
                self.y - self.rect_size[1] / 2 < mouse[1] < self.y + self.rect_size[1] / 2:
            self.hovering = True
        else:
            self.hovering = False


class Sea:
    def __init__(self, y_top, colour=(0, 0, 0)):
        self.y_top = y_top
        self.colour = colour
        self.rect = (0, self.y_top, settings.screen_width, settings.screen_height - self.y_top+1)

    def display(self):
        self.rect = (0, self.y_top, settings.screen_width, settings.screen_height - self.y_top+1)
        pygame.draw.rect(run_data.screen, self.colour, self.rect, 0)


def start_animation():
    run_data.playing = True
    run_data.paused = False


def stop_animation():

    run_data.playing = False
    run_data.paused = False

    run_data.current_pos.update_base(sim_data.buoy_motion[0], sim_data.piston_motion[0], sim_data.wave_motion[0])
    run_data.current_pos.update_scaled()
    run_data.now_time = 0
    update_screen()


def pause_animation():
    run_data.paused = True


def speed_up():
    if run_data.speed >= 1:
        run_data.speed += 1
    else:
        run_data.speed *= 2


def slow_down():
    if run_data.speed <= 0.125:
        pass
    elif run_data.speed > 1:
        run_data.speed -= 1
    else:
        run_data.speed /= 2


def scale_up():
    if run_data.scale_factor >= 1:
        run_data.scale_factor += 1
    else:
        run_data.scale_factor *= 2

    resize()


def scale_down():
    if run_data.scale_factor <= 0.125:
        pass
    elif run_data.scale_factor > 1:
        run_data.scale_factor -= 1
    else:
        run_data.scale_factor /= 2

    resize()


def resize():
    run_data.current_pos.update_scaled()
    components.buoy_assembly.floater.radius = sim_data.buoy_radius * run_data.scale_factor
    if isinstance(components.buoy_assembly.floater, Rectangle):
        components.buoy_assembly.floater.height = sim_data.buoy_length * run_data.scale_factor
        components.buoy_assembly.floater.width = sim_data.buoy_radius * 2 * run_data.scale_factor

    components.buoy_assembly.tube.radius = sim_data.tube_radius * run_data.scale_factor
    components.buoy_assembly.tube.length = sim_data.tube_length * run_data.scale_factor
    components.piston.radius = sim_data.tube_radius * run_data.scale_factor

    if sim_data.buoy_shape == 'cylinder':
        sim_data.piston_offset = sim_data.buoy_length/2 * run_data.scale_factor
    elif sim_data.buoy_shape == 'sphere':
        sim_data.piston_offset = sim_data.buoy_radius * run_data.scale_factor

    components.piston.length = sim_data.piston_datum - sim_data.water_datum - sim_data.buoy_equilibrium*run_data.scale_factor + sim_data.piston_offset
    components.piston.shaft.thickness = int(sim_data.tube_radius * run_data.scale_factor * 0.3 * 0.5)
    components.piston.plunger.thickness = int(sim_data.tube_radius * run_data.scale_factor * 0.3)
    components.buoy_assembly.tube.thickness = int(sim_data.tube_radius * run_data.scale_factor * 0.2)

    update_screen()


def update_screen():

    components.water_line.end_point[0] = settings.screen_width
    components.equilibrium_line.end_point[0] = settings.screen_width

    run_data.screen.fill(colours.background)
    time_text = settings.font['ui'].render('{:.2f}/{:.2f}'.format(run_data.now_time, run_data.end_time), True, (0, 0, 0))
    speed_text = settings.font['ui'].render('Speed: {:g}'.format(run_data.speed), True, (0, 0, 0))
    scale_text = settings.font['ui'].render('Scale: {:g}'.format(run_data.scale_factor), True, (0, 0, 0))

    speed_rect = speed_text.get_rect()
    scale_rect = scale_text.get_rect()

    components.water.y_top = sim_data.water_datum + run_data.current_pos.wave_y_scaled
    components.water.display()
    components.water_line.display()
    components.equilibrium_line.display()

    components.piston.y = sim_data.piston_datum + run_data.current_pos.piston_y_scaled

    if sim_data.buoy_shape == 'sphere':
        components.buoy_assembly.floater.y = sim_data.water_datum - components.buoy_assembly.floater.radius + sim_data.buoy_equilibrium * run_data.scale_factor + run_data.current_pos.buoy_y_scaled
    elif sim_data.buoy_shape == 'cylinder':
        components.buoy_assembly.floater.y = sim_data.water_datum - (components.buoy_assembly.floater.height/2) + sim_data.buoy_equilibrium * run_data.scale_factor + run_data.current_pos.buoy_y_scaled

    components.buoy_assembly.tube.y = sim_data.piston_datum + run_data.current_pos.buoy_y_scaled
    components.buoy_assembly.display()
    components.piston.display()
    for button in components.buttons.values():
        button.display()

    run_data.screen.blit(speed_text, (settings.screen_width - speed_rect.width-settings.edge_border, settings.edge_border))
    run_data.screen.blit(scale_text, (settings.screen_width - scale_rect.width-settings.edge_border, speed_rect.height/2 + scale_rect.height/2 + 15))
    run_data.screen.blit(time_text, (10, 10))

    pygame.display.update()


def set_buttons():
    components.buttons['btn_start'].font = settings.font['text_btn']
    components.buttons['btn_pause'].font = settings.font['text_btn']
    components.buttons['btn_stop'].font = settings.font['text_btn']

    components.buttons['btn_bigger'].font = settings.font['arrow_btn']
    components.buttons['btn_smaller'].font = settings.font['arrow_btn']
    components.buttons['btn_faster'].font = settings.font['arrow_btn']
    components.buttons['btn_slower'].font = settings.font['arrow_btn']

    for button in components.buttons.keys():
        components.buttons[button].resize_rect()

    edge_margin = settings.edge_border
    between_margin = settings.button_spacing
    s1 = components.buttons['btn_start'].rect_size
    s2 = components.buttons['btn_pause'].rect_size
    s3 = components.buttons['btn_stop'].rect_size
    s4 = components.buttons['btn_bigger'].rect_size
    s5 = components.buttons['btn_smaller'].rect_size
    s6 = components.buttons['btn_faster'].rect_size
    s7 = components.buttons['btn_slower'].rect_size

    tallest_bottom = max([s3[1], s4[1], s5[1]]) * (1 + settings.button_padding)
    tallest_top = max([s1[1], s2[1], s6[1], s7[1]]) * (1 + settings.button_padding)

    right_width = max([s4[0], s5[0], s5[0], s7[0]]) * (1 + settings.button_padding)
    left_widest = max([s1[0], s2[0], s3[0]]) * (1 + settings.button_padding)

    components.buttons['btn_start'].resize((left_widest, tallest_top))
    components.buttons['btn_pause'].resize((left_widest, tallest_top))
    components.buttons['btn_stop'].resize((left_widest*2 + between_margin, tallest_bottom))

    components.buttons['btn_bigger'].resize((right_width, tallest_bottom))
    components.buttons['btn_smaller'].resize((right_width, tallest_bottom))
    components.buttons['btn_faster'].resize((right_width, tallest_top))
    components.buttons['btn_slower'].resize((right_width, tallest_top))

    components.buttons['btn_start'].x = left_widest/2 + edge_margin
    components.buttons['btn_start'].y = settings.screen_height - edge_margin - tallest_bottom - between_margin - tallest_top/2

    components.buttons['btn_pause'].x = edge_margin + left_widest + between_margin + left_widest/2
    components.buttons['btn_pause'].y = settings.screen_height - edge_margin - tallest_bottom - between_margin - tallest_top/2

    components.buttons['btn_stop'].x = edge_margin + (2*left_widest + between_margin)/2
    components.buttons['btn_stop'].y = settings.screen_height - edge_margin - tallest_bottom/2

    components.buttons['btn_bigger'].x = settings.screen_width - edge_margin - right_width/2
    components.buttons['btn_bigger'].y = settings.screen_height - edge_margin - tallest_bottom/2

    components.buttons['btn_smaller'].x = settings.screen_width - edge_margin - right_width - between_margin - right_width/2
    components.buttons['btn_smaller'].y = settings.screen_height - edge_margin - tallest_bottom/2

    components.buttons['btn_faster'].x = settings.screen_width - edge_margin - right_width/2
    components.buttons['btn_faster'].y = settings.screen_height - edge_margin - tallest_bottom - between_margin - tallest_bottom/2

    components.buttons['btn_slower'].x = settings.screen_width - edge_margin - right_width - between_margin - right_width/2
    components.buttons['btn_slower'].y = settings.screen_height - edge_margin - tallest_bottom - between_margin - tallest_bottom/2


def resize_window():

    screen_rect = run_data.screen.get_rect()
    width = screen_rect.width
    height = screen_rect.height

    if width < settings.MIN_WIDTH:
        width = settings.MIN_WIDTH
    if height < settings.MIN_HEIGHT:
        height = settings.MIN_HEIGHT

    settings.screen_width = width
    settings.screen_height = height
    run_data.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    sim_data.water_datum = height * 0.25
    sim_data.piston_datum = height * 0.66

    font_ratio = int(settings.screen_width/20)
    if font_ratio < 30:
        font_ratio = 30
    elif font_ratio > 55:
        font_ratio = 55

    settings.font['ui'] = pygame.font.SysFont(settings.font_name, font_ratio)
    settings.font['text_btn'] = pygame.font.SysFont(settings.font_name, font_ratio)
    settings.font['arrow_btn'] = pygame.font.SysFont(settings.font_name, font_ratio)

    set_buttons()

    components.water_line.start_point[1] = sim_data.water_datum
    components.water_line.end_point[1] = sim_data.water_datum
    components.equilibrium_line.start_point[1] = sim_data.piston_datum
    components.equilibrium_line.end_point[1] = sim_data.piston_datum
    components.piston.length = sim_data.piston_datum - sim_data.water_datum - sim_data.buoy_equilibrium*run_data.scale_factor + sim_data.piston_offset

    components.buoy_assembly.floater.x = width/2

    update_screen()


def check_buttons(val):
    mouse = pygame.mouse.get_pos()
    for button in components.buttons.values():
        if val == 1:
            button.click(mouse)
        elif val == 2:
            button.hover(mouse)
        elif val == 3:
            button.mouse_down(mouse)


def print_sim_data(print_data, file):
    period = float(print_data['T'][0])
    frequency = float(print_data['F'][0])
    significant_height = float(print_data['Hs'][0])
    r_buoy = float(print_data['r_buoy'][0])
    m1 = float(print_data['m1'][0])
    m2 = float(print_data['m2'][0])
    c_wave = float(print_data['C_wave'][0])
    c_damper = float(print_data['C_damper'][0])
    k = float(print_data['K'][0, 0])
    length_buoy = float(print_data['L_buoy'][0])
    shape_buoy = print_data['shape_buoy'][0]
    length_tube = float(print_data['tube_length'][0])
    r_tube = float(print_data['tube_radius'][0])
    equilibrium = float(print_data['buoy_equilibrium'][0])

    if shape_buoy != 'cylinder':
        length_buoy = ''
    else:
        length_buoy = 'Length: {:g}'.format(length_buoy)

    out_str = """
==== PARAMETERS ====

FILENAME
Data file: {file:s}

WAVE DATA
Period: {period:g}
Frequency: {freq:g}
Significant Height: {Hs:g}
Damping: {c_wave:g}

BUOY DATA
Shape: {shape}
Radius: {buoy_r:g}
Mass: {buoy_m:g}
{buoy_l}
Equilibrium Submersion: {eq:g}

TUBE DATA
Radius: {tube_r:g}
Length: {tube_l:g}
Mass: {tube_m:g}

PTO DATA
Damping Coefficient: {c_pto:g}
Spring Constant: {k_pto:g}

OTHER
Mass Ratio: {m_ratio:g}

====================
""".format(period=period, freq=frequency, Hs=significant_height, c_wave=c_wave, shape=shape_buoy, buoy_r=r_buoy, buoy_m=m1,
           buoy_l=length_buoy, eq=equilibrium, tube_r=r_tube, tube_l=length_tube, tube_m=m2,
           c_pto=c_damper, k_pto=k, m_ratio=m2/m1, file=file)

    print(out_str)


class SimData:
    def __init__(self, simulation):
        self.buoy_equilibrium = float(simulation['buoy_equilibrium'])
        self.buoy_motion = simulation['buoy_motion'][0]
        self.piston_motion = simulation['piston_motion'][0]
        self.wave_motion = simulation['wave_motion'][0]
        self.buoy_radius = float(simulation['buoy_radius'])
        self.buoy_length = float(simulation['buoy_length'])
        self.buoy_shape = str(simulation['buoy_shape'][0])
        self.t = simulation['time'][0]
        self.tube_radius = float(simulation['tube_radius'])
        self.tube_length = float(simulation['tube_length'])
        self.diff = self.buoy_motion - self.wave_motion
        self.water_datum = None
        self.piston_datum = None
        self.piston_offset = None


class RunData:
    def __init__(self):
        self.speed = None
        self.scale_factor = None
        self.now_time = 0
        self.end_time = None
        self.screen = None
        self.current_pos = None
        self.running = None
        self.playing = None
        self.paused = None


class Colours:
    def __init__(self):
        self.seablue = (0, 105, 148)
        self.buoyyellow = (219, 181, 12)
        self.green = (0, 154, 23)
        self.red = (255, 0, 0)
        self.background = (255, 255, 255)


class Settings:
    def __init__(self):
        screen = pygame.display.Info()
        self.MIN_WIDTH = 400
        self.MIN_HEIGHT = screen.current_h * 0.5
        self.screen_width = self.MIN_WIDTH
        self.screen_height = self.MIN_HEIGHT
        self.font_name = 'Avenir'
        self.font = {'ui': pygame.font.SysFont(self.font_name, int(self.MIN_WIDTH/20)),
        'text_btn': pygame.font.SysFont(self.font_name, int(self.MIN_WIDTH/20)),
        'arrow_btn':pygame.font.SysFont(self.font_name, int(self.MIN_WIDTH/20))}
        self.button_padding = 0.2
        self.edge_border = 10
        self.button_spacing = 5


class Components:
    def __init__(self):
        self.water = None
        self.water_line = None
        self.equilibrium_line = None
        self.buoy_assembly = None
        self.buttons = None
        self.piston = None


def main():

    if max([sim_data.buoy_radius, sim_data.tube_radius])*8 > settings.MIN_WIDTH:
        settings.screen_width = max([sim_data.buoy_radius, sim_data.tube_radius])*8

    run_data.screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.RESIZABLE)

    pygame.display.set_caption('Buoy Simulation')
    run_data.screen.fill(colours.background)

    sim_data.water_datum = settings.screen_height * 0.25
    sim_data.piston_datum = settings.screen_height * 0.66

    # defining shapes
    components.water = Sea(sim_data.water_datum, colours.seablue)
    components.water_line = Line([0, sim_data.water_datum], [settings.screen_width, sim_data.water_datum], thickness=round(sim_data.buoy_radius*0.2))
    components.equilibrium_line = Line([0, sim_data.piston_datum], [settings.screen_width, sim_data.piston_datum], thickness=2, colour=(200, 0, 0))

    if sim_data.buoy_shape == 'cylinder':
        buoy = Rectangle((sim_data.buoy_radius*run_data.scale_factor*2, sim_data.buoy_length*run_data.scale_factor),
                         sim_data.water_datum - (sim_data.buoy_length*run_data.scale_factor/2) + sim_data.buoy_equilibrium*run_data.scale_factor, colours.buoyyellow)
        sim_data.piston_offset = sim_data.buoy_length/2 * run_data.scale_factor
    elif sim_data.buoy_shape == 'sphere':
        buoy = Circle(sim_data.water_datum - (sim_data.buoy_radius*run_data.scale_factor) + sim_data.buoy_equilibrium*run_data.scale_factor, sim_data.buoy_radius*run_data.scale_factor, colours.buoyyellow)
        sim_data.piston_offset = sim_data.buoy_radius * run_data.scale_factor
    else:
        raise AttributeError

    components.piston = Piston(sim_data.tube_radius*run_data.scale_factor, sim_data.piston_datum, sim_data.piston_datum - sim_data.water_datum - sim_data.buoy_equilibrium*run_data.scale_factor + sim_data.piston_offset,
                               plunger_thickness=round(sim_data.tube_radius*run_data.scale_factor*0.3), shaft_thickness=round(sim_data.tube_radius*run_data.scale_factor*0.3*0.5), colour=colours.green)

    tube = Tube(sim_data.tube_radius*run_data.scale_factor, sim_data.tube_length*run_data.scale_factor, sim_data.piston_datum, round(sim_data.tube_radius*run_data.scale_factor*0.2), colours.buoyyellow)
    components.buoy_assembly = Buoy(buoy, tube)
    
    btn_start = Button("Play", (60, 25), (30, settings.screen_height - 12.5), settings.font['text_btn'], settings.button_padding, (150, 150, 150), start_animation)
    btn_pause = Button("Pause", (60, 25), (90, settings.screen_height - 12.5), settings.font['text_btn'], settings.button_padding, (150, 150, 150), pause_animation)
    btn_stop = Button("Stop", (60, 25), (150, settings.screen_height - 12.5), settings.font['text_btn'], settings.button_padding, (150, 150, 150), stop_animation)

    btn_bigger = Button("Bigger", (50, 25), (settings.screen_width - 25, settings.screen_height - 12.5), settings.font['arrow_btn'], settings.button_padding, (150, 150, 150), scale_up)
    btn_smaller = Button("Smaller", (50, 25), (settings.screen_width - 75, settings.screen_height - 12.5), settings.font['arrow_btn'], settings.button_padding, (150, 150, 150), scale_down)

    btn_faster = Button("Faster", (50, 25), (settings.screen_width - 25, settings.screen_height - 12.5 - 25), settings.font['arrow_btn'], settings.button_padding, (150, 150, 150), speed_up)
    btn_slower = Button("Slower", (50, 25), (settings.screen_width - 75, settings.screen_height - 12.5 - 25), settings.font['arrow_btn'], settings.button_padding, (150, 150, 150), slow_down)

    components.buttons = {'btn_start': btn_start, 'btn_pause': btn_pause, 'btn_stop': btn_stop,
                          'btn_faster': btn_faster, 'btn_slower': btn_slower,
                          'btn_bigger': btn_bigger, 'btn_smaller': btn_smaller}

    run_data.current_pos = CurrentPositions(sim_data.buoy_motion[0], sim_data.piston_motion[0], sim_data.wave_motion[0])
    run_data.current_pos.update_scaled()

    resize_window()
    run_data.running = True
    run_data.playing = False
    run_data.paused = False

    def event_handling():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_data.running = False
                break
            if event.type == pygame.MOUSEBUTTONUP:
                check_buttons(1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    check_buttons(3)
            if event.type == pygame.MOUSEMOTION:
                check_buttons(2)
            if event.type == pygame.WINDOWRESIZED:
                resize_window()

    while run_data.running:
        event_handling()
        update_screen()
        if run_data.playing:

            for i, (t_i, y_buoy, y_piston, y_wave) in enumerate(zip(sim_data.t, sim_data.buoy_motion, sim_data.piston_motion, sim_data.wave_motion)):
                run_data.now_time = t_i
                t0 = time.time_ns() / (10 ** 9)
                event_handling()

                if run_data.paused:
                    while run_data.paused:
                        event_handling()
                        update_screen()
                        if not run_data.running:
                            break

                if not run_data.running or not run_data.playing:
                    break

                run_data.current_pos.buoy_y = y_buoy
                run_data.current_pos.piston_y = y_piston
                run_data.current_pos.wave_y = y_wave
                run_data.current_pos.update_scaled()

                update_screen()

                t_i /= run_data.speed
                t1 = time.time_ns() / (10 ** 9)
                t_diff = t1 - t0

                if i < len(sim_data.t)-1:
                    t_to_next = sim_data.t[i+1]/run_data.speed - t_i
                else:
                    t_to_next = t_i - sim_data.t[i-1]/run_data.speed

                if t_diff < t_to_next:
                    time.sleep(t_to_next - t_diff)


def check_arguments():
    arguments = sys.argv
    if len(arguments) == 1:
        file = 'demo_file.mat'
    elif len(arguments) == 2:
        file = arguments[1]
    else:
        raise KeyError('Too many arguments')

    if file.lower() not in [x.lower() for x in os.listdir('.')]:
        raise ValueError('File not in directory')

    return file


if __name__ == '__main__':
    # Getting and checking filename passed with run command. If none given, it returns the default "demo_file.mat"
    filename = check_arguments()

    # Moved pygame and scipy imports here so arguments can be checked faster
    import pygame
    from scipy.io import loadmat

    pygame.init()  # Initialising pygame

    data = loadmat(filename, chars_as_strings=1)  # loading data

    print_sim_data(data['simulation_data'][0, 0], filename)  # Printing data

    # Initialising holder variables
    settings = Settings()
    sim_data = SimData(data['simulation'][0, 0])
    run_data = RunData()
    colours = Colours()
    components = Components()

    # Adding some necessary values to the run_data variable
    run_data.speed = float(data['speed'])
    run_data.scale_factor = float(data['scale'])
    run_data.end_time = max(sim_data.t)

    # Main loop
    main()
