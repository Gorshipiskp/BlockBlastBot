import time
from json import load

import mouse
import winsound

DEBUG = False

figs_starts = load(open("figures_starts.json", "r"))


def calc_x_move(n, start_x, border_horizontal):
    dx = n * 35

    return start_x + dx


def calc_y_move(n, start_y, border_vertical):
    dy = n * 35

    return start_y + dy


POSITIONS = {
    0: (830, 785),
    1: (960, 785),
    2: (1090, 785),
}


def move_figure(x, y, fig_id, shape):
    x_s, y_s = len(shape), len(shape[0])

    coords_str = f"({x_s}, {y_s})"

    if coords_str not in figs_starts:
        print(f"NOT FOUND ({x_s}, {y_s})")

        winsound.Beep(350, 250)
        winsound.Beep(700, 750)

        exit()
    else:
        cur_fig = figs_starts[coords_str]

        if str(fig_id + 1) not in cur_fig:
            print(f"NOT FOUND ({x_s}, {y_s}) ({fig_id + 1})")

            winsound.Beep(350, 250)
            winsound.Beep(700, 750)

            exit()
        else:
            x_start = cur_fig[str(fig_id + 1)][0]
            y_start = cur_fig[str(fig_id + 1)][1]

    x_take, y_take = POSITIONS[fig_id]
    x_start_rel = x_take - (len(shape) - 1) / 2 * 22
    y_start_rel = y_take - (len(shape[0]) - 1) / 2 * 22

    x_end = calc_x_move(x, x_start, x_s)
    y_end = calc_y_move(y, y_start, y_s)

    mouse.move(x_start_rel, y_start_rel, absolute=True, duration=0.15)
    time.sleep(0.1)
    mouse.hold(mouse.LEFT)
    time.sleep(1 if DEBUG else 0.2)

    mouse.move(x_end, y_end, absolute=True, duration=0.15)

    shatter = 5

    mouse.move(x_end + shatter, y_end + shatter, absolute=True, duration=0.05)
    mouse.move(x_end - shatter, y_end - shatter, absolute=True, duration=0.05)
    mouse.move(x_end - shatter, y_end + shatter, absolute=True, duration=0.05)
    mouse.move(x_end + shatter, y_end - shatter, absolute=True, duration=0.05)

    mouse.move(x_end, y_end, absolute=True, duration=0.15)
    time.sleep(2.5 if DEBUG else 0.3)
    mouse.release(mouse.LEFT)
    mouse.move(900, 500, absolute=True, duration=0.15)
    time.sleep(1.5 if DEBUG else 0.2)


if __name__ == "__main__":
    while True:
        print(mouse.get_position())
        time.sleep(0.75)
