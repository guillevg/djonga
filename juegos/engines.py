def tres_en_raya_is_valid_move(*args, **kwargs):
    LINEAS = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    tablero = kwargs.get('tablero', None)
    player = kwargs.get('player', None)
    move = kwargs.get('move', None)
    print('tres_en_raya_is_...')
    print('tablero =', tablero)
    print('player =', player)
    print('move =', move)

    if len(tablero) == 9:
        print('Tablero lleno')
        return False  # Tablero lleno
    elif str(move) in tablero:
        print('Casilla ocupada')
        return False  # La casilla está ocupada
    elif player != 'OX'[len(tablero) % 2]:
        print('No es el turno de este jugador')
        return False  # No es el turno de este jugador
    casillas = [' ' for _ in range(9)]
    for i, el in enumerate(tablero):
        casillas[int(el)] = 'OX'[i % 2]
    casillas[int(move)] = player
    for i, j, k in LINEAS:
        if player and casillas[i] == casillas[j] == casillas[k] == player:
            return player
    return True

def tres_en_raya_is_valid_move_2(*args, **kwargs):
    tablero = kwargs.get('tablero', None)
    player = kwargs.get('player', None)
    move = kwargs.get('move', None)
    print('tres_en_raya_is_...\n', tablero, player, move)

    if len(tablero) == 9:
        print('Tablero lleno')
        return False  # Tablero lleno
    elif str(move) in tablero:
        print('Casilla ocupada')
        return False  # La casilla está ocupada
    elif player != 'OX'[len(tablero) % 2]:
        print('No es el turno de este jugador')
        return False  # No es el turno de este jugador
    print('OK')
    return True


ENGINE_DICT = {
    'tres-en-raya': tres_en_raya_is_valid_move,
}
