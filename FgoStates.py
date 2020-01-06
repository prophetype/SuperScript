from State import *
import numpy as np
from Controller import Controller
import Driver


class FgoStartState(ImageCheckClick):
    def __init__(self, parent=None, check_while_work_areas = None, check_imgs=None, check_areas=None, work_areas=None, times=None):
        super().__init__(parent=parent, check_imgs=check_imgs, check_areas=check_areas, work_areas=work_areas, times=times)
        self.check_while_work_areas = check_while_work_areas
    
    def check_state(self):
        if super().check_state():
            return True
        else:
            if not State.scanning:
                self.controller.click_area(self.check_while_work_areas, 0.75)
            return False


class FgoBattleState(TextCheckState):

    SKILL_AREAS = []
    BATTLE_AREAS = []

    TEXT_CHECK_AREAS = []
    IMAGE_CHECK = []
    IMAGE_CHECK_AREAS = []

    def __init__(self, parent = None, 
                       check_texts = [], 
                       skills = [], 
                       times = None):

        super().__init__(parent=parent, check_texts = check_texts, check_areas = FgoBattleState.TEXT_CHECK_AREAS)
        #skills = 1~9  10,11,12,13
        self.skills = [FgoBattleState.SKILL_AREAS[i - 1] for i in skills]
        self.skill_state = True
        if times == None or len(times) != len(skills):
            self.times = [2.5] * len(skills)
        
        self.config = "--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789//"
        
    
    def reset(self):
        self.skill_state = True
        super().reset()
    
    def check_state(self):
        
        if State.controller.check_images(self.IMAGE_CHECK_AREAS, self.IMAGE_CHECK) and super().check_state():
            return True
        else:
            return False


    def work(self):
        
        if self.skill_state:
            State.controller.click_areas(self.skills, self.times)
            self.skill_state = False

        State.controller.click_area(FgoBattleState.BATTLE_AREAS, 2)
    
    @classmethod
    def set_skill_areas(cls, areas):
        cls.SKILL_AREAS = areas
    
    @classmethod
    def set_battle_areas(cls, areas):
        cls.BATTLE_AREAS = areas
    
    @classmethod
    def set_text_check_areas(cls, areas):
        cls.TEXT_CHECK_AREAS = areas
    
    @classmethod
    def set_battle_check_areas(cls, areas):
        cls.IMAGE_CHECK_AREAS = areas
    
    @classmethod
    def set_battle_image(cls, imgs):
        cls.IMAGE_CHECK = [State.controller.imread(imgs)]


class FgoCardState(State):
    
    CARD_AREAS = []
    CHECK_AREAS = []
    COLOR_IMAGES = []
    
    def __init__(self, parent = None, 
                      card_seq = [0, 1, 2], 
                      ulti = [1,2,3]):
        super().__init__(parent=parent)

        self.card_seq = card_seq
        self.ulti = ulti

        self.colors = [None] * 5
        self.times = [0.7] * 6
    
    def reset(self):
        return True
    
    def check_state(self):
        
        colors = State.controller.check_from_images(self.CHECK_AREAS, self.COLOR_IMAGES)
        print("get colors:", colors)
        if None not in colors and len(colors) == 5:
            self.colors = colors
            print("return True")
            return True
        else:
            return False
    

    def work(self):
        selected = []
        
        for i in self.ulti:
            selected.append(self.CARD_AREAS[i+4])

        for color in self.card_seq:
            for i in range(5):
                if color == self.colors[i]:
                    selected.append(self.CARD_AREAS[i])

        State.controller.click_areas(selected[0:6], self.times)
    
    @classmethod
    def set_cards_areas(cls, areas):
        cls.CARD_AREAS = areas
    
    @classmethod
    def set_check_areas(cls, areas):
        cls.CHECK_AREAS = areas
    
    @classmethod
    def set_color_imgs(cls, colors):
        cls.COLOR_IMAGES = [Controller.imread(img) for img in colors]

class TransformState(State):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.text_transform = []
        self.check_transform = []
        self.next_state = None
    
    def add_text_transform(self, states = []):
        self.text_transform = self.text_transform + states
    
    def add_check_transoform(self, states = []):
        self.check_transform += states
    
    def check_state(self):

        for i in range(1000):
            img = self.controller.get_screen()
        
            if State.controller.check_images(self.text_transform[0].IMAGE_CHECK_AREAS, 
                                         self.text_transform[0].IMAGE_CHECK,
                                         img, True):

                while True:
                    imgs = self.controller.extract_img(img, self.text_transform[0].TEXT_CHECK_AREAS)[0]
                    text = self.controller.recognizer.orc(imgs, "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789//")
                    print("transforming")
                    print("get string:", text)
                    if len(text) > 0:
                        for s in self.text_transform:
                            if s.check_texts[0][0] == text[0]:
                                self.next_state = s
                                return True
                    img = self.controller.get_screen()
        
            else:
                for i in self.check_transform:
                    if i.check_state(img, True):
                        self.next_state = i
                        return True
                State.controller.click_area((430, 284, 686, 453), 0.1)
                return False
        raise RuntimeError("error state")

    def work(self):
        pass
    
    def run(self):
        temp = self.next_state
        self.next_state = None
        return temp

class FgoEndState(WorkState, CheckState):
    def __init__(self, parent = None, check_areas = None, work_areas = None):
        WorkState.__init__(self, parent=parent, work_areas=work_areas)
        CheckState.__init__(self, check_areas=check_areas)

    def check_state(self, img, from_souce = False):
        if not from_souce:
            img = State.controller.get_screen()
        img = State.controller.extract_img(img, self.check_areas)[0]
        return self.is_end(img)

    def is_end(self, image):
        image = np.array(image)
        size = np.size(image)
        #energy = np.sum(image)/size
        dark = np.sum(image < 30)/size
        color = np.sum(image > 235)/size
        print("checking end")
        print(dark, color)
        if dark > 0.75 and color > 0.025:
            return True
        else:
            False
    
    def work(self):
        WorkState.work(self)


def FgoStateFactory():
    path = "1440x810"
    driver = Driver.UiautoDriver()
    top = TopState(10, controller=Controller(driver))
    mission = FgoStartState(top,
                              check_while_work_areas= [1265, 732, 1412, 792],
                              check_imgs = [path + "\\mission.jpg"], 
                              check_areas = [[1200, 727, 1440, 810], ], 
                              work_areas = [[716, 195, 1297, 320], ],
                              times = 2)

    support = ImageCheckClick(mission, check_imgs = [path + "\\support.jpg"],
                                          check_areas= [[1100, 1, 1440, 90]],
                                          work_areas= [[86, 250, 1189, 389], [1265, 732, 1412, 792]],
                                          times = [3, 8])      
    
    apple = ImageCheckClick(mission, check_imgs = [path + "\\apple.jpg"],
                                        check_areas = [[320, 250, 500, 460], ],
                                        work_areas = [[348, 304, 1084, 424], [828, 610, 1062, 656]],
                                        times = 2)
    
    
    apple.add_state(support)


    #0~8  skills
    #9 master skills
    #10~12  suit skills
    #13~15  target
    skill_areas = [(47, 616, 108, 681),
                (149, 618, 215, 683),
                (259, 621, 318, 679),
                (407, 621, 461, 674),
                (512, 625, 569, 679),
                (616, 622, 674, 679),
                (768, 622, 822, 677),
                (872, 625, 927, 680),
                (978, 621, 1034, 679),###

                (1318, 334, 1373, 379),
                (991, 322, 1048, 378),
                (1088, 326, 1147, 375),
                (1189, 323, 1249, 378),##
                
                (297, 401, 446, 572),
                (630, 412, 806, 585),
                (1012, 412, 1159, 569)]
    
    battle_areas = [1207, 639, 1337, 743]
    battle_check_areas = [(1177, 593, 1375, 778), ]
    battle_image = path + "//battle.jpg"
    text_check_areas = [(935, 9, 1060, 44)]

    FgoBattleState.set_skill_areas(skill_areas)
    FgoBattleState.set_battle_areas(battle_areas)
    FgoBattleState.set_battle_check_areas(battle_check_areas)
    FgoBattleState.set_text_check_areas(text_check_areas)
    FgoBattleState.set_battle_image(battle_image)


    FgoBattleState.BATTLE_AREAS = battle_areas
    FgoBattleState.SKILL_AREAS = skill_areas

    cards_areas = [(68, 476, 217, 671),
                    (360, 478, 504, 672),
                    (645, 476, 787, 672),
                    (933, 481, 1084, 674),
                    (1229, 479, 1377, 671),
                    (396, 149, 530, 303),
                    (656, 149, 792, 326),
                    (914, 145, 1053, 327)]
    
    cards_check_areas = [(42, 541, 289, 714),
                        (330, 539, 562, 728),
                        (607, 566, 850, 721),
                        (909, 562, 1141, 706),
                        (1203, 572, 1403, 699)]
    check_imgs = [path + "//blue.jpg", path + "//green.jpg", path + "//red.jpg"]

    FgoCardState.set_cards_areas(cards_areas)
    FgoCardState.set_check_areas(cards_check_areas)
    FgoCardState.set_color_imgs(check_imgs)

    transform = TransformState(support)


    battle1 = FgoBattleState(transform, check_texts = ["1/3"], skills = [3, ])
    cards1 = FgoCardState(battle1, card_seq=[2, 1, 0], ulti= [1,])
    cards1.add_state(transform)

    battle2 = FgoBattleState(transform, check_texts = ["2/3"], skills = [8, 9, 10, 12, 14, 7, 15])
    cards2 = FgoCardState(battle2, card_seq=[2, 1, 0], ulti= [2,])
    cards2.add_state(transform)

    battle3 = FgoBattleState(transform, check_texts = ["3/3"], skills = [])
    cards3 = FgoCardState(battle3, card_seq=[2, 1, 0], ulti= [1,])
    cards3.add_state(transform)

    end = FgoEndState(transform, check_areas=[(129, 475, 1310, 550), (1159, 748, 1367, 780)],
                      work_areas=[(116, 255, 1313, 571)])


    transform.add_text_transform([battle1, battle2, battle3])
    transform.add_check_transoform([end])

    return top

if __name__ == "__main__":
    top = FgoStateFactory()
    top.loop()