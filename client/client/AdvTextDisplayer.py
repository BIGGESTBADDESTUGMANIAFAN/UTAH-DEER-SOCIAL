import pygame
import pynput
import time

def InsertStr(Old:str, Sub:str, index:int)->str:
    return Old[:index] + Sub + Old[index:]




def PrintA(Object):
    Text.append(Object if type(Object) == str else Object.__repr__())


def InputA() -> str:
    global AwaitingInput
    AwaitingInput = True
    while AwaitingInput:
        time.sleep(0.1)
    return LastInput



def KeyboardInput(Key : pynput.keyboard.KeyCode):
    global TypingLine, Charon
    if not pygame.key.get_focused():
        return
    try:
        TypingLine = InsertStr(TypingLine, Key.char, len(TypingLine)-Charon)
    except:
        match Key:
            case pynput.keyboard.Key.space:
                TypingLine = InsertStr(TypingLine, " ", len(TypingLine)-Charon)
            case pynput.keyboard.Key.left:
                Charon = min(Charon + 1, len(TypingLine))
            case pynput.keyboard.Key.right:
                Charon = max(Charon - 1,0)
            case pynput.keyboard.Key.backspace:
                if len(TypingLine) > Charon:
                    TypingLine = TypingLine[:len(TypingLine)-1-Charon] + TypingLine[ len(TypingLine)-Charon:]
            case pynput.keyboard.Key.delete:
                TypingLine = TypingLine[:len(TypingLine)-Charon] + TypingLine[ len(TypingLine)+1-Charon:]
                Charon = max(Charon - 1,0)
            case pynput.keyboard.Key.enter:
                Typeline(TypingLine)
                Charon = 0
                TypingLine = ""

def Typeline(Line: str):
    global LastInput, AwaitingInput
    if AwaitingInput:
        LastInput = Line
        AwaitingInput = False

#globals
    
LastInput : str = ""
TypingLine : str = ""
AwaitingInput : bool = False
#note: Charon is characters LEFT of the end of the string.
Charon : int = 0
running = True
FontSize = 20
Text : list[str] = []
offset = 0


def init():
    global LastInput, TypingLine, AwaitingInput, Charon, running, FontSize, Text, offset
    time.sleep(0.1)
    Screen = pygame.display.set_mode((400,400), pygame.RESIZABLE)
    pygame.init()
    Ticktime = 0
    LastFrame = 0
    pynput.keyboard.Listener(KeyboardInput).start()
    pygame.display.set_caption("Utah Deer Social", "Gyat Social")
    while running:
        Ticktime = (Ticktime+(time.time()-LastFrame))%1
        LastFrame = time.time()
        Screen.fill((10,10,10))
        YCoord = offset
        for Line in Text:
            if pygame.display.get_window_size()[1] > YCoord >= -FontSize:
                Screen.blit(pygame.font.Font('freesansbold.ttf', FontSize).render(Line, True, (255,255,255)), (0, YCoord))
            YCoord += FontSize
        pygame.draw.rect(Screen, (80,80,80), pygame.rect.Rect(0, pygame.display.get_window_size()[1]-1.25*(FontSize+7.5), pygame.display.get_window_size()[0], 100))
        Screen.blit(pygame.font.Font('freesansbold.ttf', int(1.25*FontSize)).render(TypingLine, True, (255,255,255)), (0, pygame.display.get_window_size()[1]-1.25*FontSize))
        if Ticktime < .666 and pygame.key.get_focused():
            pygame.draw.rect(Screen, (255,255,255), pygame.rect.Rect(pygame.font.Font('freesansbold.ttf', int(1.25*FontSize)).render(TypingLine[:len(TypingLine)-Charon], True, (255,255,255)).get_bounding_rect().right, pygame.display.get_window_size()[1]-1.25*FontSize, 3, 1.25*FontSize))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                offset = min(offset + event.y, 0)
    pygame.quit()