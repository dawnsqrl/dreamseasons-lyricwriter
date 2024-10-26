from json import loads
from random import uniform, seed

from manim import *

seed(1026)


def pixel_x(x):
    return (config.right_side - config.left_side) * (x / config.frame_size[0])


def pixel_y(y):
    return (config.bottom - config.top) * (y / config.frame_size[1])


def pixel_pos(x, y):
    return config.left_side + pixel_x(x) + config.top + pixel_y(y)


class LyricWriter(Scene):
    def __init__(self, path):
        super().__init__()
        with open(path, 'r') as file:
            data = loads(file.read())
            self.font = data['font']
            self.time_unit = 1 / data['unit']
            self.data = data['data']
        self.in_time = 0.5
        self.in_shift = DOWN / 2
        self.out_time = 2
        self.word_spacing = 40  # pixel
        self.noise_cap = 0.1  # unit
        self.correction_factor = 0.98  # default = 1

    def construct(self):
        sign = 1
        for sentence in self.data:
            self.next_section(name=sentence['text'])
            word_objects = []
            successions = []
            elapsed_time = 0
            assert len(words := sentence['text'].split()) \
                   == len(steps := sentence['step'])
            for word, step in zip(words, steps):
                word_object = Text(
                    word, font=self.font,
                    font_size=32, color=WHITE
                )
                if len(word_objects) == 0:
                    word_object = word_object.move_to(
                        pixel_pos(100, 200), aligned_edge=LEFT
                    )
                else:
                    word_object = word_object.next_to(
                        word_objects[-1], RIGHT, aligned_edge=ORIGIN,
                        buff=pixel_x(self.word_spacing)
                    )
                word_objects.append(word_object)
                successions.append(Succession(
                    Wait(elapsed_time),
                    FadeIn(word_object, shift=self.in_shift, run_time=self.in_time)
                ))
                elapsed_time += step * self.time_unit * self.correction_factor
            for word_object in word_objects:
                word_object.shift(UP * self.noise_cap * sign * uniform(0, 1))
                sign *= -1
            self.play(successions)
            self.wait(sentence['step'][-1] * self.time_unit * self.correction_factor)
            self.play(FadeOut(*word_objects, run_time=self.out_time))


if __name__ == '__main__':
    with tempconfig({
        'frame_size': (2000, 400),
        'frame_rate': 24,
        'transparent': True,
        'save_sections': True
    }):
        scene = LyricWriter('input-all.json')
        scene.render()
