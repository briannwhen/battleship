import sys
import pygame
import json
import random


class SpriteClass(pygame.sprite.Sprite):
    """
    Taken from the textbook ImageSprite class. Creates a sprite representation given a position and filename
    """
    def __init__(self, x, y, filename) :
        super().__init__()
        self.loadImage(x, y, filename)

    def loadImage(self, x, y, filename) :
        img = pygame.image.load(filename)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.rect.height

class Board(SpriteClass):
    """
    Grid for both boards
    """
    def __init__(self, x, y):
        super().__init__(x, y, "grid.png")
        self._layer = 1

class Ship(SpriteClass):
    """
    Represents a unit of a Ship
    """
    def __init__(self, x, y):
        super().__init__(x, y, "ship.png")
        self._layer = 2

class Attack(SpriteClass):
    """
    Attack unit for when a hit is made
    """
    def __init__(self, x, y):
        super().__init__(x, y, "attack.png")
        self._layer = 3

class Missed(SpriteClass):
    """
    Sprite that displays a missed attempt by the player
    """
    def __init__(self, x, y):
        super().__init__(x, y, "missed.png")
        self._layer = 2


class Player:
    """
    Holds a 2d array of boolean values (all false initially)
    The functions provided allow the class user to toggle the boolean value and see if it is set to True
    The function isAllFalse tests whether there are any True values in the 2d array.
    """
    def __init__(self):
        self._array = [[False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False],
                     [False, False, False, False, False, False, False, False, False, False]]

    def isTrue(self, row, col):
        """
        :param row: integer - row value
        :param col: integer - column value
        :return: True if the corresponding instance array value is True
        """
        if self._array[row - 1][col - 1]:
            return True
        else:
            return False

    def makeTrue(self, row, col):
        self._array[row - 1][col - 1 ] = True

    def makeFalse(self, row, col):
        self._array[row - 1][col - 1 ] = False

    def isAllFalse(self):
        if self._array == [[False] * 10] * 10:
            return True
        else:
            return False


class Battleship:
    """
    Provides functions to run and start a battleship game. The game will display on a 900 by 500 pixel screen.
    """
    def __init__(self):
        """
        Initializes all the necessary game variables and starts the game
        """
        pygame.init()
        self.loadJson()    # Opens the JSON file that contains the ship data for the computer and the player
        self._screen = pygame.display.set_mode((900, 500))      # Start the game
        self._clock = pygame.time.Clock()
        self._allSprites = pygame.sprite.LayeredUpdates()
        self._text = ""                     #     Initialize the text box
        self._font = pygame.font.Font(None, 32)
        self._inputBox = pygame.Rect(100, 430, 140, 32)
        self._colorInactive = pygame.Color('lightskyblue3')
        self._colorActive = pygame.Color('dodgerblue2')
        self._color = self._colorInactive
        self._active = False
        self._ticks = 0     # Game time
        self._user = Player()       #   Initialize all the necessary virtual grids
        self._computer = Player()
        self._attempts = Player()
        self._potentials = Player()
        self._playerAttempts = Player()
        self._playerCount = 17      # Initialize ship counts for each user
        self._computerCount = 17
        self._gameOver = False      #  Controls the game over screen

    def loadJson(self):
        file = open("usrData.json")
        self._data = json.load(file)

    def update(self):
        """
        Function that displays all sprites in the allSprites group at each loop of the game.
        """
        self._allSprites.update()

    def draw(self):
        """
        Draws allSprites group to the screen
        """
        self._allSprites.draw(self._screen)

    def add(self, sprite):
        """
        Adds a sprite to the group of sprites that gets displayed to the screen.
        :param sprite: Expects an instance of SpriteClass or one of its subclasses
        """
        self._allSprites.add(sprite)

    def getTicks(self):
        return self._ticks

    def letterSwitch(self, letter):
        """
        :param letter: Single letter within the range of A - J
        :return: Corresponding number in increasing order starting from A - 1
        """
        letters = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10}
        return letters[letter]

    def initFleet(self, letter, number, shipName, orient):
        """
        :param letter: row letter of the starting position of the ship
        :param number: column value of the starting position of the ship
        :param shipName: string contains the ship name that will be added
        :param orient: a single letter denoting the orientation of ship placement
        :return: this function will place the ships passed to it onto the players board
        """
        ships = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Submarine": 3, "Destroyer": 2}
        rowVal = self.letterSwitch(letter.upper())       # convert passed letter to a integer row value
        columnVal = number

        if orient == "h":       # Horizontal case.
            if columnVal + (ships[shipName] -1) > 10:       # Test for out of range. If so quit the game.
                print("Out of range")
                pygame.quit()
                sys.exit()
            else:
                for i in range(columnVal, columnVal + (ships[shipName])):     # Test if any ship collides.
                    if not self._user.isTrue(rowVal, i):
                        self._user.makeTrue(rowVal, i)
                    else:
                        print("Overlap")                # If there is a collision between placed ships, the game quits.
                        pygame.quit()
                        sys.exit()
                for i in range(columnVal, columnVal + (ships[shipName])):     # If the ship meets the requirements,
                    self.add(Ship(48 + (34 * i), 46 + (34 * rowVal)))         # it will be printed to the screen

        elif orient == "v":     # Similar to the code block directly above. Handles the vertical case.
            if rowVal + (ships[shipName] -1) > 10:
                print("Out of range")
                pygame.quit()
                sys.exit()
            else:
                for i in range(rowVal, rowVal + (ships[shipName])):
                    if not self._user.isTrue(i, columnVal):
                        self._user.makeTrue(i, columnVal)
                    else:
                        print("Overlap")
                        pygame.quit()
                        sys.exit()
                for i in range(rowVal, rowVal + (ships[shipName])):
                    self.add(Ship(48 + (34 * columnVal), 46 + (34 * i)))

    def initEnemyFleet(self, letter, number, shipName, orient):
        """
        :param letter: row letter of the starting position of the ship
        :param number: column value of the starting position of the ship
        :param shipName: string contains the ship name that will be added
        :param orient: a single letter denoting the orientation of ship placement
        :return: this function does not place any ships onto the screen. It will only alter the boolean array of the computer.
        """
        ships = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Submarine": 3, "Destroyer": 2}
        rowVal = self.letterSwitch(letter.upper())     # Get the corresponding number from the letter
        columnVal = number

        if orient == "h":       # Horizontal case.
            if columnVal + (ships[shipName] -1) > 10:       # Test for out of bounds. If so then quit
                print("Out of range")
                pygame.quit()
                sys.exit()
            else:
                for i in range(columnVal, columnVal + (ships[shipName])):
                    if not self._computer.isTrue(rowVal, i):        # Test for overlapping ships
                        self._computer.makeTrue(rowVal, i)          # if no overlap, then set the boolean array to true
                    else:
                        print("Overlap")                # if overlapped, quit
                        pygame.quit()
                        sys.exit()

        elif orient == "v":     # Similar to code block directly above. Handles the vertical case.
            if rowVal + (ships[shipName] -1) > 10:
                print("Out of range")
                pygame.quit()
                sys.exit()
            else:
                for i in range(rowVal, rowVal + (ships[shipName])):
                    if not self._computer.isTrue(i, columnVal):
                        self._computer.makeTrue(i, columnVal)
                    else:
                        print("Overlap")
                        pygame.quit()
                        sys.exit()

    def changePotentials(self, row, col):
        """
        If a cell is hit, then all the surrounding cells will be made true in the potentials array, only if the cell
        has not already been visited. The length of this function comes from handling the edge cases.
        :param row: number from 1 to 10
        :param col: number from 1 to 10
        :return: changes the "hunt" locations of the bot intelligence whenever hits are made by the computer
        """
        if row == 1:
            if col == 1:
                if not self._attempts.isTrue(1, 2):         # Checks if already visited
                    self._potentials.makeTrue(1, 2)         # If not visited, then make the corresponding potential array true
                if not self._attempts.isTrue(2, 1):
                    self._potentials.makeTrue(2, 1)
            elif col <= 9 and col >= 2:
                if not self._attempts.isTrue(1, col + 1):
                    self._potentials.makeTrue(1, col + 1)
                if not self._attempts.isTrue(1, col - 1):
                    self._potentials.makeTrue(1, col - 1)
                if not self._attempts.isTrue(2, col):
                    self._potentials.makeTrue(2, col)
            elif col == 10:
                if not self._attempts.isTrue(1, 9):
                    self._potentials.makeTrue(1, 9)
                if not self._attempts.isTrue(2, 10):
                    self._potentials.makeTrue(2, 10)
        elif row <= 9 and row >= 2:
            if col == 1:
                if not self._attempts.isTrue(row + 1, 1):
                    self._potentials.makeTrue(row + 1, 1)
                if not self._attempts.isTrue(row - 1, 1):
                    self._potentials.makeTrue(row - 1, 1)
                if not self._attempts.isTrue(row, 2):
                    self._potentials.makeTrue(row, 2)
            elif col <= 9 and col >= 2:
                if not self._attempts.isTrue(row + 1, col):
                    self._potentials.makeTrue(row + 1, col)
                if not self._attempts.isTrue(row - 1, col):
                    self._potentials.makeTrue(row - 1, col)
                if not self._attempts.isTrue(row, col + 1):
                    self._potentials.makeTrue(row, col + 1)
                if not self._attempts.isTrue(row, col - 1):
                    self._potentials.makeTrue(row, col - 1)
            elif col == 10:
                if not self._attempts.isTrue(row + 1, 10):
                    self._potentials.makeTrue(row + 1, 10)
                if not self._attempts.isTrue(row - 1, 10):
                    self._potentials.makeTrue(row - 1, 10)
                if not self._attempts.isTrue(row, 9):
                    self._potentials.makeTrue(row, 9)
        elif row == 10:
            if col == 1:
                if not self._attempts.isTrue(9, 1):
                    self._potentials.makeTrue(9, 1)
                if not self._attempts.isTrue(10, 2):
                    self._potentials.makeTrue(10, 2)
            elif col <= 9 and col >= 2:
                if not self._attempts.isTrue(9, col):
                    self._potentials.makeTrue(9, col)
                if not self._attempts.isTrue(10, col + 1):
                    self._potentials.makeTrue(10, col + 1)
                if not self._attempts.isTrue(10, col - 1):
                    self._potentials.makeTrue(10, col - 1)
            elif col == 10:
                if not self._attempts.isTrue(10, 9):
                    self._potentials.makeTrue(10, 9)
                if not self._attempts.isTrue(9, 10):
                    self._potentials.makeTrue(9, 10)

    def sendAttack(self, inputString):
        """
        :param inputString: this text is received from the textbox that is displayed on the screen. Called when return is hit
        and whatever string is written in the text box will be passed into this function.
        :return: Breaks down the string into smaller string using "," and validates the input. If a hit is made, then a red
        dot will be displayed on the guess board. If not, then a missed sprite will be placed at that position. After placing a
        sprite, the sendComputerAttackFunction will be called.
        """
        inputList = inputString.split(",")
        if inputList[0].isalpha():
            if ord(inputList[0].upper()) > 75:      # Validate that the correct letter is received
                return False
            else:
                rowVal = self.letterSwitch(inputList[0].upper())      # Get the corresponding rowVal
        if inputList[1].isdigit():
            colVal = int(inputList[1])
        else:
            return False
        if rowVal > 10 or colVal > 10:
            return False
        if self._playerAttempts.isTrue(rowVal, colVal):
            return False
        self._playerAttempts.makeTrue(rowVal, colVal)
        if self._computer.isTrue(rowVal, colVal):           # Test if a hit is made
            self.add(Attack(479 + (34 * colVal), 46 + (34 * rowVal)))   # Places a red dot onto the hit ship unit
            self._computerCount -= 1        # Decrease the shipCount of the computer
        else:               # if missed
            self.add(Missed(479 + (34 * colVal), 46 + (34 * rowVal)))       # Place a missed unit onto the guessed spot
        self.sendComputerAttack()              # Everytime a user sets a shot, the computer will send one as well.

    def sendComputerAttack(self):
        """
        Called only when the user has sent a valid shot. If the potentials array is all false, the computer will guess
        randomly from the available positions. Whenever a hit is made, the proper surrounding cells are changed in the
        potentials array. Whenever there are true values in the potentials array, the computer will play in hunt mode, and
        search nearby cells until it sinks the ship.
        :return: Sends either a random or intelligent shot from the computer.
        """
        if self._potentials.isAllFalse():       # If potentials array is all false, play randomly
            rowVal = random.randint(1, 10)          # generate random values
            colVal = random.randint(1, 10)
            while self._attempts.isTrue(rowVal, colVal):        # Get values that haven't already been guessed.
                rowVal = random.randint(1, 10)
                colVal = random.randint(1, 10)
            self._attempts.makeTrue(rowVal, colVal)     # Add to array of already guessed
            if self._user.isTrue(rowVal, colVal):       # If a hit is made
                self.add(Attack(48 + (34 * colVal), 46 + (34 * rowVal)))           # Display a hit unit
                self._playerCount -= 1      # Decrease the player ship count
                self.changePotentials(rowVal, colVal)      # Change the proper cells in the potentials array
            else:
                self.add(Missed(48 + (34 * colVal), 46 + (34 * rowVal)))        # Missed. Display missed unit.
        else:
            rowVal = random.randint(1, 10)          # Playing intelligently
            colVal = random.randint(1, 10)
            while not self._potentials.isTrue(rowVal, colVal):      # Get random values that are true in the potentials array
                rowVal = random.randint(1, 10)
                colVal = random.randint(1, 10)
            self._attempts.makeTrue(rowVal, colVal)     # Add to array of already guessed
            self._potentials.makeFalse(rowVal, colVal)      # Remove from array of potentials.
            if self._user.isTrue(rowVal, colVal):       # If a hit is made,
                self.add(Attack(48 + (34 * colVal), 46 + (34 * rowVal)))        # Display the hit unit
                self._playerCount -= 1          # Decrease the player unit
                self.changePotentials(rowVal, colVal)      # Change the proper cells in the potentials array
            else:
                self.add(Missed(48 + (34 * colVal), 46 + (34 * rowVal)))    # Missed. Display missed unit.

    def displayBoards(self):
        """
        Called only when the game starts. Displays the player board and the guess board.
        """
        player_board = Board(50, 400)
        guess_board = Board(480,400)
        gameBoards = pygame.sprite.Group()
        gameBoards.add(player_board)
        gameBoards.add(guess_board)
        self.add(gameBoards)

    def displayGameover(self, result: str):
        """
        Called only when one of the shipCounts is set to zero
        :param result:  The result string to the displayed to the string
        :return: Renders the text to be displayed onto the game over screen and sets both ship counts to None.
        """
        self._allSprites.empty()        # Clear the screen
        self._playerCount = None
        self._computerCount = None
        self._active = False            # Remove the input text box functionality
        self._color = (0, 25, 87)           # Make the input text box transparent
        self._gameOverMessage = self._font.render("Game Over", True, (189, 205, 206))       # Render the game over texts
        self._resultString = self._font.render(result, True, (189, 205, 206))
        self._endGameMessage = self._font.render("Press the escape key to close the window", True, (189, 205, 206))

    def run(self):
        """
        Called every loop of the game. This is the game loop
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:        # Quit the game whenever the escape is called at any time.
                        pygame.quit()
                        sys.exit()
                    if self._active:    # active is only true if the user has clicked on the textbox
                        if event.key == pygame.K_RETURN:    # Sends text to sendAttack function when enter is pressed
                            self.sendAttack(self._text)
                            self._text = ""     # Clear the text box
                        elif event.key == pygame.K_BACKSPACE:
                            self._text = self._text[:-1]        # Delete a character from the text box
                        else:
                            self._text += event.unicode     # If a letter is pressed while in active mode, it will be added
                elif event.type == pygame.QUIT:     # If the close button is pressed, close the game.
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:      # If the game is not over, a click on the text box will allow for
                    if not self._gameOver:                      # text to be typed into it.
                        if self._inputBox.collidepoint(event.pos):
                            self._active = not self._active
                        else:
                            self._active = False            # Toggles the color of the textbox when in active mode.
                        self._color = self._colorActive if self._active else self._colorInactive

            if self.getTicks() == 0:        # When the game starts, initialize the player and computer virtual grids
                self.displayBoards()       # and display the players ships to the screen.
                for i in range(5):      # Passes data from the JSON file to the fleet initialization functions
                    self.initFleet(self._data['playerShips'][i]['letterPos'], self._data['playerShips'][i]['numberPos'],
                                   self._data['playerShips'][i]['shipName'], self._data['playerShips'][i]['orientation'])
                    self.initEnemyFleet(self._data['enemyShips'][i]['letterPos'], self._data['enemyShips'][i]['numberPos'],
                                        self._data['enemyShips'][i]['shipName'], self._data['enemyShips'][i]['orientation'])

            if self._playerCount == 0 or self._computerCount == 0:      # If all of a players ships are sunk, game over
                self._gameOver = True
                if self._playerCount == 0:
                    self.displayGameover("The computer has won :(")        # Text to be displayed in game over screen.
                else:
                    self.displayGameover("!!! You have won !!!")


            self.update()
            self._screen.fill((0, 25, 87))      # Background color of game
            if self._gameOver:          # The game over text will only show when one of the scores is set to 0
                self._screen.blit(self._gameOverMessage, (370, 100))
                self._screen.blit(self._resultString, (330, 200))
                self._screen.blit(self._endGameMessage, (270, 300))
            self._textSurface = self._font.render(self._text, True, self._color)        # Show text and textbox on screen.
            width = max(400, self._textSurface.get_width() + 10)
            self._inputBox.w = width
            self._screen.blit(self._textSurface, (self._inputBox.x + 5, self._inputBox.y + 5))  # Show text box on screen
            pygame.draw.rect(self._screen, self._color, self._inputBox, 2)
            self.draw()         # Draw game to screen.
            pygame.display.update()
            self._clock.tick(60)
            self._ticks += 1


def main():
    """
    Creates and runs a battleship game.
    """
    game = Battleship()
    game.run()


main()
