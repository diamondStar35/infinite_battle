import ngk
import pygame

def dlg(text, callback=None, sound_file=None):
    """
    Displays a modal dialog. Speaks the text and waits for Enter.
    Optionally plays a sound file in the background.
    """
    sound = None
    if sound_file:
        sound = ngk.snd.Sound()
        # Try to load the sound, and if successful, play it.
        if sound.load(sound_file):
            sound.play()
        else:
            sound = None

    ngk.speak(text)
    while True:
        ngk.process()
        pygame.time.wait(5)
        if callable(callback): callback
        if ngk.key_pressed(pygame.K_LEFT) or ngk.key_pressed(pygame.K_RIGHT) or ngk.key_pressed(pygame.K_UP) or ngk.key_pressed(pygame.K_DOWN):
            ngk.speak(text)
        if ngk.key_pressed(pygame.K_RETURN):
            # If a sound is playing, fade it out before breaking the loop.
            if sound:
                fade(sound, 20)
            break

def dlg_list(texts):
    for i in texts:
        dlg(i)

def dlgplay(path):
    s=ngk.snd.Sound()
    s.load(path)
    s.play()
    while s.handle.is_playing==True:
        ngk.process()
        if  ngk.key_pressed(ngk.K_RETURN):
            fade(s,20)
            break

def fade(snd,fadespeed=20):
    if not snd or not snd.handle: # Add a check to prevent errors if sound is None
        return
    fadetimer=ngk.Timer()
    while snd.volume>-60:
        ngk.process()
        pygame.time.wait(5)
        if fadetimer.elapsed>=fadespeed:
            fadetimer.restart()
            snd.volume-=1
        if snd.volume<=-60:
            snd.stop()
