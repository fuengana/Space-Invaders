"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the
Alien Invaders game.  Instances of Wave represent a single wave.  Whenever you
move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a
complicated issue.  If you do not know, ask on Piazza and we will answer.

Names: Adele Kong (ak2333) and Nahbuma Gana (nfg23)
Date: 07 May 2019
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary. It
    also marches the aliens back and forth across the screen until they are all
    destroyed or they reach the defense line (at which point the player loses).
    When the wave is complete, you should create a NEW instance of Wave (in
    Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update. See subcontrollers.py from Lecture 24 for an example. This class
    will be similar to than one in how it interacts with the main class
    Invaders.

    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien
                 or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly
                 empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden. You may find that you
    want to access an attribute in class Invaders. It is okay if you do, but you
    MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter
    for any attribute that you need to access in Invaders.  Only add the getters
    and setters that you need for Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may
    want to keep track of the score.  You also might want some label objects to
    display the score and number of lives. If you make changes, please list the
    changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
        left_side:   Position of the left-most alien [int or float]
        right_side:  Position of the right-most alien [int or float]
        bottom:      Position of the bottom-most alien [int or float]
        move_right:  True if aliens are moving right, False otherwise [bool]
        move_down:   True if aliens are moving down, False otherwise [bool]
        shoot_steps: Number of steps aliens take before shooting [int]
        time_shot:   The amount of time since the last Alien shot [int or float]
        speed:       The speed that the aliens move at [int or float]
    """
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def setAliens(self):
        """
        Intializes a new ship and sets to attributes. Ship starts in the middle
        below the dline
        """
        new_alien_images = []
        for image in ALIEN_IMAGES:
            new_alien_images.append(image)
            new_alien_images.append(image)
        wave = []
        y = GAME_HEIGHT - (ALIEN_CEILING + ALIEN_V_SEP * ALIEN_ROWS +
            ALIEN_HEIGHT * (ALIEN_ROWS - 0.5))
        k1 = 0
        while k1 < ALIEN_ROWS:
            x = ALIEN_H_SEP + ALIEN_WIDTH / 2
            row = []
            k2 = 0
            while k2 < ALIENS_IN_ROW:
                new_k = k1
                if k1 > (len(ALIEN_IMAGES) * 2) - 1:
                    new_k = k1 % (len(ALIEN_IMAGES) * 2)
                alien_image = new_alien_images[new_k]
                alien = Alien(x, y, ALIEN_WIDTH, ALIEN_HEIGHT, alien_image)
                row.append(alien)
                x += ALIEN_WIDTH + ALIEN_H_SEP
                k2 += 1
            wave.append(row)
            y += ALIEN_HEIGHT + ALIEN_V_SEP
            k1 += 1
        self._aliens = wave


    def setShip(self):
        """
        Intializes a new ship and sets to attributes. Ship starts in the middle
        below the dline
        """
        self._ship = Ship(GAME_WIDTH / 2, SHIP_BOTTOM, SHIP_WIDTH, SHIP_HEIGHT,
                     "ship.png")


    def setDLine(self):
        """
        Initializes Dline to be drawn above the ship and below the aliens.
        """
        self._dline = GPath(points = [ALIEN_H_SEP, DEFENSE_LINE, GAME_WIDTH -
                      ALIEN_H_SEP, DEFENSE_LINE])

    def setSpeed(self):
        """
        Sets the speed of wave based on the initial Speed
        """
        self.speed = self.initial_speed


    def getInitialSpeed(self):
        """
        Initializes intial speed of the wave during the first wave
        """
        return self.initial_speed


    def getLives(self):
        """
        Returns attribute lives
        """
        return self._lives


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        Initializer for wave objects
        """
        self.setAliens()
        self.setShip()
        self.setDLine()
        self._lives = SHIP_LIVES
        self._time = 0
        self.left_side = ALIEN_H_SEP
        self.right_side = ALIEN_H_SEP * ALIENS_IN_ROW + (ALIEN_WIDTH *
                          ALIENS_IN_ROW)
        self.bottom = GAME_HEIGHT - ALIEN_CEILING - ALIEN_ROWS * (ALIEN_HEIGHT +
                      ALIEN_V_SEP - 1)
        self.move_right = True
        self.move_down = False
        self._bolts = []
        self.shoot_steps = random.randint(1, BOLT_RATE)
        self.time_shot = 0
        self.initial_speed = ALIEN_SPEED
        self.speed = self.initial_speed


    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, input, dt):
        """
        Creates the animation to move the ship, aliens and laser bolts

        Parameter input: the users input to control the ship,
        fire bolts and change the game state.
        Precondition: Must be an isntance of Ginput

        Parameter dt: the time passed since the last animation frame in seconds
        Precondition: Must be a float
        """
        assert isinstance(input, GInput)
        assert type(dt) == float or int
        if self._ship != None:
            self.move_ship(input)
        self.move_aliens(dt)
        self.move_Player_bolts(input)
        self.move_Alien_bolts(dt)
        self.collision()


    # UPDATE HELPERS
    def move_ship(self, input):
        """
        Moves the ship left or right across the game screen

        Parameter input: the users input to control the ship by moving it
        either left or right.
        Precondition: Must be an isntance of Ginput
        """
        assert isinstance(input, GInput)
        if input.is_key_down('right') == True and self._ship.x <= (GAME_WIDTH -
                ALIEN_H_SEP - SHIP_WIDTH / 2):
            self._ship.x += SHIP_MOVEMENT
        if input.is_key_down('left') == True and self._ship.x >= (ALIEN_H_SEP +
                SHIP_WIDTH / 2):
            self._ship.x -= SHIP_MOVEMENT


    def alien_columns(self):
        """
        Returns: list of aliens within the columns
        """
        alien_columns = []
        for i1 in range(ALIENS_IN_ROW):
            alien_columns.append([])
            for i2 in range(ALIEN_ROWS):
                alien_columns[i1].append(self._aliens[i2][i1])
        return alien_columns


    def update_left_side(self):
        """
        Returns: x-coordinate of left-most alien
        """
        for column in self.alien_columns():
            for alien in column:
                if alien == None:
                    pass
                elif alien != None:
                    return alien.x - ALIEN_WIDTH / 2


    def update_right_side(self):
        """
        Returns: x-coordinate of right-most alien
        """
        for i in range(len(self.alien_columns())):
            for alien in self.alien_columns()[len(self.alien_columns()) - 1 -
                    i]:
                if alien == None:
                    pass
                elif alien != None:
                    return alien.x + ALIEN_WIDTH / 2


    def update_bottom(self):
        """
        Returns: y-coordinate of bottom-most alien
        """
        for row in self._aliens:
            for alien in row:
                if alien == None:
                    pass
                elif alien != None:
                    return alien.y - ALIEN_HEIGHT / 2


    def move_aliens(self, dt):
        """
        Moves aliens across the screen and back

        Paramater dt: time passed since the last animation frame in seconds
        Precondition: Must be a float
        """
        assert type(dt) == float or int
        if self._time > self.speed:
            self._time = 0
            if self.move_down == False:
                for row in self._aliens:
                    for alien in row:
                        if alien != None:
                            if self.move_right == True:
                                alien.x += ALIEN_H_WALK
                            else:
                                alien.x -= ALIEN_H_WALK
                            self.left_side = self.update_left_side()
                            self.right_side = self.update_right_side()
                if (self.right_side >= GAME_WIDTH - ALIEN_H_SEP or
                        self.left_side <= ALIEN_H_SEP):
                    self.move_down = True
            else:
                for row in self._aliens:
                    for alien in row:
                        if alien != None:
                            alien.y -= ALIEN_V_WALK
                if self.right_side >= GAME_WIDTH - ALIEN_H_SEP:
                    self.move_right = False
                elif self.left_side <= ALIEN_H_SEP:
                    self.move_right = True
                self.move_down = False
        else:
            self._time += dt


    def move_Player_bolts(self, input):
        """
        Fires bolt from the ship above the dline to the aliens

        Parameter input: the users input to fire the bolt by pressing the
        spacebar
        Precondition: Must be an instance of Ginput
        """
        assert isinstance(input, GInput)
        if input.is_key_down('spacebar') == True and (len(self._bolts) == 0 or
            self._bolts[0].isPlayerBolt() == False) and self._ship != None:
            bolt = Bolt(self._ship.x, (self._ship.y + self._ship.height / 2 +
                BOLT_HEIGHT / 2), BOLT_WIDTH, BOLT_HEIGHT, 'white', BOLT_SPEED)
            self._bolts.insert(0, bolt)
        if len(self._bolts) != 0 and self._bolts[0].isPlayerBolt() == True:
            self._bolts[0].y += self._bolts[0].getVelocity()
        if len(self._bolts) != 0 and (self._bolts[0].isPlayerBolt() == True and
            self._bolts[0].y >= GAME_HEIGHT + BOLT_HEIGHT / 2):
            self._bolts.pop(0)


    def move_Alien_bolts(self, dt):
        """
        Fires alien bolts downwards below the dline.

        Parameter dt: time passed since the last animation frame in seconds
        Precondition: Must be a float
        """
        assert type(dt) == float or int
        if self.time_shot >= self.shoot_steps * self.speed:
            shooting_alien = None
            while shooting_alien == None:
                shooting_alien = self._aliens[random.randint(0, ALIEN_ROWS -
                    1)][random.randint(0, ALIENS_IN_ROW - 1)]
            bolt = Bolt(shooting_alien.x, (shooting_alien.y - ALIEN_HEIGHT / 2 -
                BOLT_HEIGHT / 2), BOLT_WIDTH, BOLT_HEIGHT, 'red', -BOLT_SPEED)
            self._bolts.append(bolt)
            self.time_shot = 0
        else:
            self.time_shot += dt
        if self.time_shot == 0:
            self.shoot_steps = random.randint(1, BOLT_RATE)
        for bolt in self._bolts:
            if bolt.isPlayerBolt() == True:
                pass
            else:
                if bolt.y <= 0:
                    self._bolts.remove(bolt)
                else:
                    bolt.y += bolt.getVelocity()


    def collision(self):
        """
        Detects collision between bolt and ship and removes lives from the
        player if a bolt hits the ship.
        """
        for bolt in self._bolts:
            for i1 in range(len(self._aliens)):
                for i2 in range(len(self._aliens[i1])):
                    if (self._aliens[i1][i2] != None and
                            self._aliens[i1][i2].collides(bolt)):
                        self._aliens[i1][i2] = None
                        self._bolts.remove(bolt)
                        self.speed *= 0.98
            if self._ship != None and self._ship.collides(bolt):
                self._ship = None
                if self._bolts[0].isPlayerBolt():
                    self._bolts.remove(self._bolts[0])
                self._bolts.remove(bolt)
                self._lives -= 1


    def game_over(self):
        """
        Returns: either a 0, 1, or 2 depending on if the aliens are shot or if
        the ship is shot.
        """
        aliens_shot = 0
        for row in self._aliens:
            for alien in row:
                if alien == None:
                    aliens_shot += 1
        if aliens_shot == ALIENS_IN_ROW * ALIEN_ROWS:
            return 0
        if self._lives == 0 or self.bottom <= DEFENSE_LINE:
            return 1
        elif self._ship == None:
            return 2


    def next_speed(self, new_speed):
        """
        Increments the initial speed exponentially by raising .9 to the n power

        Parameter n: an exponent used to incremaent the speed
        Precondition: n is an int or float
        """
        self.initial_speed = new_speed


    def lives(self, lives):
        """
        Takes argument for lives and makes an attribute of waves class.
        """
        self._lives = lives


    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the ship, aliens, dline, and bolts
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.draw(view)
        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)


    # HELPER METHODS FOR COLLISION DETECTION
