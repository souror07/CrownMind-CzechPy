# Game Core Logic - Separated from UI
# This module contains all game logic that can be used by both
# Tkinter (Windows) and Kivy (Android) interfaces

import copy
import math
import random

EMPTY = "."
RED = "r"
RED_KING = "R"
BLACK = "b"
BLACK_KING = "B"

BOARD_SIZE = 8

# Difficulty levels
DIFFICULTY_LEVELS = {
    "Beginner": {"depth": 1, "mix": 0.50},
    "Easy": {"depth": 2, "mix": 0.25},
    "Normal": {"depth": 3, "mix": 0.12},
    "Hard": {"depth": 4, "mix": 0.05},
    "Expert": {"depth": 5, "mix": 0.00},
}
DEFAULT_DIFFICULTY = "Normal"
TRANSPOSITION_TABLE = {}


# =================================================
# Core helpers
# =================================================
def make_move(start, path, captured=None):
    return {
        "start": tuple(start),
        "path": [tuple(p) for p in path],
        "captured": [tuple(p) for p in (captured or [])],
    }


def move_end(move):
    return move["path"][-1]


def inside(row, col):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def is_red(piece):
    return piece in (RED, RED_KING)


def is_black(piece):
    return piece in (BLACK, BLACK_KING)


def is_king(piece):
    return piece in (RED_KING, BLACK_KING)


def directions(piece):
    if piece == RED:
        return [(-1, -1), (-1, 1)]
    if piece == BLACK:
        return [(1, -1), (1, 1)]
    return [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def board_key(board):
    return tuple(tuple(row) for row in board)


def create_board():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for row in range(3):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = BLACK
    for row in range(5, 8):
        for col in range(BOARD_SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = RED
    return board


def count_pieces(board):
    red_count = 0
    black_count = 0
    for row in board:
        for piece in row:
            if is_red(piece):
                red_count += 1
            elif is_black(piece):
                black_count += 1
    return red_count, black_count


# =================================================
# Move generation
# =================================================
def simple_moves_for_piece(board, row, col):
    piece = board[row][col]
    if piece == EMPTY:
        return []

    moves = []
    for dr, dc in directions(piece):
        nr, nc = row + dr, col + dc
        if inside(nr, nc) and board[nr][nc] == EMPTY:
            moves.append(make_move((row, col), [(nr, nc)]))
    return moves


def jump_sequences_from(board, row, col, start_pos=None, path=None, captured=None):
    piece = board[row][col]
    if piece == EMPTY:
        return []

    if start_pos is None:
        start_pos = (row, col)
    if path is None:
        path = []
    if captured is None:
        captured = []

    sequences = []
    found_any = False

    for dr, dc in directions(piece):
        mid_r, mid_c = row + dr, col + dc
        land_r, land_c = row + 2 * dr, col + 2 * dc

        if not (inside(mid_r, mid_c) and inside(land_r, land_c)):
            continue
        if board[land_r][land_c] != EMPTY:
            continue

        middle_piece = board[mid_r][mid_c]
        if middle_piece == EMPTY:
            continue

        if is_red(piece) and not is_black(middle_piece):
            continue
        if is_black(piece) and not is_red(middle_piece):
            continue

        found_any = True
        next_board = copy.deepcopy(board)
        next_board[row][col] = EMPTY
        next_board[mid_r][mid_c] = EMPTY

        next_piece = piece
        if piece == RED and land_r == 0:
            next_piece = RED_KING
        elif piece == BLACK and land_r == BOARD_SIZE - 1:
            next_piece = BLACK_KING

        next_board[land_r][land_c] = next_piece
        new_path = path + [(land_r, land_c)]
        new_captured = captured + [(mid_r, mid_c)]

        if next_piece != piece:
            sequences.append(make_move(start_pos, new_path, new_captured))
            continue

        deeper = jump_sequences_from(
            next_board,
            land_r,
            land_c,
            start_pos=start_pos,
            path=new_path,
            captured=new_captured,
        )

        if deeper:
            sequences.extend(deeper)
        else:
            sequences.append(make_move(start_pos, new_path, new_captured))

    return sequences if found_any else []


def get_all_moves(board, player):
    normal_moves = []
    jump_moves = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == EMPTY:
                continue

            if player == "red" and is_red(piece):
                normal_moves.extend(simple_moves_for_piece(board, row, col))
                jump_moves.extend(jump_sequences_from(board, row, col))
            elif player == "black" and is_black(piece):
                normal_moves.extend(simple_moves_for_piece(board, row, col))
                jump_moves.extend(jump_sequences_from(board, row, col))

    return jump_moves if jump_moves else normal_moves


def legal_starts(board, player):
    return {move["start"] for move in get_all_moves(board, player)}


# =================================================
# Apply move / winner
# =================================================
def apply_move(board, move):
    new_board = copy.deepcopy(board)
    if move is None:
        return new_board

    start_r, start_c = move["start"]
    end_r, end_c = move_end(move)
    piece = new_board[start_r][start_c]

    new_board[start_r][start_c] = EMPTY
    for cap_r, cap_c in move["captured"]:
        new_board[cap_r][cap_c] = EMPTY

    if piece == RED and end_r == 0:
        piece = RED_KING
    elif piece == BLACK and end_r == BOARD_SIZE - 1:
        piece = BLACK_KING

    new_board[end_r][end_c] = piece
    return new_board


def get_winner(board):
    red_count, black_count = count_pieces(board)
    red_moves = len(get_all_moves(board, "red"))
    black_moves = len(get_all_moves(board, "black"))

    if red_count == 0 and black_count == 0:
        return "draw"
    if red_count == 0:
        return "black"
    if black_count == 0:
        return "red"
    if red_moves == 0 and black_moves == 0:
        return "draw"
    if red_moves == 0:
        return "black"
    if black_moves == 0:
        return "red"
    return None


def game_over(board):
    return get_winner(board) is not None


# =================================================
# Evaluation / AI
# =================================================
def evaluate(board):
    score = 0.0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece == EMPTY:
                continue

            center_bonus = 1.0 - (abs(3.5 - c) / 3.5)
            advance_bonus = (r / 7.0) if piece in (BLACK, BLACK_KING) else ((7 - r) / 7.0)

            if piece == BLACK:
                score += 1.0 + 0.20 * advance_bonus + 0.08 * center_bonus
            elif piece == BLACK_KING:
                score += 2.15 + 0.10 * center_bonus
            elif piece == RED:
                score -= 1.0 + 0.20 * advance_bonus + 0.08 * center_bonus
            elif piece == RED_KING:
                score -= 2.15 + 0.10 * center_bonus

    score += 0.03 * (len(get_all_moves(board, "black")) - len(get_all_moves(board, "red")))
    return score


def move_heuristic(board, move):
    start_r, start_c = move["start"]
    end_r, end_c = move_end(move)
    piece = board[start_r][start_c]

    capture_bonus = 100 * len(move["captured"])
    promotion_bonus = 25 if ((piece == BLACK and end_r == BOARD_SIZE - 1) or (piece == RED and end_r == 0)) else 0
    center_bonus = 4 - abs(3.5 - end_c)
    progress_bonus = 0.5 if ((piece in (BLACK, BLACK_KING) and end_r > start_r) or (piece in (RED, RED_KING) and end_r < start_r)) else 0.0

    return capture_bonus + promotion_bonus + center_bonus + progress_bonus


def alpha_beta(board, depth, alpha, beta, maximizing):
    key = (board_key(board), depth, maximizing)
    if key in TRANSPOSITION_TABLE:
        return TRANSPOSITION_TABLE[key]

    winner = get_winner(board)
    if depth == 0 or winner is not None:
        result = (evaluate(board), None)
        TRANSPOSITION_TABLE[key] = result
        return result

    player = "black" if maximizing else "red"
    moves = get_all_moves(board, player)
    if not moves:
        result = (evaluate(board), None)
        TRANSPOSITION_TABLE[key] = result
        return result

    moves.sort(key=lambda m: move_heuristic(board, m), reverse=True)

    best_move = moves[0]
    if maximizing:
        best_value = -math.inf
        for move in moves:
            value, _ = alpha_beta(apply_move(board, move), depth - 1, alpha, beta, False)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
    else:
        best_value = math.inf
        for move in moves:
            value, _ = alpha_beta(apply_move(board, move), depth - 1, alpha, beta, True)
            if value < best_value:
                best_value = value
                best_move = move
            beta = min(beta, best_value)
            if beta <= alpha:
                break

    result = (best_value, best_move)
    TRANSPOSITION_TABLE[key] = result
    return result


def alpha_beta_root_moves(board, depth):
    moves = get_all_moves(board, "black")
    if not moves:
        return []

    moves.sort(key=lambda m: move_heuristic(board, m), reverse=True)
    scored = []
    for move in moves:
        value, _ = alpha_beta(apply_move(board, move), depth - 1, -math.inf, math.inf, False)
        scored.append((value, move))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def choose_move_by_difficulty(scored_moves, difficulty_name):
    if not scored_moves:
        return None, None

    meta = DIFFICULTY_LEVELS[difficulty_name]
    mix = meta["mix"]

    if difficulty_name == "Expert" or mix == 0:
        return scored_moves[0]

    if difficulty_name == "Hard":
        pool = scored_moves[:min(3, len(scored_moves))]
        weights = [0.78, 0.16, 0.06][:len(pool)]
        return random.choices(pool, weights=weights, k=1)[0]

    if difficulty_name == "Normal":
        pool = scored_moves[:min(4, len(scored_moves))]
        weights = [0.52, 0.24, 0.16, 0.08][:len(pool)]
        return random.choices(pool, weights=weights, k=1)[0]

    if difficulty_name == "Easy":
        pool = scored_moves[:min(5, len(scored_moves))]
        weights = [0.34, 0.24, 0.18, 0.14, 0.10][:len(pool)]
        return random.choices(pool, weights=weights, k=1)[0]

    pool = scored_moves[:min(6, len(scored_moves))]
    weights = [0.24, 0.20, 0.18, 0.15, 0.13, 0.10][:len(pool)]
    return random.choices(pool, weights=weights, k=1)[0]


def score_to_bar_value(score):
    return max(0, min(100, 50 + score * 10))
