from random import randint

def game(players, limit=50):
    # board size
    board_size = (3, 3)

    # remember the last move for each player
    last_move = [-1, -1]

    # remember the player's locations
    location = [[randint(0, board_size[0]), randint(0, board_size[1])]]

    # put the second player at sufficient distance from the first
    location.append([(location[0][0] + 2) % 4, (location[0][1] + 2) % 4])

    # maximum of 50 moves before a tie
    for iteration in range(limit):
        # for each player
        for i in range(2):
            locs = location[i][:] + location[1-i][:]
            locs.append(last_move[i])
            move = players[i].evaluate(locs) % 4

            # you lose if you move the same direction twice in a row
            if last_move[i] == move: return 1-i
            last_move[i] = move

            # 0 for upward move
            if move == 0:
                location[i][0] -= 1
                # board limits
                if location[i][0] < 0: location[i][0] = 0

            # 1 for downward move
            if move == 1:
                location[i][0] += 1
                if location[i][0] > board_size[0]:
                    location[i][0] = board_size[0]

            # 2 for backward move
            if move == 2:
                location[i][1] -= 1
                if location[i][1] < 0: location[i][1] = 0

            # 3 for forward move
            if move == 3:
                location[i][1] += 1
                if location[i][1] > board_size[1]:
                    location[i][1] = board_size[1]

            # if you have captured the other player, you win
            if location[i] == location[1-i]: return i
    return -1

def tournament(players):
    # count losses
    losses = [0 for player in players]

    # each player plays against every other player
    for i in range(len(players)):
        for j in range(len(players)):
            if i == j: continue

            # who is the winner?
            winner = game([players[i], players[j]])

            # two points for a loss, one point for a tie
            if winner == 0:
                losses[j] += 2
            elif winner == 1:
                losses[i] += 2
            elif winner == -1:
                losses[i] += 1
                losses[j] += 1
    # sort and return the results
    zipped = zip(losses, players)
    zipped.sort()
    return zipped

class HumanPlayer:
        def evaluate(self, board):
            # get my location and the location of other players
            me = tuple(board[:2])
            others = [tuple(board[i:i+2])
                      for i in range(2, len(board)-1, 2)]

            # display the board
            for i in range(4):
                for j in range(4):
                    if (i, j) == me:
                        print 'O',
                    elif (i, j) in others:
                        print 'X',
                    else:
                        print '.',
                print

            # show moves, for reference
            print 'Your last move was %d' % board[len(board)-1]
            print ' 0'
            print '2 3'
            print ' 1'
            print 'Enter Move: ',

            # return whatever the user enters
            move = int(raw_input())
            return move