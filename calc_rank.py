#!/usr/bin/env python3

RANKING_FILE = "current_rankings.txt"   # The name of the file holding the current tournament standings
NQ_FILE = "not_qualified.txt"           # The file to hold the players without enough games to qualify
GAME_FILE = "game_{}.txt"               # The name structure for the file saved for each tournament game
NEW_PLAYER_START_RATING = 1500          # The start rating given to players (first game will adjust from this value)
KILLS_VALUE = 1.0                       # The multiplier used for game kills (used if USE_PLAYER_KILLS is True)
QUALIFYING_GAME_COUNT = 10              # The number of games a player must play before their rating counts
MINIMUM_PLAYERS = 5                     # The minimum players needed for a tournament game

USE_PLAYER_KILLS = True                # True = Uses player kills in game in rating adjustment calculation
PRINT_ERRORS = False

VERSION = 2.0


class PUBGRatings(object):
    def __init__(self):
        self.__players = []
        self.__save_players = []
        self.__comments = []
        self.__game_data = []
        self.__results = []
        self.__not_qualified = []
        self.__names = []

        self.process_data()

    @staticmethod
    def games_exist():
        count = 1
        while True:
            try:
                t = open(GAME_FILE.format(count), 'r')
                t.close()
            except:
                break
            count += 1
        return count - 1 if count > 1 else 0

    def adjustment(self, players, total_players):
        # {'name': name, 'position': position, 'kills': kills, 'games': games,
        #  'rating': rating, 'prev_kills': previous_kills}
        adjustments = {}
        while len(players) > 1:
            if players[0]['name'] not in adjustments:
                adjustments[players[0]['name']] = []
            tr1 = 10 ** (players[0]['rating'] / 400)
            second = 1
            tr2 = 0
            while tr2 != -1:
                try:
                    if players[second]['name'] not in adjustments:
                        adjustments[players[second]['name']] = []
                    tr2 = 10 ** (players[second]['rating'] / 400)
                    adj1 = 20 * (1 - (tr1 / (tr1 + tr2)))
                    adjustments[players[0]['name']].append(adj1)
                    adj2 = 20 * (0 - (tr2 / (tr1 + tr2)))
                    adjustments[players[second]['name']].append(adj2)
                    second += 1
                except IndexError:
                    tr2 = -1
            del players[0]
        for player, adj in adjustments.items():
            adjustments[player] = sum(adj) / (total_players - 1)
        return adjustments

    def get_data(self):
        self.__players = []
        self.__comments = []
        found = 0
        qualified = 0
        try:
            count = 0
            try:
                file = open(RANKING_FILE, 'r')
                lines = file.readlines()
                file.close()
                for line in lines:
                    if line.startswith("#"):
                        self.__comments.append(line)
                        continue
                    player = line.split(",")
                    self.__players.insert(count, {})
                    self.__players[count]['name'] = player[0]
                    self.__players[count]['rank'] = int(player[1])
                    self.__players[count]['rating'] = float(player[2])
                    self.__players[count]['kills'] = int(player[3])
                    self.__players[count]['games'] = int(player[4].strip())
                    count += 1
                qualified = count
            except FileNotFoundError:
                found = -1
            try:
                file = open(NQ_FILE, 'r')
                lines = file.readlines()
                file.close()
                for line in lines:
                    player = line.split(",")
                    self.__players.insert(count, {})
                    self.__players[count]['name'] = player[0]
                    self.__players[count]['rank'] = int(player[1])
                    self.__players[count]['rating'] = float(player[2])
                    self.__players[count]['kills'] = int(player[3])
                    self.__players[count]['games'] = int(player[4].strip())
                    count += 1
            except FileNotFoundError:
                if found == -1:
                    found = -3
                else:
                    found = -2

        except Exception as e:
            if PRINT_ERRORS:
                print("Error getting existing data: {}".format([e]))
        return found, qualified

    def write_data(self):
        try:
            file = open(RANKING_FILE, 'w')
            for line in self.__comments:
                file.write(line + "\n")
            for player in self.__save_players:
                file.write("{0[name]},{0[rank]},{0[rating]},{0[kills]},{0[games]}\n".format(player))
            file.close()
            file = open(NQ_FILE, 'w')
            for player in self.__not_qualified:
                file.write("{0[name]},{0[rank]},{0[rating]},{0[kills]},{0[games]}\n".format(player))
            file.close()
            return True
        except Exception as e:
            if PRINT_ERRORS:
                print("Error writing data: {}".format([e]))
            return False

    def save_game(self):
        count = 1
        while True:
            try:
                t = open(GAME_FILE.format(count), 'r')
                t.close()
            except:
                break
            count += 1
        try:
            file = open(GAME_FILE.format(count), 'w')
            file.write("#name, finish position, kills, old_rating, adjustment, new_rating\n")
            for player in self.__results:
                file.write("{},{},{},{},{},{}\n"
                           .format(player['name'], player['position'], player['kills'], player['rating'],
                                   player['adjustment'], player['new_rating']))
            file.close()
        except Exception as e:
            if PRINT_ERRORS:
                print("Error writing game data: {}".format([e]))

    def process_games(self):
        count = 1
        games_results = []
        while True:
            try:
                g = open(GAME_FILE.format(count), 'r')
                lines = g.readlines()
                g.close()
                rank = 1
                player_count = 0
                players = []

                for line in lines:
                    if line.startswith("#"):
                        continue
                    player_count += 1
                    player = line.split(",")
                    name = player[0]
                    position = int(player[1])
                    kills = int(player[2])
                    games = 1
                    rating = NEW_PLAYER_START_RATING
                    previous_kills = 0
                    for p in games_results:
                        if p['name'] == name:
                            games = p['games'] + 1
                            rating = p['rating']
                            previous_kills = p['kills']
                            games_results.remove(p)
                            break
                    players.append({'name': name, 'position': position, 'kills': kills, 'games': games,
                                    'rating': rating, 'prev_kills': previous_kills})

                ordered = []
                for p in players:
                    pos = 0
                    for r in ordered:
                        if r['position'] > p['position']:
                            break
                        pos += 1
                    ordered.insert(pos, p)
                adjustments = self.adjustment(ordered.copy(), player_count)

                for player in ordered:
                    player['new_rating'] = player['rating'] + adjustments[player['name']]
                    pos = 0
                    for p in games_results:
                        if p['rating'] > player['new_rating'] or p['rating'] == player['new_rating'] and\
                                p['kills'] > player['kills']:
                            break
                        pos += 1
                    games_results.insert(pos, {})
                    games_results[pos]['name'] = player['name']
                    games_results[pos]['rating'] = player['new_rating']
                    games_results[pos]['kills'] = player['kills'] + player['prev_kills']
                    games_results[pos]['games'] = player['games']
                    if count > 1:
                        rank += 1

            except FileNotFoundError:
                break
            except Exception as e:
                print("File {} read exception: {}".format(count, [e]))
            count += 1

        self.__save_players = games_results
        self.__not_qualified = []
        pos = len(self.__save_players)
        while pos > 0:
            pos -= 1
            if self.__save_players[pos]['games'] < QUALIFYING_GAME_COUNT:
                self.__not_qualified.insert(0, self.__save_players[pos])
                del self.__save_players[pos]

        for x in range(len(self.__save_players)):
            self.__save_players[x]['rank'] = x + 1
        for x in range(len(self.__not_qualified)):
            self.__not_qualified[x]['rank'] = x + 1

        if self.write_data():
            print("Processing Existing game files completed.\n")
        else:
            print("Error processing existing game files.\n")
        self.__save_players = []
        self.__not_qualified = []
        return True

    def process_data(self):
        print("Starting PUBG Tournament Ranking program {}".format(self.__class__.__name__))
        files = self.get_data()
        if files[0] > -3:
            message = ["Current Player Standings: {} Player Records {} Qualified\n(Name : Rank Rating Kills Games)"
                       .format(len(self.__players), files[1])]
            for player in self.__players:
                message.append("{0[name]:6}: {0[rank]:>2} {1:>7} {0[kills]:>6} {0[games]:>5}"
                               .format(player, round(float(player["rating"]), 2)))
            print("\n".join(message))
        else:
            recorded_games = self.games_exist()
            if recorded_games:
                process_games = input("There {0} {1} game{2} files but no ranking file. Would you like to process"
                                      " the game{2} file{2} (y/N)? "
                                      .format("are" if recorded_games > 1 else "is", recorded_games,
                                              "s" if recorded_games > 1 else ""))
                if not process_games or process_games.lower() == 'n':
                    print("This is the first recorded game of the tournament.")
                else:
                    if self.process_games():
                        files = self.get_data()
                        if files[0] > -3:
                            message = ["Current Player Standings: {} Player Records {} Qualified\n"
                                       "(Name : Rank Rating Kills Games)"
                                       .format(len(self.__players), files[1])]
                            for player in self.__players:
                                message.append("{0[name]:6}: {0[rank]:>2} {1:>7} {0[kills]:>6} {0[games]:>5}"
                                               .format(player, round(float(player["rating"]), 2)))
                            print("\n".join(message))
            else:
                print("This is the first recorded game of the tournament.")

        print("\n***Input Game Results***")
        while True:
            try:
                total_players = int(input("Number of Players in Game (0 to quit): "))
            except ValueError:
                print("The value must be a number")
                continue
            if total_players == 0:
                print("Exiting Program.")
                exit()
            elif total_players < MINIMUM_PLAYERS:
                print("The participating players mut be at least {}. Exiting Program.".format(MINIMUM_PLAYERS))
                exit()
            break
        print("\n")

        def get_data(num):
            for c in range(num):
                redo = True
                while redo:
                    name = input("Player Name: ")
                    while name in self.__names:
                        print("That name has already been input. Input so far: {}".format(", ".join(self.__names)))
                        name = input("Player Name: ")
                        if name not in self.__names:
                            break
                    self.__names.append(name)
                    if name in ["stop", "quit", "done", "exit"]:
                        break
                    while True:
                        try:
                            position = int(input("Player's Finishing Position: "))
                        except ValueError:
                            print("The value must be a number")
                            continue
                        break
                    while True:
                        try:
                            game_kills = int(input("Player's kills in Game: "))
                        except ValueError:
                            print("The value must be a number")
                            continue
                        break
                    print("Data Entered: {} {} {}".format(name, position, game_kills))
                    correct = input("Is this correct (Y/n)? ")
                    if not correct or correct.lower() == 'y':
                        redo = False
                        self.__game_data.insert(c, {})
                        self.__game_data[c]['name'] = name
                        self.__game_data[c]['position'] = position
                        self.__game_data[c]['kills'] = game_kills
                    else:
                        self.__names.remove(name)
                print("\n")

        get_data(total_players)
        while len(self.__game_data) != total_players:
            print("The Players entered does not match the number of players reported as playing.")
            get_more = input("Do you want to enter more data (Y/n)? ")
            if not get_more or get_more.lower() == "y":
                get_data(total_players - len(self.__game_data))
            else:
                total_players = len(self.__game_data)

        for participant in self.__game_data:
            games_played = 1
            rating = NEW_PLAYER_START_RATING
            previous_kills = 0
            for player in self.__players:
                if player['name'] == participant['name']:
                    games_played = player['games'] + 1
                    rating = player['rating']
                    previous_kills = player['kills']
                    self.__players.remove(player)
                    break
            participant['games'] = games_played
            participant['rating'] = rating
            participant['prev_kills'] = previous_kills

        for player in self.__game_data:
            count = 0
            for reorder in self.__results:
                if reorder['position'] > player['position']:
                    break
                count += 1
            self.__results.insert(count, player)

        adjustments = self.adjustment(self.__results.copy(), total_players)
        for player in self.__results:
            player['adjustment'] = adjustments[player['name']]
            player['new_rating'] = player['rating'] + player['adjustment']

        self.save_game()

        for player in self.__players:
            count = 0
            for save in self.__save_players:
                if save['rating'] > player['rating']:
                    break
                elif save['rating'] == player['rating'] and save['kills'] > player['kills']:
                    break
                count += 1
            self.__save_players.insert(count, {})
            self.__save_players[count]['name'] = player['name']
            self.__save_players[count]['rating'] = player['rating']
            self.__save_players[count]['kills'] = player['kills']
            self.__save_players[count]['games'] = player['games']

        for results in self.__results:
            count = 0
            for save in self.__save_players:
                if save['rating'] > results['new_rating']:
                    break
                elif save['rating'] == results['new_rating'] and save['kills'] > results['kills']:
                    break
                count += 1
            self.__save_players.insert(count, {})
            self.__save_players[count]['name'] = results['name']
            self.__save_players[count]['rating'] = results['new_rating']
            self.__save_players[count]['kills'] = results['kills'] + results['prev_kills']
            self.__save_players[count]['games'] = results['games']

        pos = len(self.__save_players)
        while pos > 0:
            pos -= 1
            if self.__save_players[pos]['games'] < QUALIFYING_GAME_COUNT:
                self.__not_qualified.insert(0, self.__save_players[pos])
                del self.__save_players[pos]

        for x in range(len(self.__save_players)):
            self.__save_players[x]['rank'] = x + 1
        for x in range(len(self.__not_qualified)):
            self.__not_qualified[x]['rank'] = x + 1

        self.write_data()
        print("New Rankings: {} Qualified\n(Name: Rank Rating Kills Games)".format(len(self.__save_players)))
        for player in self.__save_players:
            print("{0[name]:6}: {0[rank]:>2} {1:>7} {0[kills]:>6} {0[games]:>5}"
                  .format(player, round(float(player["rating"]), 2)))
        # print("\n")
        print("\nNot Yet Qualified: {} Players\n(Name: Rating Kills Games)".format(len(self.__not_qualified)))
        for player in self.__not_qualified:
            print("{0[name]:6}: {1:>7} {0[kills]:>6} {0[games]:>5}"
                  .format(player, round(float(player["rating"]), 2)))
        print("\n")


def main():
    if __name__ == '__main__':
        PUBGRatings()
        while True:
            input_again = input("Do you want to enter another game? (y/N): ")
            if not input_again or input_again.lower() == 'n':
                break
            PUBGRatings()


main()
