#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
+------------------------------------------------------------------+
|   D A R K C H E S S   4 . 0                                      |
|   - Pieces minimalist style (chess.com-like)                     |
|   - Export PGN permanent (compatible lichess.org)                |
|   - Fast simulation mode (N parties IA vs IA en quelques sec)    |
+------------------------------------------------------------------+
"""
import sys, os, json, time, random, datetime, webbrowser
import chess, chess.pgn

from PySide6.QtCore import (Qt, QTimer, Signal, QThread, QSize, QRectF,
                            QStandardPaths)
from PySide6.QtGui import (QAction, QActionGroup, QPainter, QColor, QFont,
                           QFontMetrics, QPen, QPainterPath)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QListWidget, QMessageBox,
                               QInputDialog, QFrame, QFileDialog, QStackedWidget,
                               QPushButton, QDialog, QFormLayout, QSpinBox,
                               QLineEdit, QComboBox, QDialogButtonBox,
                               QProgressBar, QCheckBox, QGridLayout, QSlider)

APP_TITLE = "Darkchess"
APP_VERSION = "4.0"
LICHESS_URL = "https://lichess.org"

# ===========================================================================
#  THÈMES
# ===========================================================================
THEMES = {
    "clair": {
        "window_bg": "#f2f3f5", "panel_bg": "#ffffff", "panel_brd": "#d7dbe0",
        "text": "#1d2129", "muted": "#6b7280", "accent": "#2563eb",
        "accent_txt": "#ffffff", "sq_light": "#ebecd0", "sq_dark": "#779556",
        "highlight": "rgba(255,255,0,0.35)", "last_move": "rgba(255,255,0,0.45)",
        "check": "rgba(239,68,68,0.65)", "dot": "rgba(30,41,59,0.30)",
        "white_pc": "#ffffff", "white_ol": "#2d2d2d",
        "black_pc": "#2d2d2d", "black_ol": "#1a1a1a",
        "clock_run": "#2563eb", "clock_idle": "#c3c9d1",
    },
    "sombre": {
        "window_bg": "#111318", "panel_bg": "#1c2028", "panel_brd": "#2d333f",
        "text": "#e8eaed", "muted": "#8b93a1", "accent": "#3b82f6",
        "accent_txt": "#ffffff", "sq_light": "#b8c0cc", "sq_dark": "#4a5563",
        "highlight": "rgba(255,255,0,0.30)", "last_move": "rgba(255,220,60,0.40)",
        "check": "rgba(239,68,68,0.75)", "dot": "rgba(226,232,240,0.40)",
        "white_pc": "#ffffff", "white_ol": "#15171a",
        "black_pc": "#15171a", "black_ol": "#0a0c0f",
        "clock_run": "#3b82f6", "clock_idle": "#39414d",
    },
    "enfer": {
        "window_bg": "#0d0202", "panel_bg": "#1a0505", "panel_brd": "#3d0f0f",
        "text": "#f0d0d0", "muted": "#a87070", "accent": "#dc2626",
        "accent_txt": "#ffffff", "sq_light": "#c98b8b", "sq_dark": "#4a0e0e",
        "highlight": "rgba(255,120,60,0.45)", "last_move": "rgba(255,180,60,0.50)",
        "check": "rgba(255,255,255,0.70)", "dot": "rgba(255,200,200,0.45)",
        "white_pc": "#fff5f5", "white_ol": "#3a0000",
        "black_pc": "#2a0606", "black_ol": "#1a0000",
        "clock_run": "#dc2626", "clock_idle": "#4a1515",
    },
}

# ===========================================================================
#  MOTEUR
# ===========================================================================
MATE = 100000
PIECE_VALUE = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
               chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
PST = {
    chess.PAWN: [0,0,0,0,0,0,0,0, 50,50,50,50,50,50,50,50,
                 10,10,20,30,30,20,10,10, 5,5,10,25,25,10,5,5,
                 0,0,0,20,20,0,0,0, 5,-5,-10,0,0,-10,-5,5,
                 5,10,10,-20,-20,10,10,5, 0,0,0,0,0,0,0,0],
    chess.KNIGHT: [-50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,0,0,0,-20,-40,
                   -30,0,10,15,15,10,0,-30, -30,5,15,20,20,15,5,-30,
                   -30,0,15,20,20,15,0,-30, -30,5,10,15,15,10,5,-30,
                   -40,-20,0,5,5,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50],
    chess.BISHOP: [-20,-10,-10,-10,-10,-10,-10,-20, -10,0,0,0,0,0,0,-10,
                   -10,0,5,10,10,5,0,-10, -10,5,5,10,10,5,5,-10,
                   -10,0,10,10,10,10,0,-10, -10,10,10,10,10,10,10,-10,
                   -10,5,0,0,0,0,5,-10, -20,-10,-10,-10,-10,-10,-10,-20],
    chess.ROOK: [0,0,0,0,0,0,0,0, 5,10,10,10,10,10,10,5,
                 -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
                 -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
                 -5,0,0,0,0,0,0,-5, 0,0,0,5,5,0,0,0],
    chess.QUEEN: [-20,-10,-10,-5,-5,-10,-10,-20, -10,0,0,0,0,0,0,-10,
                  -10,0,5,5,5,5,0,-10, -5,0,5,5,5,5,0,-5,
                  0,0,5,5,5,5,0,-5, -10,5,5,5,5,5,0,-10,
                  -10,0,5,0,0,0,0,-10, -20,-10,-10,-5,-5,-10,-10,-20],
    chess.KING: [-30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
                 -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
                 -20,-30,-30,-40,-40,-30,-30,-20, -10,-20,-20,-20,-20,-20,-20,-10,
                 20,20,0,0,0,0,20,20, 20,30,10,0,0,10,30,20],
}


def _pst(pt, color, sq):
    t = PST[pt]
    r, f = chess.square_rank(sq), chess.square_file(sq)
    return t[(7 - r) * 8 + f] if color == chess.WHITE else t[r * 8 + f]


AI_MODES = {
    "aggressive": "Agressif", "defensive": "Défensif", "balanced": "Équilibré",
    "chaotic": "Chaotique", "tactician": "Tacticien", "strategist": "Stratège",
    "polyvalent": "Polyvalent",
}


class SearchTimeout(Exception):
    pass


class Engine:
    def __init__(self, mode="balanced", profile=None):
        self.mode = mode if mode in AI_MODES else "balanced"
        self.profile = profile or {}
        self.nodes = 0

    def evaluate(self, board):
        material = positional = 0
        enemy_king = board.king(not board.turn)
        for sq, pc in board.piece_map().items():
            s = 1 if pc.color == chess.WHITE else -1
            material += s * PIECE_VALUE[pc.piece_type]
            positional += s * _pst(pc.piece_type, pc.color, sq)
        base = material + positional
        m = self.mode
        if m == "aggressive":
            base += self._attack(board, enemy_king) * 4
        elif m == "defensive":
            base += self._safety(board) * 3
        elif m == "chaotic":
            base += self._attack(board, enemy_king) * 4 + random.randint(-30, 30)
        elif m == "tactician":
            base += self._tactical(board) * 5
        elif m == "strategist":
            base += self._positional(board) * 4
        elif m == "polyvalent":
            base += (self._tactical(board) * 4
                     if self._nature(board) == "tactical"
                     else self._positional(board) * 4)
        return base if board.turn == chess.WHITE else -base

    def _attack(self, board, ek):
        if ek is None: return 0
        s = 0
        for sq in chess.SQUARES:
            pc = board.piece_at(sq)
            if pc is None or pc.color != board.turn or pc.piece_type == chess.KING:
                continue
            d = chess.square_distance(sq, ek)
            if d <= 4: s += (5 - d) * 3
        return s

    def _safety(self, board):
        s = 0
        for sq, pc in board.piece_map().items():
            if pc.color != board.turn or pc.piece_type == chess.KING: continue
            a = board.attackers(not board.turn, sq)
            d = board.attackers(board.turn, sq)
            if a and not d: s -= PIECE_VALUE[pc.piece_type] // 3
            elif d: s += 5
        return s

    def _tactical(self, board):
        s = 0
        for sq, pc in board.piece_map().items():
            if pc.color == board.turn: continue
            a = board.attackers(board.turn, sq)
            d = board.attackers(not board.turn, sq)
            if a and not d: s += PIECE_VALUE[pc.piece_type] // 4
            elif a and d: s += PIECE_VALUE[pc.piece_type] // 12
        if board.is_check(): s += 30
        return s

    def _positional(self, board):
        s = 0
        for sq in [chess.D4, chess.E4, chess.D5, chess.E5]:
            if board.is_attacked_by(board.turn, sq): s += 10
        for sq in [chess.C3, chess.C4, chess.C5, chess.C6, chess.D3, chess.D6,
                   chess.E3, chess.E6, chess.F3, chess.F4, chess.F5, chess.F6]:
            if board.is_attacked_by(board.turn, sq): s += 4
        for sq, pc in board.piece_map().items():
            if pc.color != board.turn: continue
            if pc.piece_type in (chess.KNIGHT, chess.BISHOP):
                r = chess.square_rank(sq)
                if (board.turn == chess.WHITE and r > 0) or \
                   (board.turn == chess.BLACK and r < 7):
                    s += 5
            elif pc.piece_type == chess.KING:
                r = chess.square_rank(sq)
                if board.turn == chess.WHITE and r <= 1: s += 10
                elif board.turn == chess.BLACK and r >= 6: s += 10
        return s

    def _nature(self, board):
        c = 0
        for sq, pc in board.piece_map().items():
            if board.attackers(not pc.color, sq): c += 1
        return "tactical" if c > 4 else "positional"

    def _ordered(self, board):
        moves = list(board.legal_moves)
        aggr = self.mode in ("aggressive", "chaotic", "tactician")
        def key(m):
            s = 0
            if board.is_capture(m):
                v = board.piece_type_at(m.to_square)
                a = board.piece_type_at(m.from_square)
                s += 10 * PIECE_VALUE.get(v, 0) - PIECE_VALUE.get(a, 0)
            if aggr:
                board.push(m)
                try:
                    if board.is_check(): s += 50
                finally: board.pop()
            return s
        moves.sort(key=key, reverse=True)
        return moves

    def quiesce(self, board, alpha, beta, deadline):
        self.nodes += 1
        if self.nodes % 512 == 0 and time.monotonic() > deadline:
            raise SearchTimeout
        stand = self.evaluate(board)
        if stand >= beta: return beta
        if stand > alpha: alpha = stand
        for m in self._ordered(board):
            if not board.is_capture(m): continue
            board.push(m)
            try:
                score = -self.quiesce(board, -beta, -alpha, deadline)
            finally: board.pop()
            if score >= beta: return beta
            if score > alpha: alpha = score
        return alpha

    def negamax(self, board, depth, alpha, beta, ply, deadline):
        self.nodes += 1
        if self.nodes % 512 == 0 and time.monotonic() > deadline:
            raise SearchTimeout
        if board.is_checkmate(): return -MATE + ply
        if board.is_stalemate() or board.is_insufficient_material(): return 0
        if depth == 0: return self.quiesce(board, alpha, beta, deadline)
        best = -10 ** 9
        for m in self._ordered(board):
            board.push(m)
            try:
                score = -self.negamax(board, depth - 1, -beta, -alpha,
                                      ply + 1, deadline)
            finally: board.pop()
            if score > best: best = score
            if score > alpha: alpha = score
            if alpha >= beta: break
        return best

    def _finalize(self, moves, scores, best_score, depth_done, rng):
        if depth_done == 0: return moves[0]
        if best_score < 90000 and scores:
            thresholds = {"aggressive": 8, "defensive": 4, "chaotic": 45,
                          "balanced": 12, "tactician": 6, "strategist": 10,
                          "polyvalent": 12}
            th = thresholds.get(self.mode, 12)
            good = [m for m in moves
                    if scores.get(m.uci(), -10 ** 9) >= best_score - th]
            return rng.choice(good) if good else moves[0]
        return moves[0]

    def best_move(self, board, max_seconds):
        deadline = time.monotonic() + max_seconds
        self.nodes = 0
        moves = self._ordered(board)
        if not moves: return None
        rng = random.Random(time.time_ns())
        best_move = moves[0]
        best_score = -10 ** 9
        scores = {}
        depth_done = 0
        for depth in range(1, 7):
            try:
                alpha = -10 ** 9
                lb, ls = None, -10 ** 9
                scores = {}
                for m in moves:
                    board.push(m)
                    try:
                        s = -self.negamax(
                            board, depth - 1, -10 ** 9,
                            -alpha if alpha != -10 ** 9 else 10 ** 9,
                            1, deadline)
                    finally: board.pop()
                    scores[m.uci()] = s
                    if s > ls: ls, lb = s, m
                    if s > alpha: alpha = s
                if lb is not None:
                    best_move, best_score = lb, ls
                    depth_done = depth
                    c = {u for u, sc in scores.items() if sc >= best_score - 12}
                    if c: moves = [m for m in moves if m.uci() in c]
            except SearchTimeout:
                break
        rng2 = random.Random(time.time_ns() ^ id(board))
        return self._finalize(moves, scores, best_score, depth_done, rng2) or best_move

    def best_move_fast(self, board, depth=2):
        """Coup rapide par recherche en profondeur limitée, sans timeout."""
        moves = self._ordered(board)
        if not moves: return None
        rng = random.Random(time.time_ns() ^ id(board))
        best = moves[0]
        best_score = -10 ** 9
        scores = {}
        deadline = time.monotonic() + 3600
        for m in moves:
            board.push(m)
            try:
                s = -self.negamax(board, depth - 1, -10 ** 9, 10 ** 9, 1, deadline)
            finally: board.pop()
            scores[m.uci()] = s
            if s > best_score: best_score, best = s, m
        return self._finalize(moves, scores, best_score, depth, rng) or best


class EngineThread(QThread):
    moveReady = Signal(str, int)
    def __init__(self, board_copy, seconds, gid, mode, profile):
        super().__init__()
        self.board = board_copy
        self.seconds = seconds
        self.game_id = gid
        self.engine = Engine(mode=mode, profile=profile)
    def run(self):
        mv = self.engine.best_move(self.board, self.seconds)
        self.moveReady.emit(mv.uci() if mv else "0000", self.game_id)


# ===========================================================================
#  PROFIL IA
# ===========================================================================
class AIProfile:
    DEFAULT = {
        "name": "Aurora", "level": 1, "xp": 0, "ai_mode": "balanced",
        "memory_enabled": True,
        "stats": {"wins": 0, "losses": 0, "draws": 0, "games": 0},
        "characteristics": {"aggression": 50, "defense": 50, "tactics": 50,
                            "position": 50, "adaptability": 50},
        "memory": {"openings": {}, "notes": []},
    }

    @staticmethod
    def path():
        base = QStandardPaths.writableLocation(
            QStandardPaths.AppDataLocation) or os.path.expanduser("~/.darkchess")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "profile.json")

    @classmethod
    def load(cls):
        p = cls.path()
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                m = json.loads(json.dumps(cls.DEFAULT))
                m.update(data)
                m["stats"].update(data.get("stats", {}))
                m["characteristics"].update(data.get("characteristics", {}))
                m["memory"].update(data.get("memory", {}))
                return m
            except (OSError, ValueError): pass
        return json.loads(json.dumps(cls.DEFAULT))

    @classmethod
    def save(cls, profile):
        try:
            with open(cls.path(), "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except OSError: pass

    @classmethod
    def update_after_game(cls, profile, result, moves_uci, ai_color):
        if not profile.get("memory_enabled", True): return profile
        stats = profile["stats"]
        stats["games"] += 1
        ai_won = ((result == "1-0" and ai_color == chess.WHITE) or
                  (result == "0-1" and ai_color == chess.BLACK))
        if result == "1/2-1/2":
            stats["draws"] += 1; xp = 5
        elif ai_won:
            stats["wins"] += 1; xp = 20
        else:
            stats["losses"] += 1; xp = 3
        profile["xp"] = profile.get("xp", 0) + xp
        profile["level"] = 1 + profile["xp"] // 100
        if len(moves_uci) >= 4:
            key = " ".join(moves_uci[:4])
            op = profile["memory"].setdefault("openings", {})
            e = op.setdefault(key, {"w": 0, "l": 0, "d": 0})
            if result == "1/2-1/2": e["d"] += 1
            elif ai_won: e["w"] += 1
            else: e["l"] += 1
        ch = profile["characteristics"]
        if ai_won:
            ch["tactics"] = min(100, ch["tactics"] + 1)
            ch["aggression"] = min(100, ch["aggression"] + 1)
        else:
            ch["defense"] = min(100, ch["defense"] + 1)
            ch["position"] = min(100, ch["position"] + 1)
        ch["adaptability"] = min(100, ch["adaptability"] + 1)
        cls.save(profile)
        return profile


# ===========================================================================
#  RENDU DES PIÈCES — STYLE CHESS.COM
# ===========================================================================
GLYPH = {
    chess.WHITE: {chess.KING: "♚", chess.QUEEN: "♛", chess.ROOK: "♜",
                  chess.BISHOP: "♝", chess.KNIGHT: "♞", chess.PAWN: "♟"},
    chess.BLACK: {chess.KING: "♚", chess.QUEEN: "♛", chess.ROOK: "♜",
                  chess.BISHOP: "♝", chess.KNIGHT: "♞", chess.PAWN: "♟"},
}

_FONT_CACHE = {}

def _font(family, size):
    key = (family, int(size))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = QFont(family, int(size))
    return _FONT_CACHE[key]


class BoardWidget(QWidget):
    squareClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.theme = THEMES["clair"]
        self.board = chess.Board()
        self.orientation = chess.WHITE
        self.selected = None
        self.targets = set()
        self.last_move = None
        self.show_legal = True

    def sizeHint(self): return QSize(640, 640)

    def square_rect(self, sq):
        size = min(self.width(), self.height())
        side = size / 8.0
        r, f = chess.square_rank(sq), chess.square_file(sq)
        if self.orientation == chess.WHITE: col, row = f, 7 - r
        else: col, row = 7 - f, r
        ox = (self.width() - size) / 2.0
        oy = (self.height() - size) / 2.0
        return QRectF(ox + col * side, oy + row * side, side, side)

    def square_at(self, pos):
        size = min(self.width(), self.height())
        ox = (self.width() - size) / 2.0
        oy = (self.height() - size) / 2.0
        x, y = pos.x() - ox, pos.y() - oy
        if x < 0 or y < 0 or x >= size or y >= size: return None
        col = int(x * 8 // size); row = int(y * 8 // size)
        if self.orientation == chess.WHITE: f, r = col, 7 - row
        else: f, r = 7 - col, row
        return chess.square(f, r)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        t = self.theme
        p.fillRect(self.rect(), QColor(t["window_bg"]))
        for sq in chess.SQUARES:
            r = self.square_rect(sq)
            light = (chess.square_rank(sq) + chess.square_file(sq)) % 2 == 1
            p.fillRect(r, QColor(t["sq_light"] if light else t["sq_dark"]))
        if self.last_move:
            p.fillRect(self.square_rect(self.last_move.from_square),
                       QColor(t["last_move"]))
            p.fillRect(self.square_rect(self.last_move.to_square),
                       QColor(t["last_move"]))
        if self.selected is not None:
            p.fillRect(self.square_rect(self.selected), QColor(t["highlight"]))
        if self.board.is_check():
            ksq = self.board.king(self.board.turn)
            if ksq is not None:
                p.fillRect(self.square_rect(ksq), QColor(t["check"]))
        if self.show_legal:
            p.setPen(Qt.NoPen); p.setBrush(QColor(t["dot"]))
            for sq in self.targets:
                r = self.square_rect(sq)
                p.drawEllipse(r.center(), r.width() * 0.13, r.width() * 0.13)
        self._draw_coords(p)
        self._draw_pieces(p)
        p.end()

    def _draw_coords(self, p):
        t = self.theme
        size = min(self.width(), self.height())
        side = size / 8.0
        p.setFont(_font("Inter", max(7, side * 0.18)))
        ef = 0 if self.orientation == chess.WHITE else 7
        er = 0 if self.orientation == chess.WHITE else 7
        hf = Qt.AlignBottom | (Qt.AlignLeft if self.orientation == chess.WHITE
                               else Qt.AlignRight)
        vf = Qt.AlignTop | (Qt.AlignLeft if self.orientation == chess.WHITE
                            else Qt.AlignRight)
        for i in range(8):
            rank = (7 - i) if self.orientation == chess.WHITE else i
            rsq = chess.square(ef, rank)
            light = (chess.square_rank(rsq) + chess.square_file(rsq)) % 2 == 1
            p.setPen(QColor(t["sq_dark"] if light else t["sq_light"]))
            r = self.square_rect(rsq)
            p.drawText(r.adjusted(side * 0.05, 0, -side * 0.05, -side * 0.03),
                       hf, str(rank + 1))
            f = i if self.orientation == chess.WHITE else 7 - i
            fsq = chess.square(f, er)
            light = (chess.square_rank(fsq) + chess.square_file(fsq)) % 2 == 1
            p.setPen(QColor(t["sq_dark"] if light else t["sq_light"]))
            r = self.square_rect(fsq)
            p.drawText(r.adjusted(side * 0.05, side * 0.03, -side * 0.05, 0),
                       vf, chr(ord("a") + f))

    def _draw_pieces(self, p):
        """Rendu minimaliste style chess.com : silhouette unie, contour fin."""
        t = self.theme
        for sq, pc in self.board.piece_map().items():
            r = self.square_rect(sq)
            is_white = pc.color == chess.WHITE
            font = _font("DejaVu Sans", r.width() * 0.78)
            fm = QFontMetrics(font)
            glyph = GLYPH[pc.color][pc.piece_type]
            x = r.x() + (r.width() - fm.horizontalAdvance(glyph)) / 2.0
            y = r.y() + (r.height() - fm.height()) / 2.0 + fm.ascent()
            path = QPainterPath()
            path.addText(x, y, font, glyph)
            fill = QColor(t["white_pc"] if is_white else t["black_pc"])
            outline = QColor(t["white_ol"] if is_white else t["black_ol"])
            # Contour fin pour la netteté, remplissage uni
            p.setPen(QPen(outline, max(1.0, r.width() * 0.030)))
            p.setBrush(fill)
            p.drawPath(path)

    def mousePressEvent(self, event):
        sq = self.square_at(event.position())
        if sq is not None: self.squareClicked.emit(sq)


# ===========================================================================
#  PAGE MENU
# ===========================================================================
class MainMenuPage(QWidget):
    playRequested = Signal()
    profileRequested = Signal()
    optionsRequested = Signal()
    lichessRequested = Signal()
    quitRequested = Signal()

    def __init__(self, theme):
        super().__init__()
        self.theme_key = theme
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("DARKCHESS")
        title.setObjectName("menuTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(f"v{APP_VERSION} — Jeu d'échecs Qt")
        sub.setObjectName("menuSub")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(24)

        self.btn_play = self._mk("▶   Jouer")
        self.btn_profile = self._mk("🤖   Profil de l'IA")
        self.btn_options = self._mk("⚙   Options")
        self.btn_lichess = self._mk("♟   Ouvrir Lichess.org")
        self.btn_quit = self._mk("✕   Quitter")
        for b in (self.btn_play, self.btn_profile, self.btn_options,
                  self.btn_lichess, self.btn_quit):
            layout.addWidget(b)

        self.btn_play.clicked.connect(self.playRequested.emit)
        self.btn_profile.clicked.connect(self.profileRequested.emit)
        self.btn_options.clicked.connect(self.optionsRequested.emit)
        self.btn_lichess.clicked.connect(self.lichessRequested.emit)
        self.btn_quit.clicked.connect(self.quitRequested.emit)

    def _mk(self, text):
        b = QPushButton(text)
        b.setObjectName("menuBtn")
        b.setMinimumHeight(52)
        b.setCursor(Qt.PointingHandCursor)
        return b

    def apply_theme(self, t):
        self.theme_key = t.get("_key", "clair")
        self.setStyleSheet(f"""
            QWidget {{ background: {t['window_bg']}; }}
            QLabel#menuTitle {{ color: {t['text']}; font-size: 46px;
                font-weight: 900; letter-spacing: 8px; }}
            QLabel#menuSub {{ color: {t['muted']}; font-size: 13px; }}
            QPushButton#menuBtn {{
                background: {t['panel_bg']}; color: {t['text']};
                border: 1px solid {t['panel_brd']}; border-radius: 12px;
                font-size: 16px; padding: 10px 20px;
            }}
            QPushButton#menuBtn:hover {{
                background: {t['accent']}; color: {t['accent_txt']};
                border-color: {t['accent']};
            }}
        """)


# ===========================================================================
#  DIALOGS
# ===========================================================================
class ProfileDialog(QDialog):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.profile = json.loads(json.dumps(profile))
        self.setWindowTitle("Profil de l'IA")
        self.setMinimumWidth(480)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        f1 = QFormLayout()
        self.ed_name = QLineEdit(self.profile.get("name", "Aurora"))
        f1.addRow("Nom :", self.ed_name)
        self.cb_mode = QComboBox()
        for k, l in AI_MODES.items(): self.cb_mode.addItem(l, k)
        i = self.cb_mode.findData(self.profile.get("ai_mode", "balanced"))
        if i >= 0: self.cb_mode.setCurrentIndex(i)
        f1.addRow("Mode par défaut :", self.cb_mode)
        self.chk_memory = QCheckBox("Activer la mémoire active")
        self.chk_memory.setChecked(self.profile.get("memory_enabled", True))
        f1.addRow("", self.chk_memory)
        root.addLayout(f1)

        fr = QFrame(); fr.setObjectName("card")
        fl = QVBoxLayout(fr); fl.setContentsMargins(12, 10, 12, 10)
        self.lbl_lvl = QLabel(); self.lbl_lvl.setObjectName("lvlLabel")
        fl.addWidget(self.lbl_lvl)
        self.xp_bar = QProgressBar(); self.xp_bar.setRange(0, 100)
        fl.addWidget(self.xp_bar)
        root.addWidget(fr)

        cf = QFrame(); cf.setObjectName("card")
        cg = QGridLayout(cf); cg.setContentsMargins(12, 10, 12, 10)
        self.sliders = {}
        for i, (k, l) in enumerate({"aggression": "Agressivité",
            "defense": "Défense", "tactics": "Tactique",
            "position": "Position", "adaptability": "Adaptabilité"}.items()):
            cg.addWidget(QLabel(l), i, 0)
            s = QSlider(Qt.Horizontal); s.setRange(0, 100)
            s.setValue(self.profile["characteristics"].get(k, 50))
            cg.addWidget(s, i, 1)
            v = QLabel(str(s.value())); v.setFixedWidth(30)
            cg.addWidget(v, i, 2)
            s.valueChanged.connect(lambda x, lbl=v: lbl.setText(str(x)))
            self.sliders[k] = s
        root.addWidget(cf)

        st = self.profile["stats"]
        lbl_stats = QLabel(
            f"<b>Parties :</b> {st.get('games', 0)} — "
            f"<b>V :</b> {st.get('wins', 0)} / "
            f"<b>D :</b> {st.get('losses', 0)} / "
            f"<b>N :</b> {st.get('draws', 0)}")
        root.addWidget(lbl_stats)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        root.addWidget(btns)
        self._update_lvl()

    def _update_lvl(self):
        lvl = self.profile.get("level", 1)
        xp = self.profile.get("xp", 0)
        self.lbl_lvl.setText(f"<b>Niveau {lvl}</b> — {xp} XP ({xp % 100}/100)")
        self.xp_bar.setValue(xp % 100)

    def get_profile(self):
        self.profile["name"] = self.ed_name.text().strip() or "Aurora"
        self.profile["ai_mode"] = self.cb_mode.currentData()
        self.profile["memory_enabled"] = self.chk_memory.isChecked()
        for k, s in self.sliders.items():
            self.profile["characteristics"][k] = s.value()
        return self.profile


class OptionsDialog(QDialog):
    def __init__(self, theme_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options")
        self.setMinimumWidth(360)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.cb_theme = QComboBox()
        self.cb_theme.addItem("Clair", "clair")
        self.cb_theme.addItem("Sombre", "sombre")
        self.cb_theme.addItem("Enfer", "enfer")
        i = self.cb_theme.findData(theme_key)
        if i >= 0: self.cb_theme.setCurrentIndex(i)
        form.addRow("Thème :", self.cb_theme)
        lay.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def selected_theme(self): return self.cb_theme.currentData()


class FastSimDialog(QDialog):
    """Dialogue pour lancer N parties IA vs IA rapidement."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulation rapide")
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)
        info = QLabel(
            "Simulation IA vs IA accélérée.\n"
            "Les parties ne sont pas affichées — seul le résultat compte\n"
            "pour faire évoluer le profil d'Aurora (XP, niveau, mémoire)."
        )
        info.setWordWrap(True)
        lay.addWidget(info)
        form = QFormLayout()
        self.spin_games = QSpinBox()
        self.spin_games.setRange(1, 100)
        self.spin_games.setValue(10)
        form.addRow("Nombre de parties :", self.spin_games)
        self.cb_mode = QComboBox()
        for k, l in AI_MODES.items(): self.cb_mode.addItem(l, k)
        form.addRow("Mode IA :", self.cb_mode)
        lay.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def values(self):
        return self.spin_games.value(), self.cb_mode.currentData()


# ===========================================================================
#  PAGE DE JEU
# ===========================================================================
RESULT_TEXT = {
    chess.Termination.CHECKMATE: "Échec et mat !",
    chess.Termination.STALEMATE: "Pat — nulle",
    chess.Termination.INSUFFICIENT_MATERIAL: "Matériel insuffisant — nulle",
    chess.Termination.SEVENTYFIVE_MOVES: "75 coups — nulle",
    chess.Termination.FIVEFOLD_REPETITION: "Répétition quintuple — nulle",
    chess.Termination.FIFTY_MOVES: "50 coups — nulle",
    chess.Termination.THREEFOLD_REPETITION: "Triple répétition — nulle",
}


class GamePage(QWidget):
    backToMenu = Signal()
    statsUpdated = Signal(dict)

    START_SECONDS = 5 * 60.0

    def __init__(self, theme_key, profile):
        super().__init__()
        self.theme_key = theme_key
        self.profile = profile
        self.ai_mode = profile.get("ai_mode", "balanced")
        self.game_id = 0
        self.engine_thinking = False
        self.mode = "pvp"
        self.human_color = chess.WHITE
        self.game_active = False
        self.board = chess.Board()
        self.clocks = {chess.WHITE: self.START_SECONDS,
                       chess.BLACK: self.START_SECONDS}
        self.move_texts = []
        self.move_uci_list = []
        self.selected = None
        self.targets = []
        self._last_running = {chess.WHITE: None, chess.BLACK: None}
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)
        self.board_widget = BoardWidget()
        self.board_widget.theme = THEMES[self.theme_key]
        root.addWidget(self.board_widget, 1)
        self.board_widget.squareClicked.connect(self.on_square_clicked)

        panel = QFrame(); panel.setObjectName("panel"); panel.setFixedWidth(280)
        lay = QVBoxLayout(panel); lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        tb = QHBoxLayout()
        self.btn_back = QPushButton("← Menu"); self.btn_back.setObjectName("smallBtn")
        self.btn_back.clicked.connect(self.backToMenu.emit); tb.addWidget(self.btn_back)
        self.btn_profile_view = QPushButton("🤖")
        self.btn_profile_view.setObjectName("smallBtn")
        self.btn_profile_view.clicked.connect(self._show_profile_quick)
        tb.addWidget(self.btn_profile_view)
        lay.addLayout(tb)

        title_black = QLabel("NOIRS"); title_black.setObjectName("sideTitle")
        title_black.setAlignment(Qt.AlignCenter); lay.addWidget(title_black)
        self.clock_black = QLabel("--:--")
        self.clock_black.setAlignment(Qt.AlignCenter)
        self.clock_black.setFixedHeight(60); lay.addWidget(self.clock_black)

        self.move_list = QListWidget(); lay.addWidget(self.move_list, 1)

        self.clock_white = QLabel("--:--")
        self.clock_white.setAlignment(Qt.AlignCenter)
        self.clock_white.setFixedHeight(60); lay.addWidget(self.clock_white)
        title_white = QLabel("BLANCS"); title_white.setObjectName("sideTitle")
        title_white.setAlignment(Qt.AlignCenter); lay.addWidget(title_white)

        # Bouton PGN permanent
        self.btn_pgn = QPushButton("📄 Exporter PGN")
        self.btn_pgn.setObjectName("smallBtn")
        self.btn_pgn.clicked.connect(self.save_pgn)
        lay.addWidget(self.btn_pgn)

        self.status_label = QLabel(""); self.status_label.setWordWrap(True)
        lay.addWidget(self.status_label)
        root.addWidget(panel)

        self.clock_labels = {chess.BLACK: self.clock_black,
                             chess.WHITE: self.clock_white}
        self.timer = QTimer(self); self.timer.setInterval(100)
        self.timer.timeout.connect(self.on_tick); self.timer.start()

    def _show_profile_quick(self):
        dlg = ProfileDialog(self.profile, self)
        if dlg.exec() == QDialog.Accepted:
            self.profile = dlg.get_profile()
            self.ai_mode = self.profile.get("ai_mode", self.ai_mode)
            AIProfile.save(self.profile)
            self.statsUpdated.emit(self.profile)

    def apply_theme(self, key):
        self.theme_key = key
        t = THEMES[key]
        self.board_widget.theme = t; self.board_widget.update()
        self.setStyleSheet(f"""
            QFrame#panel {{ background: {t['panel_bg']};
                border: 1px solid {t['panel_brd']}; border-radius: 12px; }}
            QLabel {{ color: {t['text']}; }}
            QLabel#sideTitle {{ color: {t['muted']}; font-weight: 600;
                letter-spacing: 3px; font-size: 11px; }}
            QListWidget {{ background: {t['window_bg']}; color: {t['text']};
                border: 1px solid {t['panel_brd']}; border-radius: 8px;
                font-family: 'Consolas'; font-size: 13px; padding: 4px; }}
            QListWidget::item {{ padding: 3px 8px; }}
            QListWidget::item:selected {{ background: {t['accent']};
                color: {t['accent_txt']}; }}
            QPushButton#smallBtn {{ background: {t['panel_bg']};
                color: {t['text']}; border: 1px solid {t['panel_brd']};
                border-radius: 8px; padding: 6px 10px; font-size: 12px; }}
            QPushButton#smallBtn:hover {{ background: {t['accent']};
                color: {t['accent_txt']}; }}
        """)
        self.refresh_clocks(force=True); self.refresh_status()

    def start_game(self, mode, human_color=chess.WHITE):
        self.game_id += 1
        self.mode = mode
        self.human_color = human_color
        self.board = chess.Board()
        self.clocks = {chess.WHITE: self.START_SECONDS,
                       chess.BLACK: self.START_SECONDS}
        self.move_texts = []; self.move_uci_list = []
        self.move_list.clear()
        self.selected = None; self.targets = []
        self.engine_thinking = False; self.game_active = True
        self.board_widget.board = self.board
        self.board_widget.selected = None
        self.board_widget.targets = set()
        self.board_widget.last_move = None
        self.board_widget.orientation = human_color if mode == "pvai" else chess.WHITE
        self.board_widget.update()
        titles = {"pvp": "Humain vs Humain", "pvai": "Humain vs IA",
                  "simu": "Simulation IA vs IA (Blitz 5+0)"}
        self.status(f"Partie — {titles[mode]}. IA : "
                    f"{AI_MODES.get(self.ai_mode, self.ai_mode)}")
        self.refresh_clocks(force=True); self.refresh_status()
        if mode in ("pvai", "simu"):
            if mode == "simu" or self.board.turn != self.human_color:
                QTimer.singleShot(300, self.maybe_engine_turn)

    def fmt_clock(self, s):
        s = max(0.0, s)
        return f"{int(s // 60):02d}:{int(s % 60):02d}"

    def refresh_clocks(self, force=False):
        t = THEMES[self.theme_key]
        for color, lbl in self.clock_labels.items():
            lbl.setText(self.fmt_clock(self.clocks[color]))
            running = (self.game_active and self.board.turn == color
                       and not self.board.is_game_over())
            if force or self._last_running[color] != running:
                self._last_running[color] = running
                bg = t["clock_run"] if running else t["clock_idle"]
                fg = t["accent_txt"] if running else t["text"]
                lbl.setStyleSheet(
                    f"background:{bg}; color:{fg}; border-radius:10px;"
                    f" font-size:28px; font-weight:700; font-family:'Consolas';")

    def on_tick(self):
        if self.game_active and not self.board.is_game_over():
            side = self.board.turn
            self.clocks[side] -= 0.1
            if self.clocks[side] <= 0:
                self.clocks[side] = 0.0; self.game_active = False
                winner = "Noirs" if side == chess.WHITE else "Blancs"
                self.refresh_clocks(force=True)
                self.refresh_status(f"⏱ Temps écoulé — {winner}.")
                QMessageBox.information(self, "Temps écoulé",
                    f"Victoire des {winner} au temps.")
                return
            self.refresh_clocks()

    def status(self, t): self.status_label.setText(t)

    def refresh_status(self, override=None):
        if override is not None: self.status(override); return
        if not self.game_active or self.board.is_game_over(): return
        side = "Blancs" if self.board.turn == chess.WHITE else "Noirs"
        txt = f"Trait aux {side}"
        if self.board.is_check(): txt += "  •  Échec !"
        if self.engine_thinking: txt += "  •  IA réfléchit…"
        self.status(txt)

    def refresh_move_list(self):
        self.move_list.clear()
        for i in range(0, len(self.move_texts), 2):
            w = self.move_texts[i]
            b = self.move_texts[i + 1] if i + 1 < len(self.move_texts) else ""
            self.move_list.addItem(f"{i // 2 + 1:>3}.  {w:<10} {b}")
        self.move_list.scrollToBottom()

    def on_square_clicked(self, sq):
        if not self.game_active or self.engine_thinking: return
        if self.board.is_game_over(): return
        if self.mode == "pvai" and self.board.turn != self.human_color: return
        pc = self.board.piece_at(sq)
        if self.selected is None:
            if pc is not None and pc.color == self.board.turn: self.select(sq)
            return
        if sq == self.selected: self.clear_selection(); return
        moves = [m for m in self.board.legal_moves
                 if m.from_square == self.selected and m.to_square == sq]
        if moves:
            mv = moves[0]
            if any(m.promotion for m in moves):
                choice, ok = QInputDialog.getItem(self, "Promotion",
                    "Choisissez la pièce :",
                    ["Dame", "Tour", "Fou", "Cavalier"], 0, False)
                if not ok: self.clear_selection(); return
                letter = {"Dame": chess.QUEEN, "Tour": chess.ROOK,
                          "Fou": chess.BISHOP, "Cavalier": chess.KNIGHT}[choice]
                mv = chess.Move(self.selected, sq, promotion=letter)
            self.clear_selection(); self.play_move(mv)
        elif pc is not None and pc.color == self.board.turn: self.select(sq)
        else: self.clear_selection()

    def select(self, sq):
        targets = [m.to_square for m in self.board.legal_moves
                   if m.from_square == sq]
        if not targets: self.clear_selection(); return
        self.selected = sq; self.targets = targets
        self.board_widget.selected = sq
        self.board_widget.targets = set(targets)
        self.board_widget.update()

    def clear_selection(self):
        self.selected = None; self.targets = []
        self.board_widget.selected = None
        self.board_widget.targets = set()
        self.board_widget.update()

    def play_move(self, move):
        san = self.board.san(move); uci = move.uci()
        self.board.push(move)
        self.move_texts.append(san); self.move_uci_list.append(uci)
        self.refresh_move_list()
        self.board_widget.board = self.board
        self.board_widget.last_move = move
        self.board_widget.update()
        if self.check_game_end(): return
        self.refresh_status(); self.maybe_engine_turn()

    def check_game_end(self):
        if not self.board.is_game_over(): return False
        self.game_active = False
        o = self.board.outcome()
        text = RESULT_TEXT.get(o.termination, "Partie terminée")
        self.refresh_status(f"Partie terminée — {text} ({self.board.result()})")
        self.refresh_clocks(force=True)
        self._post_game_update(self.board.result())
        self.show_end_dialog(text)
        return True

    def _post_game_update(self, result, time_expired=False):
        if self.mode == "simu":
            AIProfile.update_after_game(self.profile, result,
                                        self.move_uci_list, chess.WHITE)
            self.statsUpdated.emit(self.profile)
            QTimer.singleShot(400, self.show_feedback)

    def show_end_dialog(self, result_text):
        box = QMessageBox(self); box.setIcon(QMessageBox.Information)
        box.setWindowTitle("Fin de partie")
        box.setText(f"{result_text}\n\nRésultat : {self.board.result()}")
        if self.mode != "simu":
            box.setInformativeText("Analyse ou export ?")
            btn_fb = box.addButton("Analyse", QMessageBox.ActionRole)
            btn_pgn = box.addButton("Enregistrer PGN", QMessageBox.ActionRole)
            box.addButton("Fermer", QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() == btn_fb: self.show_feedback()
            elif box.clickedButton() == btn_pgn: self.save_pgn()
        else:
            box.setInformativeText("Partie IA vs IA — analyse automatique…")
            box.addButton("OK", QMessageBox.AcceptRole); box.exec()

    def show_feedback(self):
        if not self.move_texts: return
        total = len(self.move_texts)
        captures = sum(1 for m in self.move_texts if "x" in m)
        checks = sum(1 for m in self.move_texts if "+" in m or "#" in m)
        result = self.board.result()
        if self.mode == "pvp":
            winner = {"1-0": "Blancs", "0-1": "Noirs",
                      "1/2-1/2": "Nulle"}.get(result, "—")
        elif self.mode == "simu":
            winner = {"1-0": "Aurora (Blancs)", "0-1": "Aurora (Noirs)",
                      "1/2-1/2": "Nulle"}.get(result, "—")
        else:
            won = ((result == "1-0" and self.human_color == chess.WHITE) or
                   (result == "0-1" and self.human_color == chess.BLACK))
            winner = "Vous" if won else "Aurora"
        lvl = self.profile.get("level", 1); xp = self.profile.get("xp", 0)
        st = self.profile.get("stats", {})
        html = (f"<h3>Analyse</h3><table cellspacing='4'>"
                f"<tr><td><b>Coups :</b></td><td>{total}</td></tr>"
                f"<tr><td><b>Captures :</b></td><td>{captures}</td></tr>"
                f"<tr><td><b>Échecs :</b></td><td>{checks}</td></tr>"
                f"<tr><td><b>Résultat :</b></td><td>{result}</td></tr>"
                f"<tr><td><b>Vainqueur :</b></td><td>{winner}</td></tr>"
                f"</table><h4>Profil Aurora</h4>"
                f"<p>Niveau <b>{lvl}</b> — {xp} XP<br>"
                f"{st.get('games', 0)} parties : {st.get('wins', 0)} V / "
                f"{st.get('losses', 0)} D / {st.get('draws', 0)} N</p>")
        QMessageBox.information(self, "Feedback", html)

    def _player_name(self, color):
        if self.mode == "pvp":
            return "Blancs" if color == chess.WHITE else "Noirs"
        if self.mode == "simu":
            return f"Aurora ({'Blancs' if color == chess.WHITE else 'Noirs'})"
        if color == self.human_color: return "Humain"
        return f"Aurora ({AI_MODES.get(self.ai_mode, '—')})"

    def save_pgn(self):
        """Export PGN permanent — compatible lichess.org."""
        if not self.move_texts:
            QMessageBox.information(self, "Aucun coup",
                                    "La partie n'a pas encore commencé.")
            return
        name = f"darkchess_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la partie", name, "Fichiers PGN (*.pgn)")
        if not path: return
        game = chess.pgn.Game()
        game.headers["Event"] = "Darkchess"
        game.headers["Site"] = "Local"
        game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
        game.headers["White"] = self._player_name(chess.WHITE)
        game.headers["Black"] = self._player_name(chess.BLACK)
        game.headers["Result"] = self.board.result()
        game.headers["Annotator"] = f"Darkchess {APP_VERSION}"
        node = game; board = chess.Board()
        for san in self.move_texts:
            try: mv = board.parse_san(san)
            except ValueError: break
            node = node.add_main_variation(mv); board.push(mv)
        try:
            with open(path, "w", encoding="utf-8") as f:
                print(game, file=f, end="\n\n")
            QMessageBox.information(self, "PGN enregistré",
                f"Fichier sauvegardé :\n{path}\n\n"
                f"Importable sur lichess.org → Mes études → Importer.")
        except OSError as e:
            QMessageBox.warning(self, "Erreur",
                                f"Impossible d'enregistrer :\n{e}")

    def compute_ai_think_time(self, board):
        rem = self.clocks[board.turn]
        if rem <= 5: return max(0.3, rem * 0.15)
        mn = board.fullmove_number; pieces = len(board.piece_map())
        if mn <= 8: frac = 0.015
        elif pieces > 16: frac = 0.035
        elif pieces > 10: frac = 0.040
        else: frac = 0.030
        base = rem * frac * random.uniform(0.6, 1.4)
        return max(0.3, min(base, rem * 0.12))

    def maybe_engine_turn(self):
        if not self.game_active or self.board.is_game_over(): return
        if self.engine_thinking: return
        if self.mode == "pvp": return
        if self.mode == "pvai" and self.board.turn == self.human_color: return
        self.engine_thinking = True; self.refresh_status()
        gid = self.game_id
        think = self.compute_ai_think_time(self.board)
        self.thread = EngineThread(self.board.copy(), think, gid,
                                   self.ai_mode, self.profile)
        self.thread.moveReady.connect(self.on_engine_move)
        self.thread.start()

    def on_engine_move(self, uci, gid):
        if gid != self.game_id: return
        self.engine_thinking = False
        if not self.game_active: return
        if uci == "0000": self.check_game_end(); return
        QTimer.singleShot(150, lambda: self._apply_engine_move(uci, gid))

    def _apply_engine_move(self, uci, gid):
        if gid != self.game_id or not self.game_active: return
        try: mv = chess.Move.from_uci(uci)
        except ValueError: return
        if mv in self.board.legal_moves: self.play_move(mv)


# ===========================================================================
#  SIMULATION RAPIDE (IA vs IA sans UI)
# ===========================================================================
def run_fast_simulation(n_games, mode, profile, progress_cb=None):
    """Joue n_games parties IA vs IA en arrière-plan. Retourne le profil mis à jour."""
    engine = Engine(mode=mode, profile=profile)
    results = {"w": 0, "l": 0, "d": 0}
    for i in range(n_games):
        board = chess.Board()
        uci_moves = []
        max_moves = 200
        while not board.is_game_over() and len(uci_moves) < max_moves:
            mv = engine.best_move_fast(board, depth=2)
            if mv is None: break
            uci_moves.append(mv.uci())
            board.push(mv)
        result = board.result()
        if result == "1/2-1/2": results["d"] += 1
        elif result == "1-0": results["w"] += 1
        else: results["l"] += 1
        # Simuler un résultat pour le profil (considérer l'IA = blancs)
        AIProfile.update_after_game(profile, result, uci_moves, chess.WHITE)
        if progress_cb: progress_cb(i + 1, n_games)
    return profile, results


# ===========================================================================
#  FENÊTRE PRINCIPALE
# ===========================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1040, 740)
        self.profile = AIProfile.load()
        self.theme_key = "clair"

        self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.menu_page = MainMenuPage(self.theme_key)
        self.game_page = GamePage(self.theme_key, self.profile)
        self.stack.addWidget(self.menu_page); self.stack.addWidget(self.game_page)

        self.menu_page.playRequested.connect(self.go_to_game)
        self.menu_page.profileRequested.connect(self.show_profile)
        self.menu_page.optionsRequested.connect(self.show_options)
        self.menu_page.lichessRequested.connect(self.open_lichess)
        self.menu_page.quitRequested.connect(self.close)
        self.game_page.backToMenu.connect(self.go_to_menu)
        self.game_page.statsUpdated.connect(self.on_stats_updated)

        self._build_menus(); self.apply_theme("clair")
        self.stack.setCurrentWidget(self.menu_page)

    def _act(self, menu, text, handler, shortcut=None, checkable=False,
             checked=False, group=None):
        a = QAction(text, self)
        if shortcut: a.setShortcut(shortcut)
        a.setCheckable(checkable); a.setChecked(checked)
        if group: group.addAction(a)
        a.triggered.connect(lambda *_, h=handler: h())
        menu.addAction(a); return a

    def _build_menus(self):
        bar = self.menuBar()

        m_p = bar.addMenu("&Partie")
        self._act(m_p, "Humain vs &Humain", lambda: self.go_to_game("pvp"), "Ctrl+N")
        self._act(m_p, "Humain vs IA — &Blancs",
                  lambda: self.go_to_game("pvai", chess.WHITE), "Ctrl+1")
        self._act(m_p, "Humain vs IA — &Noirs",
                  lambda: self.go_to_game("pvai", chess.BLACK), "Ctrl+2")
        self._act(m_p, "&Simulation IA vs IA",
                  lambda: self.go_to_game("simu"), "Ctrl+S")
        m_p.addSeparator()
        self._act(m_p, "← &Menu principal", self.go_to_menu, "Escape")
        self._act(m_p, "&Quitter", self.close, "Ctrl+Q")

        m_ia = bar.addMenu("&IA")
        g = QActionGroup(self); g.setExclusive(True)
        for k in ("balanced", "aggressive", "defensive", "chaotic",
                  "tactician", "strategist", "polyvalent"):
            a = self._act(m_ia, AI_MODES[k], lambda kk=k: self.set_ai_mode(kk),
                          checkable=True,
                          checked=(k == self.profile.get("ai_mode")), group=g)
            if k == self.profile.get("ai_mode"): self.act_ai_current = a

        m_a = bar.addMenu("&Affichage")
        gt = QActionGroup(self); gt.setExclusive(True)
        self.act_light = self._act(m_a, "Thème &clair",
            lambda: self.apply_theme("clair"), checkable=True, checked=True, group=gt)
        self.act_dark = self._act(m_a, "Thème &sombre",
            lambda: self.apply_theme("sombre"), checkable=True, group=gt)
        self.act_hell = self._act(m_a, "Thème &enfer",
            lambda: self.apply_theme("enfer"), checkable=True, group=gt)
        m_a.addSeparator()
        self._act(m_a, "&Retourner l'échiquier", self.flip_board, "Ctrl+F")
        self._act(m_a, "Afficher les coups &légaux", self.toggle_legal,
                  checkable=True, checked=True)

        m_o = bar.addMenu("&Outils")
        self._act(m_o, "🤖 Profil de l'IA…", self.show_profile, "Ctrl+P")
        self._act(m_o, "⚡ Simulation rapide (10 parties)…",
                  self.show_fast_sim, "Ctrl+Shift+S")
        self._act(m_o, "📄 Exporter la partie (PGN)…",
                  self.game_page.save_pgn, "Ctrl+E")
        m_o.addSeparator()
        self._act(m_o, "♟ Ouvrir Lichess.org", self.open_lichess, "Ctrl+L")
        self._act(m_o, "⚙ Options…", self.show_options, "Ctrl+O")

        m_h = bar.addMenu("&Aide")
        self._act(m_h, "À &propos", self.show_about, "F1")

    def go_to_game(self, mode="pvp", human_color=chess.WHITE):
        self.game_page.start_game(mode, human_color)
        self.stack.setCurrentWidget(self.game_page)

    def go_to_menu(self):
        self.game_page.game_active = False
        self.stack.setCurrentWidget(self.menu_page)

    def set_ai_mode(self, mode):
        self.profile["ai_mode"] = mode
        self.game_page.ai_mode = mode
        AIProfile.save(self.profile)

    def on_stats_updated(self, profile): self.profile = profile

    def apply_theme(self, key):
        self.theme_key = key
        t = dict(THEMES[key]); t["_key"] = key
        self.menu_page.apply_theme(t)
        self.game_page.apply_theme(key)
        self.act_light.setChecked(key == "clair")
        self.act_dark.setChecked(key == "sombre")
        self.act_hell.setChecked(key == "enfer")
        self.setStyleSheet(f"""
            QMainWindow {{ background: {t['window_bg']}; }}
            QMenuBar {{ background: {t['panel_bg']}; color: {t['text']};
                border-bottom: 1px solid {t['panel_brd']}; }}
            QMenuBar::item {{ padding: 6px 12px; background: transparent; }}
            QMenuBar::item:selected {{ background: {t['accent']};
                color: {t['accent_txt']}; border-radius: 4px; }}
            QMenu {{ background: {t['panel_bg']}; color: {t['text']};
                border: 1px solid {t['panel_brd']}; }}
            QMenu::item {{ padding: 7px 28px; }}
            QMenu::item:selected {{ background: {t['accent']};
                color: {t['accent_txt']}; }}
            QDialog {{ background: {t['panel_bg']}; color: {t['text']}; }}
            QDialog QLabel {{ color: {t['text']}; }}
            QLineEdit, QComboBox, QSpinBox {{
                background: {t['window_bg']}; color: {t['text']};
                border: 1px solid {t['panel_brd']}; border-radius: 6px;
                padding: 5px 8px;
            }}
            QFrame#card {{ background: {t['window_bg']};
                border: 1px solid {t['panel_brd']}; border-radius: 10px; }}
            QLabel#lvlLabel {{ color: {t['text']}; font-size: 15px;
                font-weight: 600; }}
            QPushButton {{ background: {t['panel_bg']}; color: {t['text']};
                border: 1px solid {t['panel_brd']}; border-radius: 8px;
                padding: 7px 14px; }}
            QPushButton:hover {{ background: {t['accent']};
                color: {t['accent_txt']}; }}
            QProgressBar {{ border: 1px solid {t['panel_brd']};
                border-radius: 6px; background: {t['window_bg']};
                text-align: center; color: {t['text']}; height: 18px; }}
            QProgressBar::chunk {{ background: {t['accent']};
                border-radius: 5px; }}
            QSlider::groove:horizontal {{ height: 6px;
                background: {t['panel_brd']}; border-radius: 3px; }}
            QSlider::handle:horizontal {{ background: {t['accent']};
                width: 16px; margin: -6px 0; border-radius: 8px; }}
            QMessageBox, QInputDialog {{ background: {t['panel_bg']};
                color: {t['text']}; }}
        """)

    def flip_board(self):
        self.game_page.board_widget.orientation ^= True
        self.game_page.board_widget.update()

    def toggle_legal(self, checked):
        self.game_page.board_widget.show_legal = checked
        self.game_page.board_widget.update()

    def show_profile(self):
        dlg = ProfileDialog(self.profile, self)
        if dlg.exec() == QDialog.Accepted:
            self.profile = dlg.get_profile()
            self.game_page.profile = self.profile
            self.game_page.ai_mode = self.profile.get("ai_mode", "balanced")
            AIProfile.save(self.profile)

    def show_options(self):
        dlg = OptionsDialog(self.theme_key, self)
        if dlg.exec() == QDialog.Accepted: self.apply_theme(dlg.selected_theme())

    def show_fast_sim(self):
        dlg = FastSimDialog(self)
        if dlg.exec() != QDialog.Accepted: return
        n, mode = dlg.values()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.profile, results = run_fast_simulation(n, mode, self.profile)
            self.game_page.profile = self.profile
            QApplication.restoreOverrideCursor()
            lvl = self.profile.get("level", 1)
            xp = self.profile.get("xp", 0)
            QMessageBox.information(self, "Simulation terminée",
                f"{n} parties jouées en mode {AI_MODES[mode]}.\n\n"
                f"Résultats (IA = Blancs) :\n"
                f"• Victoires IA : {results['w']}\n"
                f"• Défaites IA : {results['l']}\n"
                f"• Nulles : {results['d']}\n\n"
                f"Niveau actuel d'Aurora : {lvl} ({xp} XP)")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Erreur", f"Simulation échouée : {e}")

    def open_lichess(self): webbrowser.open(LICHESS_URL)

    def show_about(self):
        QMessageBox.about(self, "À propos",
            f"<h3>{APP_TITLE} {APP_VERSION}</h3>"
            "<p>Échecs Qt (PySide6) &amp; python-chess.</p>"
            "<ul>"
            "<li>Menu principal, 3 thèmes (Clair/Sombre/Enfer)</li>"
            "<li>IA Aurora : 7 modes + profil RPG (XP, niveau, mémoire)</li>"
            "<li>Simulation rapide : N parties IA vs IA en quelques secondes</li>"
            "<li>Export PGN compatible lichess.org</li>"
            "</ul>")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setStyle("Fusion")
    win = MainWindow(); win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()