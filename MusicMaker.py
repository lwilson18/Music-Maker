"""
filename: MusicMaker.py
Author: Logan Wilson

This program includes methods for generating melodies, displaying melodies
via sheet music, and playing melodies within a homophonic texture.
Pydub, treble clef.png, as well as folders containing Piano Samples,
Major Chords, and Minor Chords, are all required.

Future developments: More key signature options, incidental notes, GUI for
selecting notes from a piano, notation improvements (e.g. stem directions,dynamic/tempo marks),
MIDI support, more time signatures, variable tempo, different instrument samples
"""
import os
from random import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pydub import AudioSegment #Need pydub folder downloaded to working directory

class Mozart(object) :
    """This class includes methods for choosing a key, choosing a chord progression, and generating a melodies, both from chord tones and stepwise."""

    def __init__(self,seed_num=None):
        """Sets initial seed as well as data structures for keys, rhythms, chord progressions, and pitches."""

        #Mozart can be initialized from given seed in order to generate a particular melody.
        #If no seed is specified, a random seed is selected and displayed, such that the same melody can be produced later.
        if seed_num == None:
            seed_num = randint(0, 10000000000)
        print(seed_num)
        seed(seed_num)

        #Potential keys in which a melody can be written. More options to be added in future developments.
        self._key_list = ["C","G"]

        #List of common chord progressions
        self._common_chord_progs = [["I","IV","V"],["I","V","vi","IV"],["I","IV","vi","V"],["I","V","vi","iii","IV","I","IV","V"],["vi","V","IV","V"],["I","vi","IV","V"],["I","V","IV","V"]]

        #Chord dictionary - associate each chord with scale degrees
        self._chord_dict = {"I" : [1,3,5,8],"iii" : [3,0,5,7],"V" : [5,0,2,7], "IV" : [4,1,6,8], "vi" : [6,1,3,8]}

        #Key dictionary - for each key, associate scale degree with pitch
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

    def chord_list(self,cadence = True) :
        """returns the chord list for the given progression"""
        self._chord_list = []
        for chord in self._prog :
            self._chord_list.append(self._key_chord_dict[self._key][chord])
            
        #If a cadence is desired, at the tonic chord to the end of the chord list
        if cadence == True :
            self._chord_list.append(self.tonic_chord())
        return self._chord_list    

    def broken_chord_melody(self,key,prog,cadence=True) :
        """Generates a melody with one chord per measure, with each measure containing only notes from the associated chords."""
        self._melody = [] #List that will contain pitch and rhythm pairs
        self._count_list = [] #List holding the counts for the entire melody - appended within generate_rhythm_list method. Useful for knowing when a measure starts.
        for roman_numeral_chord in prog:
            scale_degree_list = self._chord_dict[roman_numeral_chord] #Potential scale degrees for the chord
            self._rhythm_list=[] #Rhythms for the measure - appended within generate_rhythm_list method
            self.generate_rhythm_list(ct=4)
            for rhythm in self._rhythm_list : #Pick a pitch for each rhythm and add to melody list
                pitch_rhythm_pair = []
                scale_degree = choice(scale_degree_list)
                pitch = self._key_dict[key][scale_degree]
                pitch_rhythm_pair.append(pitch)
                pitch_rhythm_pair.append(rhythm)
                self._melody.append(pitch_rhythm_pair)

        #If a cadence is desired, add a whole note at the tonic pitch to the end of the melody.
        if cadence == True:
            self._melody.append([self.tonic_pitch(),"whole"])
            self._count_list.append(1)

    def stepwise_melody(self,key,prog,cadence = True) :
        """Generates a melody with stepwise motion."""
        self._melody = []
        self._rhythm_list = []
        self._count_list = []
        pitch_list = [] #List of scale degrees
        pitch_list.append(choice(self._chord_dict[prog[0]])) #Adds tonic scale degree
        for roman_numeral_chord in prog :
            self.generate_rhythm_list(ct=4)

        #Select subsequent pitch based on current pitch
        for x in range(len(self._rhythm_list)-1) :
            prev_pitch = pitch_list[x]
            prob = randint(1,100)
            if (self.get_key() == "C" and prev_pitch == 0) or (self.get_key() == "G" and prev_pitch == -4) :
                next_pitch = prev_pitch + 1
            elif (self.get_key() == "C" and prev_pitch == 12) or (self.get_key() == "G" and prev_pitch == 8) :
                next_pitch = prev_pitch - 1
            elif prob <= 50 :
                next_pitch = prev_pitch + 1
            elif prob >50 :
                next_pitch = prev_pitch - 1
            pitch_list.append(next_pitch)

        #Make sure first pitch in each measure is in the appropriate chord
        measure_num = -1
        for x in range(len(pitch_list)) :
            if self._count_list[x] == 1 :
                measure_num += 1
                if pitch_list[x] not in self._chord_dict[prog[measure_num]]:
                    return self.stepwise_melody(key,prog,cadence) #Otherwise, start over
            pitch_rhythm_pair = [self._key_dict[self.get_key()][pitch_list[x]],self._rhythm_list[x]]
            self._melody.append(pitch_rhythm_pair)
            
        if cadence == True:
            self._melody.append([self.tonic_pitch(),"whole"])
            self._count_list.append(1)

    def get_melody(self) :
        """Returns the melody list, containing pairs of pitches and rhythms."""
        return self._melody

    def tonic_pitch(self) :
        """"Returns the pitch of the tonic (first chord in the chord progression)"""
        return self._key_dict[self._key][self._chord_dict[self._prog[0]][0]]

    def tonic_chord(self) :
        """Returns chord of the tonic."""
        return self._key_chord_dict[self._key][self._prog[0]]

    def generate_rhythm_list(self,ct=4) :
        """Generate a list of rhythms to fill a measure."""
        self._count = 1
        temp_rhythm_list = []
        temp_count_list = []
        while self._count < ct+1 : #As long as measure isn't full, keep looping
            temp_count_list.append(self._count) #Add the current count
            rhythm = self.random_rhythm() #Choose a random rhythm
            temp_rhythm_list.append(rhythm)
            rhythmic_value = self._rhythm_dict[rhythm]
            self._count += rhythmic_value #Augment the count
            if self._count > ct+1 : #If the count is bigger than that allowable for the measure, start over
                return self.generate_rhythm_list(ct)
        #Once an appropriate list of rhythms has been produced, append the count list and rhythm list
        for count in temp_count_list : 
            self._count_list.append(count)
        for rhythm in temp_rhythm_list :
            self._rhythm_list.append(rhythm)

    def random_rhythm(self) :
        """Returns a random rhythm"""
        prob = randint(1,100)
        if prob < 50 : #50% chance of quarter note
            rhythm = "quarter"
        elif prob < 85 : #35% chance of eigth note
            rhythm = "eighth"
        else  : #15% chance of half note
            rhythm = "half"
        #can also include whole notes as a possibility, but this generally does not produce interesting melody lines
        return rhythm

    def get_count_list(self) :
        """Returns the count list"""
        return self._count_list


class Treble(object) :
    """This class draws a staff with clef and key signature, and includes methods for music notation."""

    def __init__(self,key) :
        """Creates a staff with clef and key signature. Must input key in order to draw key signature."""
        
        #Size of drawing window
        self._width = 1800
        self._height = 200

        #Colors used in notation
        self._white = (255, 255, 255)
        self._black = (0, 0, 0)

        #Initializes the image class
        self._image = Image.new("RGB", (self._width, self._height), self._white)
        self._n = ImageDraw.Draw(self._image)

        #Positions relative to top of staff
        self._y_position_dict = {"G5":-5,"F#5":0,"F5":0,"E5" : 5,"D5" : 10, "C5" : 15, "B4" : 20, "A4" : 25, "G4" : 30, "F#4" : 35, "F4" : 35,"E4":40,"D4":45,"C4":50,"B3":55}

        #Clef
        size = 30,60
        treble_clef = Image.open("treble clef.png") #Image file should be in working directory
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
        if key == "G" :
            self._n.text((30,self._o-9),"#",fill=self._black,font=font)
            self._music_start = 55 #initial position
        else :
            self._music_start = 40
        self._cursor = self._music_start #Cursor tracks horizontal position on the page

    def get_cursor(self) :
        """Returns the position of the cursor"""
        return self._cursor
    
    def eighth(self,note) :
        """Draws an eighth note for a given pitch."""
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],self._black,self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)
        self._n.line([(self._cursor+10,self._o+y_pos-35),(self._cursor+10+8,self._o+y_pos-35+8)],self._black)
        self.ledger_line(note,y_pos)
        
    def quarter(self,note) :
        """Draws a quarter note for a given pitch."""
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],self._black,self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)    
        self.ledger_line(note,y_pos)
        
    def half(self,note) :
        """Draws a half note for a given pitch."""
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+10,self._o+y_pos+5)],outline = self._black)
        self._n.line([(self._cursor+10,self._o+y_pos),(self._cursor+10,self._o+y_pos-35)],self._black)
        self.ledger_line(note,y_pos)

    def whole(self,note) :
        """Draws a whole note for a given pitch."""
        y_pos = self._y_position_dict[note]
        self._n.ellipse([(self._cursor,self._o+y_pos-5),(self._cursor+15,self._o+y_pos+5)],outline=self._black)
        self.ledger_line(note,y_pos)
        
    def ledger_line(self,note,y_pos) :
        """If a note is below the staff, adds ledger lines - in future developments, include options for notes above the staff."""
        if note == "C4" or note == "B3":
            self._n.line([(self._cursor-5,self._o+50),(self._cursor+18,self._o+50)],self._black)
                   
    def measure_line(self) :
        """Draw a measure line"""
        self._n.line([(self._cursor,self._o),(self._cursor,self._o+40)],self._black)
        self._cursor += 10

    def notate(self,note,rhythm) :
        """Calls appropriate rhythm method for notating pitch and moves cursor to appropriate postion."""
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
        """Move cursor to start in order to add another voice."""
        self._cursor = self._music_start

    def save(self,filename) :
        """Saves image to given filename within working directory. In order to view sheet music, open this file."""
        self._image.save(filename+".jpg")

class Sinatra(object) :
    """This class creates an audio file to play a given melody within a homophonic texture - i.e., basic chordal accompaniment."""
    
    def export(self,file,filename) :
        """Expects audio segment and saves as a wav file to filename within current working directory."""
        file.export(os.getcwd()+"/"+filename+".wav", format="wav")

    def sing(self,note_rhythm_pairs):
        """Reads pairs of pitches and rhythms to create an audio segment"""
        song = AudioSegment.empty()
        for [note,rhythm] in note_rhythm_pairs :
            if rhythm == "whole" :
                song += self.whole(note)
            elif rhythm == "half" :
                song += self.half(note)
            elif rhythm == "quarter" :
                song += self.quarter(note)
            elif rhythm == "eighth" :
                song += self.eighth(note)
        return song

    def chord(self,chord,sample_length) :
        """Creates audio segment for given chord with given duration"""
        if "m" in chord : #Chord is minor
            return AudioSegment.from_file(os.getcwd()+"/Minor Chords/Grand Piano - Fazioli - minor chords - "+chord+" lower.wav",format="wav")[:sample_length]
        else : #Otherwise, chord is major
            return AudioSegment.from_file(os.getcwd()+"/Major Chords/Grand Piano - Fazioli - major "+chord+".wav",format="wav")[:sample_length]

    def harmony(self,melody_1,melody_2) :
        """Overlays two melodies to play simultaneously."""
        return melody_1.overlay(melody_2)
    
    def chord_progression_audio(self,chord_list) :
        """Creates an audio segment playing chords from given chord list"""
        sample_length = 1400+100*(len(chord_list)-1)/len(chord_list) #Sets sample duration to account for time lost during crossfade
        progression_audio = self.chord(chord_list[0],sample_length) #first chord in progression
        for chord in chord_list[1:] : #add each chord to audio segment. Crossfade applied to eliminate cracks.
            progression_audio = progression_audio.append(self.chord(chord,sample_length),crossfade=100)
        return progression_audio

    def accompany(self,melody,chord_list) :
        """Takes a melody and plays it over a basic chordal accompaniment. Slight offset applied to account for small discrepancies between starting times for pitches and chords."""
        return self.offset(melody,100,"start").overlay(self.offset(self.chord_progression_audio(chord_list),100,"end"))
            
    def eighth(self,note) :
        """Creates audio segment for an eighth note at given pitch."""
        return AudioSegment.from_file(os.getcwd()+"/Piano Samples/"+note+".wav",format="wav")[:175]

    def quarter(self,note) :
        """Creates audio segment for a quarter note at given pitch."""
        return AudioSegment.from_file(os.getcwd()+"/Piano Samples/"+note+".wav",format="wav")[:350]

    def half(self,note) :
        """Creates audio segment for a half note at given pitch."""
        return AudioSegment.from_file(os.getcwd()+"/Piano Samples/"+note+".wav",format="wav")[:700]

    def whole(self,note) :
        """Creates audio segment for a whole note at given pitch."""
        return AudioSegment.from_file(os.getcwd()+"/Piano Samples/"+note+".wav",format="wav")[:1400]

    def offset(self,sound,delay,position) :
        """Offsets given audio segment with silence, depending on position"""
        if position == "start" : #Add delay at start of audio
            return AudioSegment.silent(duration=delay) + sound
        elif position == "end" : #Add delay at end of audio
            return sound + AudioSegment.silent(duration=delay)

def main() :
    """Creates a melody of chord tones, notates it, and creates an audio file of the melody over a homophonic texture."""

    #Single voice, broken chord melody
    #Compose the melody
    m1 = Mozart()
    m1.choose_key()
    m1.choose_progression()
    m1.broken_chord_melody(m1.get_key(),m1.get_progression())
    
    #Notate the melody
    t1 = Treble(m1.get_key())
    for x in range(len(m1.get_melody())) :
        if m1.get_count_list()[x] == 1 and t1.get_cursor() > 70: #Prevent measure line from being drawn immediately after clef
            t1.measure_line() 
        [pitch,rhythm]=m1.get_melody()[x]
        t1.notate(pitch,rhythm)
    t1.save("Broken Chord Melody Sheet Music") #Image saved under Broken Chord Melody Sheet Music.jpg

    #Create audio file with melody over accompaniment.
    s1 = Sinatra()
    audio1 = s1.accompany(s1.sing(m1.get_melody()),m1.chord_list())
    s1.export(audio1,"Broken Chord Melody Audio") #audio saved under Broken Chord Melody Audio.wav

    #Single voice, stepwise melody
    m2 = Mozart()
    m2.choose_key()
    m2.choose_progression()
    m2.stepwise_melody(m2.get_key(),m2.get_progression())

    t2 = Treble(m2.get_key())
    for x in range(len(m2.get_melody())) :
        if m2.get_count_list()[x] == 1 and t2.get_cursor() > 70:
            t2.measure_line() 
        [pitch,rhythm]=m2.get_melody()[x]
        t2.notate(pitch,rhythm)
    t2.save("Stepwise Melody Sheet Music")

    s2 = Sinatra()
    audio2 = s2.accompany(s2.sing(m2.get_melody()),m2.chord_list())
    s2.export(audio2,"Stepwise Melody Audio") 
    
    #Two voices, broken chord melody
    #Compose two melodies with same key and chord progression
    mA = Mozart()
    mA.choose_key()
    mA.choose_progression()
    mA.broken_chord_melody(mA.get_key(),mA.get_progression())

    mB = Mozart()
    mB.choose_key(mA.get_key())
    mB.choose_progression(mA.get_progression())
    mB.broken_chord_melody(mB.get_key(),mB.get_progression())
    
    #Notate both melodies on same sheet music
    tAB = Treble(mA.get_key())
    for x in range(len(mA.get_melody())) :
        if mA.get_count_list()[x] == 1 and tAB.get_cursor() > 70:
            tAB.measure_line() 
        [pitch,rhythm]=mA.get_melody()[x]
        tAB.notate(pitch,rhythm)
    tAB.new_voice()
    for x in range(len(mB.get_melody())) :
        if mB.get_count_list()[x] == 1 and tAB.get_cursor() > 70:
            tAB.measure_line() 
        [pitch,rhythm]=mB.get_melody()[x]
        tAB.notate(pitch,rhythm)
    tAB.save("Duet Sheet Music") 

    #Create audio file with both melodies over accompaniment.
    sAB = Sinatra()
    duet = sAB.harmony(sAB.sing(mA.get_melody()),sAB.sing(mB.get_melody()))
    audioAB = sAB.accompany(duet,mA.chord_list())
    sAB.export(audioAB,"Duet Audio") 


if __name__ == "__main__":
    main()
