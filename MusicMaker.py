"""
filename: MusicMaker.py
Author: Logan Wilson

This program includes methods for generating melodies, displaying melodies
via sheet music, and playing melodies within a homophonic texture.
"""

from random import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class Mozart(object) :
    """This class includes methods for choosing a key, choosing a chord progression, and generating a melodies, both from chord tones and stepwise."""

    def __init__(self,seed_num=None):
        """Sets initial seed as well as data structures for keys, rhythms, chord progressions, and pitches."""

        #Mozart can be initialized from given seed in order to generate a particular melody.
        #If no seed is specified, a random seed is selected and displayed, such that
        #the same melody can be produced later.
        if seed_num == None:
            seed_num = randint(0, 10000000000)
        print(seed_num)
        seed(seed_num)

        #Potential keys in which a melody can be written. More options to be added in future developments.
        self._key_list = ["C","G"]

        #List of common chord progressions
        self._common_chord_progs = [["I","IV","V"],["I","V","vi","IV"],["I","IV","vi","V"],["I","V","vi","iii","IV","I","IV","V"],["vi","V","IV","V"],["I","vi","IV","V"],["I","V","IV","V"]]

        #Chord dictionary - associate each chord with scale degrees
        #fix numbers in this
        self._chord_dict = {"I" : [1,3,5,8],"iii" : [3,0,5,7],"V" : [5,0,2,7], "IV" : [4,1,6,8], "vi" : [6,1,3,8]}

        #Key dictionary - for each key, associate scale degree with pitch
        #formerly key_dict2
        #fix numbers in this
        self._key_dict = {"C" : {0:"B3",1:"C4",2:"D4",3:"E4",4:"F4",5:"G4",6:"A4",7:"B4",8:"C5",9:"D5",10:"E5",11:"F5",12:"G5"},"G" : {-4:"B3",-3:"C4",-2:"D4",-1:"E4",0:"F#4",1:"G4",2:"A4",3:"B4",4:"C5",5:"D5",6:"E5",7:"F#5",8:"G5"}}

        #For each key, associate roman numeral with actual chord
        self._key_chord_dict = {"C" : {"I" : "C","I7":"C","ii":"Dm","V/V":"D","iii":"Em","V7/vi":"E","IV":"F","iv" : "Fm","V":"G","V7" : "G","vi":"Am","viio":"Bdim"},"G" :{"I" : "G","ii":"Am","iii":"Bm","IV":"C","V":"D","V7" : "D","vi":"Em","viio":"F#dim"}}
        
        #Potential rhythms and their associated rhythmic values. Currently, melody is assumed to be 4/4.
        #Further options for time signatures to be added in future developments.
        self._rhythm_list = ["eighth","quarter","half","whole"]
        self._rhythm_dict = {"eighth" : .5,"quarter" : 1,"half" : 2,"whole" : 4}

    def choose_key(self,key=None) :
        """Choose a key in which melody will be written. If no key is given, one will be selected randomly.""" 
        if key==None :
            self._key = choice(self._key_list)
        else :
            self._key = key
        #Select the appropriate dictionary relating scale degrees to pitches within the key.
        self._pitches = self._key_dict[self._key]

    def get_key(self) :
        """Returns the key."""
        return self._key

    def choose_progression(self,progression = None) :
        """Choose a chord progression with which melody will be written. If no progression is given, one will be selected randomly."""
        if progression == None:
            self._prog = choice(self._common_chord_progs)
        else :
            self._prog = progression
        
    def get_progression(self) :
        """Returns the chord progression."""
        return self._prog

    def broken_chord_melody(self,key,prog) :
        self._melody = []
        self._count_list = []
        for roman_numeral_chord in prog:
            chord = self._key_chord_dict[key][roman_numeral_chord]
            scale_degree_list = self._chord_dict[roman_numeral_chord]
            self._rhythm_list=[]
            self.generate_rhythm_list(ct=4) #should add to countlist
            for rhythm in self._rhythm_list :
                pitch_rhythm_pair = []
                scale_degree = choice(scale_degree_list)
                pitch = self._key_dict[self._key][scale_degree]
                pitch_rhythm_pair.append(pitch)
                pitch_rhythm_pair.append(rhythm)
                self._melody.append(pitch_rhythm_pair)

    def get_melody(self) :
        return self._melody

    def generate_rhythm_list(self,ct=4) :
        self._count = 1
        temp_rhythm_list = []
        temp_count_list = []
        while self._count < ct+1 :
            temp_count_list.append(self._count)
            rhythm = self.random_rhythm()
            temp_rhythm_list.append(rhythm)
            rhythmic_value = self._rhythm_dict[rhythm]
            self._count += rhythmic_value
            if self._count > ct+1 :
                return self.generate_rhythm_list(ct)
        for count in temp_count_list :
            self._count_list.append(count)
        for rhythm in temp_rhythm_list :
            self._rhythm_list.append(rhythm)

    def random_rhythm(self) :
        """Returns a rhythm at varying probabilities."""
        prob = randint(1,100)
        if prob < 50 :
            rhythm = "quarter"
        elif prob < 85 :
            rhythm = "eighth"
        else  :
            rhythm = "half"
        return rhythm

    def get_count_list(self) :
        return self._count_list


class Treble(object) :

    def __init__(self,m) :

        #Size of drawing window
        self._width = 1800
        self._height = 200

        #Colors used in notation
        self._white = (255, 255, 255)
        self._black = (0, 0, 0)

        self._image = Image.new("RGB", (self._width, self._height), self._white)
        self._n = ImageDraw.Draw(self._image)

        #Positions relative to top of staff
        self._y_position_dict = {"G5":-5,"F#5":0,"F5":0,"E5" : 5,"D5" : 10, "C5" : 15, "B4" : 20, "A4" : 25, "G4" : 30, "F#4" : 35, "F4" : 35,"E4":40,"D4":45,"C4":50,"B3":55}

        #Clef
        size = 30,60
        treble_clef = Image.open("treble clef.png") #Include image with code
        treble_clef.thumbnail(size)
        self._image.paste(treble_clef,(2,60))

        #Staff
        #o = vertical displacement from top edge of window
        o = 70 #Staff start
        for x in range(5) :
            self._n.line([(0,o),(self._width,o)],self._black)
            o += 10
        self._o=70 #Reset staff start
        
        #Key signature
        font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 18)
        if m.get_key() == "G" :
            self._n.text((30,self._o-9),"#",fill=self._black,font=font)
            self._music_start = 55 #initial position
        else :
            self._music_start = 40
        self._cursor = self._music_start

    def get_cursor(self) :
        return self._cursor
    
    def eighth(self,note) :
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],self._black,self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)
        self._n.line([(self._cursor+10,self._o+y_pos-35),(self._cursor+10+8,self._o+y_pos-35+8)],self._black)
        self.below_staff(note,y_pos)
        
    def quarter(self,note) :
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],self._black,self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)    
        self.below_staff(note,y_pos)
        
    def half(self,note) :
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],outline = self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)
        self.below_staff(note,y_pos)

    def whole(self,note) :
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+15,self._o+y_pos+5)],outline=self._black)
        self.below_staff(note,y_pos)
        
    def below_staff(self,note,y_pos) :
        if note == "C4" or note == "B3":
            self._n.line([(self._cursor-5,self._o+50),(self._cursor+18,self._o+50)],self._black)
                   
    #New measure
    def measure_line(self) :
        self._n.line([(self._cursor,self._o),(self._cursor,self._o+40)],self._black)
        self._cursor += 10

    #Relates rhythm input to associated function
    def notate(self,note,rhythm) :
        if rhythm == "eighth" :
            self.eighth(note)
            self._cursor += 25
        elif rhythm == "quarter" :
            self.quarter(note)
            self._cursor += 50
        elif rhythm == "half" :
            self.half(note)
            self._cursor += 100
        elif rhythm == "whole" :
            self.whole(note)
            self._cursor += 200

    def new_voice(self) :
        self._cursor = self._music_start

    def save(self,filename) :
        self._image.save(filename+".jpg")

def main() :
    m = Mozart()
    m.choose_key()
    m.choose_progression()
    m.broken_chord_melody(m.get_key(),m.get_progression())

    t = Treble(m)
    for x in range(len(m.get_melody())) :
        if m.get_count_list()[x] == 1 and t.get_cursor() > 70:
            t.measure_line() 
        [pitch,rhythm]=m.get_melody()[x]
        t.notate(pitch,rhythm)
    t.save("Sheet Music")


if __name__ == "__main__":
    main()
