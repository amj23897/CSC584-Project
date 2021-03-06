import json
import math

class Map:
    def __init__(self, jsonData):
        self.data = jsonData
        self.playerPosition = None
        self.guard1Position = None
        self.guard2Position = None
        self.obstacles = []
        self.safehousePosition = None
        self.treasurePosition = None   
        self.dead1Position = None
        self.dead2Position = None
        self.dead3Position = None
        self.dead4Position = None
        self.normal1Position = None
        self.normal2Position = None
        self.fire_i = 0
        self.loadData()
        self.treasureStolen = False
        
    def loadImages(self): #called in loadData()
        self.fireImages = [loadImage('images/fire/fire0.gif'), loadImage('images/fire/fire1.gif'), loadImage('images/fire/fire2.gif'),loadImage('images/fire/fire3.gif')]
        for i in range(len(self.fireImages)):
            self.fireImages[i].resize(160, 160) 
            
        self.normal1 = loadImage('images/corona.png')
        self.normal1.resize(30,30)
        self.normal2 = loadImage('images/corona.png')
        self.normal2.resize(30,30)
        self.safehouseImg = loadImage('images/safehouse.png')
        self.safehouseImg.resize(100,100)
        
        self.treasureImg = loadImage('images/treasure.png')
        self.treasureImg.resize(100,100)
        
        self.player_stealImg = loadShape('images/player_steal.svg')
        self.player_stealImg.scale(0.07)
                
    def loadData(self):    
        # self.playerPosition = tuple(self.data['player_start'])
        # self.guard1Position = tuple(self.data['guard1'])
        # self.guard2Position = tuple(self.data['guard2'])
        
        self.obstacles = self.data['obstacles'].values()
        
        #key locations
        self.safehousePosition = tuple(self.data['key_locations']['safe_house'])
        self.treasurePosition = tuple(self.data['key_locations']['treasure'])
        self.dead1Position = tuple(self.data['key_locations']['dead1'])
        self.dead2Position = tuple(self.data['key_locations']['dead2'])
        self.dead3Position = tuple(self.data['key_locations']['dead3'])
        self.dead4Position = tuple(self.data['key_locations']['dead4'])
        
        self.normal1Position = tuple(self.data['key_locations']['normal1'])
        self.normal2Position = tuple(self.data['key_locations']['normal2'])
        
        self.loadImages()
        
            
    def drawStaticObstacles(self):
        for obstacle in self.obstacles:
            beginShape()
            for x, y in obstacle:
                vertex(x, y)
            endShape(CLOSE)
    
    def drawStaticKeys(self):    
        fill(100)
        image(self.safehouseImg, self.safehousePosition[0]-50, self.safehousePosition[1]-50, self.safehouseImg.height/2, self.safehouseImg.width/2)
        image(self.treasureImg, self.treasurePosition[0]-25, self.treasurePosition[1]-25, self.treasureImg.height/2, self.treasureImg.width/2)
        
        image(self.normal1, self.normal1Position[0], self.normal1Position[1])
        image(self.normal2, self.normal2Position[0], self.normal2Position[1])
        pass
    
    def drawDynamicObstacles(self):
        self.fire_i = (self.fire_i + 1)%40
        fire = self.fireImages[self.fire_i//10]
        image(fire, self.dead1Position[0]-20, self.dead1Position[1]-20, fire.height/4, fire.width/4)
        image(fire, self.dead2Position[0]-20, self.dead2Position[1]-20, fire.height/4, fire.width/4)
        image(fire, self.dead3Position[0]-20, self.dead3Position[1]-20, fire.height/4, fire.width/4)
        image(fire, self.dead4Position[0]-20, self.dead4Position[1]-20, fire.height/4, fire.width/4)
        
    def drawMap(self):
        self.drawStaticObstacles()
        self.drawStaticKeys()
        self.drawDynamicObstacles()
    
    def checkTreasureStolen(self, player_loc, dist_threshold=50):
        """
        Checks if player is currently near the treasure
        default distance threshold is 50 pixels.
        use third for custom threshold
        """
        if(self.treasureStolen):
            return True
        else:
            if(self.collision_detection(player_loc, self.treasurePosition, dist_threshold)):
                self.treasureStolen=True
                return True
            else:
                return False
    
    def collision_detection(self, obj1, obj2, thresh=50):
        """
        uses euclidean distance.
        default distance threshold is 50 pixels.
        pass third argument for custom threshold.
        """
        sqDist = (obj1[0]-obj2[0])*(obj1[0]-obj2[0]) + (obj1[1]-obj2[1])*(obj1[1]-obj2[1])
        dist = math.sqrt(sqDist)
        if(dist <= thresh):
            return True
        else:
            return False
    
    def playerCollisionOccur(self, player_loc, bots):
        """
        pass current player's location and list of bot objects
        """
        obstacles=[]
        for obj in self.data['key_locations']:
            if("dead" in obj):
                obstacles.append(self.data['key_locations'][obj])
        for obstacle in obstacles:
            if(self.collision_detection(player_loc, obstacle, 30)):
                return True
        # print("No collision with obstacles")
        for bot in bots:
            if(self.collision_detection(player_loc, bot.current_location, 40)):
                return True
        # print("No collision with bots")
        return False
    
    def playerBackHome(self, player_loc):
        """
        pass current player's location to check if he reached back home
        """
        return self.collision_detection(player_loc, self.safehousePosition, 50)
    
    def playerCollisionWithPower(self, player_obj, power_obj, bots):
        distance = 40
        if power_obj.isPowerUp_active and self.collision_detection(player_obj.player_center(), power_obj.powerUp_location, distance):
            print("Power Up Gained!  PLAYER SPEED INCREASED")
            player_obj.speed+=2 # increase player's speed
            power_obj.isPowerUp_active = False # deactivate power-up so that it is not drawn
            return True
        
        if power_obj.isPowerDown_active and self.collision_detection(player_obj.player_center(), power_obj.powerDown_location, distance):
            print("Power Up Gained!  GUARDS SPEED DECREASED")
            for bot in bots:
                bot.speed-=1 # decrease bot's speed
            power_obj.isPowerDown_active = False # deactivate power-up so that it is not drawn
            return True
        
        if power_obj.isImmunity_active and self.collision_detection(player_obj.player_center(), power_obj.immunity_location, distance):
            # take steps to apply immunity power
            print("Power Up Gained!  PLAYER IMMUNE TO OBSTACLES")
            player_obj.immunity = True
            power_obj.isImmunity_active = False # deactivate power-up so that it is not drawn
            return True
        return False
    
    
