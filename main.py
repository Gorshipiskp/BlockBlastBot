import time

import keyboard
import numpy
import pyscreenshot
import winsound

from debug_logger import Logger
from mouse_control import move_figure

GAME_FIELD_SIZE = (8, 8)
NUM_FIGURES = 3
MAX_FIGURE_SIZE = (5, 5)
RESTART_BOT = "restart"

DEBUG = True

FIGURES_TO_FIND = [
    ((1, 1), 3),
]


def get_field():
    image = pyscreenshot.grab()

    w, h = image.size

    left = w // 2 - 225
    right = w // 2 + 225

    return image.crop((left, 40, right, h - 40))


def get_game_zone(field):
    w, h = field.size

    up = 228
    bottom = h - 372

    return field.crop((26, up, w - 24, bottom))


def is_filled(rgb):
    return bool(numpy.sum(rgb) > 310) or numpy.max(rgb) > 160


def formalize_field(field, GAME_FIELD_SIZE=GAME_FIELD_SIZE, booling=True):
    w, h = field.size

    field_numpied = numpy.asarray(field)
    W_F, H_F = GAME_FIELD_SIZE

    blocks_colors = []

    BLOCK_W = w // W_F
    BLOCK_H = h // H_F

    for h_c in range(H_F):
        blocks_colors.append([])

        for w_c in range(W_F):
            center_w = BLOCK_W * (w_c + 1) - BLOCK_W // 2 - (BLOCK_W // 4)
            center_h = BLOCK_H * (h_c + 1) - BLOCK_H // 2 - (BLOCK_H // 4)

            if booling:
                to_append = is_filled(field_numpied[center_w, center_h])
            else:
                to_append = [int(i) for i in field_numpied[center_w, center_h]]

            blocks_colors[h_c].append(to_append)

    return blocks_colors


def fill_bools_str(bool_field):
    rows = []

    for row in bool_field:
        rows.append("".join("■" if el else " " for el in row[::-1]))

    return "\n".join(rows)


def print_field(field, only_return):
    to_print = fill_bools_str(numpy.rot90(field, k=3))

    if only_return:
        return to_print
    print(to_print)


def crop_figure(figure):
    figure_n = numpy.asarray(figure)
    w, h = figure_n.shape

    up_border = 0
    bottom_border = w
    left_border = 0
    right_border = h

    for x in range(w):
        if numpy.sum(figure_n[x]) > 0:
            up_border = x
            break

    for x in range(w):
        x = w - x - 1

        if numpy.sum(figure_n[x]) > 0:
            bottom_border = x
            break

    for y in range(h):
        if numpy.sum(figure_n[:, y]) > 0:
            left_border = y
            break

    for y in range(h):
        y = h - y - 1

        if numpy.sum(figure_n[:, y]) > 0:
            right_border = y
            break

    return figure_n[up_border:bottom_border + 1, left_border:right_border + 1]


def field_to_ints(figure):
    return tuple(tuple(int(el) for el in row) for row in figure)


def get_figures(field):
    w, h = field.size

    up = 692
    bottom = h - 197

    figures_zone_field = field.crop((37, up, w - 37, bottom))

    wf, hf = figures_zone_field.size

    figures = []

    shatter = -1

    for fig_id in range(NUM_FIGURES):
        padding_left = 7 - shatter if fig_id == 1 else (14 - shatter if fig_id == 2 else 0)
        padding_right = 7 - shatter if fig_id == 1 else (14 - shatter if fig_id == 0 else 0)

        left = wf // NUM_FIGURES * fig_id + padding_left
        right = wf // NUM_FIGURES * (fig_id + 1) - padding_right

        figure_zone = figures_zone_field.crop((left, 0, right, hf))

        new_figure = field_to_ints(crop_figure(formalize_field(figure_zone, MAX_FIGURE_SIZE)))

        if numpy.sum(new_figure) > 0:
            figures.append(new_figure)
        else:
            figures.append(None)

    return figures


def place_figure(figure, move, game_field):
    _, ((x_start, x_end), (y_start, y_end)) = move

    game_field_c = game_field.copy()

    game_field_c[x_start:x_end, y_start:y_end] += figure

    return game_field_c


def find_possible_places(figure, fig_id, game_field):
    x_f, y_f = figure.shape
    x_g, y_g = game_field.shape

    possible_moves = {}

    for pad_x in range(x_g - x_f + 1):
        for pad_y in range(y_g - y_f + 1):
            move = (fig_id, ((pad_x, pad_x + x_f), (pad_y, pad_y + y_f)))
            game_field_pad = place_figure(figure, move, game_field)

            if numpy.max(game_field_pad) > 1:
                continue

            points = 0

            for pad_row in game_field_pad:
                if numpy.sum(pad_row) == x_g:
                    points += 100
            for pad_col in game_field_pad.T:
                if numpy.sum(pad_col) == y_g:
                    points += 100

            possible_moves[move] = points

    return possible_moves


def process_field(field):
    w, h = field.shape

    for row_id, row in enumerate(field):
        if numpy.sum(row) == w:
            field[row_id] = 0

    for col_id, col in enumerate(field.T):
        if numpy.sum(col) == h:
            field[:, col_id] = 0

    return field


def find_best_turn(figures, game_field):
    game_field_n = numpy.asarray(field_to_ints(game_field))

    best_moves = {}

    for cur_fig_id, figure in figures.items():
        possible_moves = find_possible_places(numpy.asarray(figure), cur_fig_id, game_field_n)

        if len(figures) == 1:
            if not possible_moves:
                return {}

            best_move = max(possible_moves, key=possible_moves.get)
            return {(best_move,): possible_moves[best_move]}

        for move, points in possible_moves.items():
            new_game_field = place_figure(numpy.asarray(figure), move, game_field_n)
            new_game_field = process_field(new_game_field)

            local_moves = find_best_turn({fig_id: fig for fig_id, fig in figures.items() if fig_id != cur_fig_id},
                                         new_game_field.copy())

            local_best_move = max(local_moves, key=local_moves.get) if local_moves else {}

            if local_best_move:
                best_moves[(move, *local_best_move)] = points + local_moves[local_best_move]

    return best_moves


def numerate_figs(figures):
    return dict(enumerate(figures))


def get_fig_ids(no_figures_ids):
    counter = 0
    real_ids = {}

    for fig_id_ in range(NUM_FIGURES):
        if fig_id_ not in no_figures_ids:
            real_ids[counter] = fig_id_
            counter += 1
    return real_ids


def get_figures_shapes(figures):
    return [(len(fig), len(fig[0])) for fig in figures]


def do_turn(game_zone, game_field, /, logger, turn_id):
    figures = get_figures(cur_field)
    no_figures_ids = [i for i, fig in enumerate(figures) if fig is None]
    figures = [fig for fig in figures if fig is not None]

    real_figs_ids = get_fig_ids(no_figures_ids)

    figs_shapes = {real_figs_ids.get(fig_id, fig_id) + 1: fig_shape for fig_id, fig_shape in
                   enumerate(get_figures_shapes(figures))}

    best_moves = find_best_turn(numerate_figs(figures), game_field)

    figs_str = f"DEBUG: Фигуры: {', '.join(f'{x}x{y} ({real_figs_ids.get(fig_id, fig_id) + 1})' for fig_id, (x, y) in enumerate(figs_shapes.values()))}"

    logger.log(f"Нет возможных ходов\n{figs_str}\n{print_field(game_field, only_return=True)}\n")

    if not best_moves:
        winsound.Beep(300, 1000)
        return RESTART_BOT

    the_best_move = max(best_moves, key=best_moves.get)

    best_move_msg = f"{f'Лучший ход №{turn_id} на {best_moves[the_best_move]} очков':—^60}"

    showed_moves = game_zone.copy()

    x_gz, y_gz = game_zone.size

    COLORS = {
        0: (255, 0, 0),
        1: (0, 255, 0),
        2: (0, 0, 255),
    }

    show_img = False
    x_cell = x_gz // GAME_FIELD_SIZE[0]
    y_cell = y_gz // GAME_FIELD_SIZE[1]

    if DEBUG:
        print(best_move_msg)
        print(figs_str)

        figs_found = False

        for figure_id, figure_shape in figs_shapes.items():
            if (figure_shape, figure_id) in FIGURES_TO_FIND:
                figs_found = True

                print(f"FOUND {figure_shape[0]}x{figure_shape[1]} ({figure_id }) to reassign")

                winsound.Beep(550, 200)
                winsound.Beep(700, 200)

        if figs_found:
            exit("Found figures with coordinates to reassign")

    for sub_move_id, (fig_id, moving) in enumerate(the_best_move):
        real_fig_id = real_figs_ids.get(fig_id, fig_id)
        # print(f"{real_fig_id + 1}-я фигура на x={moving[0]} y={moving[1]}")

        shape = figures[fig_id]
        (x1, x2), (y1, y2) = moving
        move_figure(x1, y1, real_fig_id, shape)
        game_field = process_field(place_figure(shape, (None, moving), game_field))

        if show_img:
            for x_t in range(x_cell * x1, x_cell * x2):
                x_p = x_t // x_cell - x1
                x = x_t - sub_move_id * 2

                for y_t in range(y_cell * y1, y_cell * y2):
                    y_p = y_t // y_cell - y1

                    if shape[x_p][y_p] == 0:
                        continue

                    y = y_t - sub_move_id * 2

                    showed_moves.putpixel((x, y), COLORS[sub_move_id])

    if show_img:
        showed_moves.show()

    time.sleep(2)

    return game_field


if __name__ == "__main__":
    turn_id = 0

    while not keyboard.is_pressed('ctrl'):
        turn_id += 1
        logger = Logger()

        cur_field = get_field()
        game_zone = get_game_zone(cur_field)
        game_field = numpy.asarray(formalize_field(game_zone), dtype=int)

        res = do_turn(game_zone, game_field, logger=logger, turn_id=turn_id)

        if isinstance(res, str) and res == RESTART_BOT:
            pass
        else:
            game_field = res
