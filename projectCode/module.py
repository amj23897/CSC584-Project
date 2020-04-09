import random
import time
from algorithm import *

class World():
    """
    Class for handling the map 
    functions and variables
    """
    def __init__(self, worldJson):
        """
        Initializes all the variables
        that are part of the class Map
        """
        self.world_json = worldJson
        
    def get_canvas_size(self):
        """
        Function that returns the size of canvas from Json
        return: array having width and height
        """
        return world_json["canvas_size"]
    
    def set_background_color(self):
        """
        Sets the background color
        """
        background(self.world_json["canvas_color"])
        
    def draw_all_obstacles(self):
        """
        Function that creates all the obstacles on
        the map
        """
        obstaclesJson = self.world_json["obstacles"]
        for obstacle in obstaclesJson.keys():
            tempObstacleJson = obstaclesJson[obstacle]
            self.draw_obstacle_utility(tempObstacleJson, obstacle)
        
    def draw_obstacle_utility(self, locationList, obstacle):
        """
        Function that creates the obstacle on
        the map
        loationList: dictionary of all the locations
                     where the obstacles are to be drawn
        obstacle: name of the obstacle that is being drawn
        """
        totalVertices = len(locationList)
        fill(0)
        stroke(0)
        strokeWeight(2)
        beginShape()
        for i in range(0,totalVertices):
            location = locationList[i]
            vertex(location[0],location[1])
        endShape(CLOSE)
        
    def draw_bot(self):
        """
        Function draws the bot on the map
        """
        circle(self.world_json["bot_start"][0], self.world_json["bot_start"][1], 10)
        
    def draw_player(self):
        """
        Function draws the bot on the map
        """
        circle(self.world_json["player_start"][0], self.world_json["player_start"][1], 10)
    
class Player():
    """
    Class to account location for the player
    """
    def __init__(self, start_location):
        """
        Function that initializes the class with
        given start location
        last_location: list containing location
        current_location: list containing location
        """
        self.last_location = None
        self.current_location = start_location
        self.speed = 2
        self.img = loadShape('images/player.svg')
        self.img.scale(0.07)
    
    def update_current_location(self, new_location):
        """
        Function that updates the new_location and also
        stores the previous one for reference
        """
        self.last_location = self.current_location
        self.current_location = new_location

    def draw_player_old(self):
        """
        Function that draws the player object at new location
        and removes the old player object from previous location
        """
        stroke(255)
        if self.last_location:
            fill(255)
            circle(self.last_location[0], self.last_location[1], 10)
        fill(0)
        circle(self.current_location[0], self.current_location[1], 10)
        
    def draw_player(self):
        shape(self.img, self.current_location[0]-25, self.current_location[1]-25)

class Bot():
    """
    Class to account location for the all
    the bot locations
    """
    def __init__(self, start_location):
        """
        Function that initializes the class with
        given start locations
        last_location : list containing locations
        current_location: list containing locations
        """
        self.last_location = None
        self.current_location = start_location
        self.path_traversing = None
        self.path_index = None
        self.is_moving = False
        self.destination = None
        self.speed = 2
        self.img = loadShape('images/guard1.svg')
        self.img.scale(0.07)
        self.current_state = None
        self.last_state_update_time = 0
        
    def update_location(self, new_location):
        """
        Function that updates the new_location and also
        stores the previous one for reference for all
        the bots
        """
        self.last_location = self.current_location
        self.current_location = new_location

    def move_bot(self):
        if self.path_traversing and self.path_index < self.max_path_index:
            self.update_location(list(self.path_traversing[self.path_index]))
            self.path_index += self.speed
        else:
            self.is_moving = False

    def draw_bot_old(self):
        """
        Function that draws all the bot objects at new
        location and removes all the old bot objects from
        previous location
        """
        stroke(255)
        if self.last_location:
            fill(255)
            circle(self.last_location[0], self.last_location[1], 10)
        fill(100)
        circle(self.current_location[0], self.current_location[1], 10)
    
    def draw_bot(self):
        shape(self.img, self.current_location[0]-25, self.current_location[1]-25)
        
class BotMovement():
    """
    Class to make sure all the bots are in moving state
    """
    def __init__(self, bot_objects, count):
        """
        Initializes class with all the bot objects
        and bots count
        """
        self.bots = bot_objects
        self.bot_count = count
        self.available_state = {
            'wander': {
                'probability': 0,
            }, 
            'guard': {
                'probability': 0,
            }, 
            'chase': {
                'probability': 0,
            }
        }
        print(width, height)
        self.pathFinderObject = pathFinder(width, height)
        self.treasureStolen = False
    
    def find_bot_path(self, bot_object):
        """
        Function to move the bot
        """
        start_location = tuple(bot_object.current_location)
        goal_location = tuple(bot_object.destination)
        #path = self.pathFinderObject.pathFindRecursiveBestFirstSearch(start_location, goal_location)
        path = self.pathFinderObject.pathFindAstar(start_location, goal_location)
        if not path:
            print("inaccessible")
            return
        bot_object.path_traversing = path
        bot_object.path_index = 0
        bot_object.max_path_index = len(path)
        bot_object.is_moving = True

    def update_probabilities(self):
        """
        Update moving actions' probability based on current state of the game
        """
        if self.treasureStolen:
            self.available_state['wander']['probability'] = 0
            self.available_state['guard']['probability'] = 0
            self.available_state['chase']['probability'] = 1
        else:
            self.available_state['wander']['probability'] = 0.10
            self.available_state['guard']['probability'] = 0.90
            self.available_state['chase']['probability'] = 0
        return

    def decide_bot_state(self, bot, delay):
        """
        Function runs a decision making algorithm to find the current state of the given bot
        if difference between current time and last_state_update_time is greater than given delay
        """
        if time.time()-bot.last_state_update_time < delay:
            return
        prand = random.random()
        pdiff = float('inf')
        closest_state = None
        sum = 0
        for state in self.available_state.keys():
            sum += self.available_state[state]['probability']
            if prand <= sum:
                closest_state = state
                break
        bot.current_state = closest_state
        bot.last_state_update_time = time.time()
        return

    def move_bots(self):
        """
        Function that moves all the bots across the canvas
        """
        self.update_probabilities()
        for i, bot in enumerate(self.bots):
            self.decide_bot_state(bot, 5) # random.randrange(3,5)
            if bot.current_state == 'wander':
                if bot.is_moving:
                    bot.move_bot()
                    bot.draw_bot()
                else:
                    print("wander state")
                    bot.destination = [random.randrange(0,640), random.randrange(0, 480)]
                    # print bot.destination
                    self.find_bot_path(bot)
            elif bot.current_state == 'guard':
                """
                to make all the bots guard the treasure
                """
                if bot.is_moving:
                    bot.move_bot()
                    bot.draw_bot()
                else:
                    print("guard state")
                    # treasure_corners = [[100,100], [200,200]]
                    # bot.destination = random.choice(treasure_corners)
                    # print("curr ", bot.current_location)
                    treasure_corners = [[640-150, 480], [640-150, 480-150], [640, 480-150], [640, 480]]
                    if(i%2):
                        treasure_corners.reverse()
                    # find nearest corner
                    x=bot.current_location[0]
                    y=bot.current_location[1]
                    nearest_corner = None
                    dist_min=float('inf')
                    for corner in treasure_corners:
                        eu_dist=(corner[0]-x)*(corner[0]-x)+(corner[1]-y)*(corner[1]-y)
                        if(eu_dist < dist_min):
                            dist_min = eu_dist
                            nearest_corner = corner
                    bot.destination = treasure_corners[(treasure_corners.index(nearest_corner)+1)%4]
                    # print bot.destination
                    self.find_bot_path(bot)
                
                pass
            elif bot.current_state == 'chase':
                """
                to make all the bots chase the player bot
                once in the vicinity/range
                """
                print("chase state")
                pass
