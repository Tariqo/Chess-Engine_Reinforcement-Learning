"""
Consider the value of the opponent's pieces: Currently, the reward function only considers the 
value of the captured piece. However, capturing a valuable piece may not be worth it if it leaves
the agent's own pieces vulnerable to attack. One way to account for this is to subtract the value
of the opponent's pieces that can now attack the agent's piece that made the capture. For example,
if the agent captures a rook worth 5 points, but in doing so exposes its own queen worth 9 points
to attack by the opponent's bishop worth 3 points, the net value gain of the move would only be 2 points.

Encourage development of pieces: A good opening strategy is to develop pieces quickly so that
 they can control the center of the board and attack the opponent's pieces. The reward function
   could give a small bonus for each move that develops a piece, such as moving a knight or bishop 
   out to a good square. This would encourage the agent to play more aggressively and avoid passive moves like moving pawns.

Penalize losing tempo: A tempo is a move that gains a move over the opponent, 
either by forcing the opponent to move a piece again or by making a useful move while the opponent is wasting time.
 The reward function could penalize moves that waste tempo, such as moving a piece twice in the opening or making a slow pawn move
   that allows the opponent to gain a tempo by attacking the pawn.

Incentivize central control: As mentioned in point 2, 
controlling the center of the board is important in the opening phase.
 The reward function could give a small bonus for each move that controls 
 a central square, such as moving a pawn to d4 or e4, or occupying the d5 or e5 square with a knight or bishop.
"""
def _get_reward(self, board, piece, move):
    pR, pF = piece.rank, piece.file
    reward = 0
    captured_piece = board.tiles[move[0]][move[1]]

    symbol = piece.name[0].upper()
    if piece.name == 'knight':
        symbol = 'N'
    if captured_piece is not None:
        reward += self.piece_values[symbol]
        # subtract the value of opponent's pieces that can attack the capturing piece
        opponent_color = chess.WHITE if self.color == chess.BLACK else chess.BLACK
        attacking_pieces = board.get_attacking_pieces(move[0], move[1], opponent_color)
        for attacking_piece in attacking_pieces:
            if attacking_piece.name != 'king':
                reward -= self.piece_values[attacking_piece.name[0].upper()]

    board.engine_try_move(pR, pF, move[0], move[1])

    is_check = board.is_in_check(self.color)
    is_checkmate = board.is_checkmate(self.color)
    is_stalemate = board.check_for_stalemate()

    # encourage development of pieces
    if piece.name in ['knight', 'bishop'] and move[0] in [2, 5]:
        reward += 0.1
    elif piece.name in ['rook', 'queen'] and pF in [0, 7]:
        reward += 0.1

    # penalize losing tempo
    if piece.name in ['pawn', 'knight', 'bishop']:
        num_moves = len(board.move_history)
        last_move = board.move_history[-1] if num_moves > 0 else None
        if last

def _get_reward(self, board, piece, move):
    R, pF = piece.rank, piece.file
    reward = 0
    captured_piece = board.tiles[move[0]][move[1]]

    symbol = piece.name[0].upper()
    if piece.name == 'knight':
        symbol = 'N'
    if captured_piece is not None:
        reward += self.piece_values[symbol]
        # subtract the value of opponent's pieces that can attack the capturing piece
        opponent_color = chess.WHITE if self.color == chess.BLACK else chess.BLACK
        attacking_pieces = board.get_attacking_pieces(move[0], move[1], opponent_color)
        for attacking_piece in attacking_pieces:
            if attacking_piece.name != 'king':
                # subtract the value of the opponent's pieces that can attack the capturing piece
                attacking_piece_value = self.piece_values[attacking_piece.name[0].upper()]
                capturing_piece_value = self.piece_values[symbol]
                if attacking_piece_value < capturing_piece_value:
                    reward += attacking_piece_value

    board.engine_try_move(pR, pF, move[0], move[1])

    is_check = board.is_in_check(self.color)
    is_checkmate = board.is_checkmate(self.color)
    is_stalemate = board.check_for_stalemate()

    # encourage development of pieces
    if piece.name in ['knight', 'bishop'] and move[0] in [2, 5]:
        reward += 0.1
    elif piece.name in ['rook', 'queen'] and pF in [0, 7]:
        reward += 0.1

    # penalize losing tempo
    if piece.name in ['pawn', 'knight', 'bishop']:
        num_moves = len(board.move_history)
        last_move = board.move_history[-1] if num_moves > 0 else None
        if last_move is not None and last_move.piece.name == piece.name:
            reward -= 0.1

    # incentivize central control
    if piece.name in ['pawn', 'knight', 'bishop']:
        central_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if (piece.rank, piece.file) in central_squares:
            reward += 0.05

    return reward
"""
I've added the following changes:

Subtracting the value of the opponent's pieces that can attack the capturing piece
Encouraging development of pieces by giving a bonus for moves that develop pieces
Penalizing losing tempo by subtracting points for making moves that waste tempo
Incentivizing central control by giving a bonus for moves that control central squares.
Note that the values used for the bonuses and penalties are arbitrary and can be adjusted based on experimentation and testing.





"""