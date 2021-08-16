import tkinter as tk
from tkinter import filedialog
import csv
from os import remove
from os import mkdir
import sys
import threading
import pygame
import random
import time
from mutagen.mp3 import MP3
import numpy as np
import librosa
import math
import subprocess
import pafy
import keras

pygame.init()
pygame.mixer.init(48000, -16, 1, 1024)
song_pointer = ""
path = ""
showing_list = False
selected = ""
playlist_thread = ""
genre = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
plist = ""
add_thread = ""
mute = False
slist = ""
showing_default = False
curr_se = []
delete_btn = ""
add_s = ""
sel_song = ""
sel_playlist = ""
pygame.mixer.init()
playing = False
p = 0
playing_playlist = False
flag = 0
dur = 0
dur_need = False
song_len = 0
song_no = 0
p_data = []
p_list = ""
user_play = False
not_down = []
down = []
busy = False
new_model = keras.models.load_model('cnnmodel')

def pied(path):
    global new_model
    l = []
    l.append(path)
    dic = {}
    x = []
    d = 0
    SAMPLE_RATE = 22050

    def predict(model, X):

        X = X[np.newaxis, ...]
        prediction = model.predict(X)

        predicted_index = np.argmax(prediction, axis=1)

        genre = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
        type_ = genre[predicted_index[0]]
        return type_

    def identifier(signal, sample_rate):
        SAMPLES_PER_TRACK = sample_rate * 30
        num_segments = 10
        hop_length = 512
        num_mfcc = 13
        n_fft = 2048
        samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
        num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)

        for d in range(num_segments):
            start = samples_per_segment * d
            finish = start + samples_per_segment

            mfcc = librosa.feature.mfcc(signal[start:finish], sample_rate, n_mfcc=num_mfcc, n_fft=n_fft,
                                        hop_length=hop_length)
            mfcc = mfcc.T

            if len(mfcc) == num_mfcc_vectors_per_segment:
                break

        x = mfcc[..., np.newaxis]
        return predict(new_model, x)

    while True:
        try:
            signal, sample_rate = librosa.load(path, offset=d)
            print("duration", d, " ", d + 30)
            dur = str(d) + ":" + str(d + 30)
            dic[dur] = identifier(signal, sample_rate)
            d = d + 30
        except:
            l.append(dic)
            break
    return l


def browse():
    global path
    global playing
    global song_pointer
    global playing_playlist
    global dur_need
    global song_len
    global dur
    global song_no
    playing = True
    playing_playlist = False
    path = filedialog.askopenfile()
    curr_se.append(path.name)
    pygame.mixer.music.load(curr_se[-1])
    song_no = len(curr_se) - 1
    dur_need = True
    dur = 0
    try:
        thread_dur.start()
    except:
        pass
    song_pointer = path.name.split("/")[-1]
    pygame.mixer.music.play()
    status.config(text=song_pointer)
    audio = MP3(path.name)
    song_len = audio.info.length
    dur_scale.config(state="active", from_=0, to=round(song_len))
    chk_play()
    try:
        slist.insert(len(curr_se), path.name.split("/")[-1])
    except:
        pass


def exit():
    global not_down
    pygame.quit()
    print(not_down)
    print("exit")
    for i in not_down:
        try:
            remove(r"{}".format(i))
        except:
            print(i)
            pass
    wn.destroy()
    sys.exit()


def show_playlist():
    global showing_list
    global genre
    global sel_playlist
    global plist
    if showing_list == True:
        plist.destroy()
        sel_playlist.destroy()
        showing_list = False
    else:
        plist = tk.Listbox(wn, bg="silver", bd=4, cursor="arrow", fg="red", relief="groove")
        for i in range(len(genre)):
            plist.insert(i + 1, genre[i].title())
        plist.place(relx=0.7, rely=0.68, anchor="center")
        sel_playlist = tk.Button(wn, text="Select", command=select_playlist)
        sel_playlist.place(relx=0.7, rely=0.84, anchor="center")
        showing_list = True


def add_song_():
    global add_thread
    path = filedialog.askopenfile()
    path = path.name
    load = tk.PhotoImage(file="loading.png")
    label = tk.Label(wn, text="ADDING SONG TO IN-BUILT PLAYLISTS", image=load, compound="right")
    label.place(relx=0.85, rely=0.05, anchor="center")
    data = []
    d = {"blues": [], "classical": [], "country": [], "disco": [], "hiphop": [], "jazz": [], "metal": [], "pop": [],
         "reggae": [], "rock": []}
    subprocess.call(['ffmpeg', '-i', path,
                     'test.wav'])
    d1 = pied("test.wav")
    remove("test.wav")
    print(d1)
    print(d1[1].keys())
    for dur in d1[1].keys():
        gen = d1[1][dur]
        l = d[gen]
        l.append(dur)
        d[gen] = l
    data.append(path)
    for i in d.keys():
        data.append(d[i])
    f = open("playlist_data.csv", "a")
    csv.writer(f).writerow(data)
    print("song added successfully")
    f.close()
    label.destroy()
    label = tk.Label(wn, text="SONG ADDED SUCCESSFULLY")
    label.place(relx=0.85, rely=0.05, anchor="center")
    sec = time.perf_counter()
    while True:
        la = time.perf_counter()
        if la - sec >= 2:
            label.destroy()
            break


def processing():
    global add_thread
    add_thread = threading.Thread(target=add_song_)
    add_thread.start()


def play_():
    global playing
    if playing:
        playing = False
    else:
        playing = True
    chk_play()


def stop_():
    global playing_playlist
    global playing
    global song_pointer
    global status
    global dur_need
    global dur
    global dur_scale
    dur = 0
    dur_scale.set(0)
    dur_scale.config(state="disabled")
    dur_need = False
    song_pointer = "NO PLAYING MEDIA"
    playing = False
    status.config(text="NO MEDIA PLAYING")
    playing_playlist = False
    pygame.mixer.music.stop()


def mute_unmute():
    global sound_btn
    global mute
    if mute == True:
        sound_btn.config(image=sound)
        pygame.mixer.music.set_volume(0.7)
        scale.set(70)
        mute = False
    else:
        sound_btn.config(image=mute_img)
        pygame.mixer.music.set_volume(0)
        scale.set(0)
        mute = True


def show_default():
    global showing_default
    global sel_song
    global slist
    global delete_btn
    global add_s
    if not showing_default:
        showing_default = True
        slist = tk.Listbox(wn, bg="silver", bd=4, cursor="arrow", fg="red", relief="groove", xscrollcommand=True,
                           yscrollcommand=True, width=40)
        for i in range(len(curr_se)):
            slist.insert(i + 1, curr_se[i].split("/")[-1])
        slist.place(relx=0.01, rely=0.67, anchor="w")
        delete_btn = tk.Button(wn, text="Remove", command=remove_song)
        add_s = tk.Button(wn, text="ADD", command=add_song_def)
        delete_btn.place(relx=0.05, rely=0.81, anchor="nw")
        add_s.place(relx=0.01, rely=0.81, anchor="nw")
        sel_song = tk.Button(wn, text="Select", command=select_song)
        sel_song.place(relx=0.143, rely=0.832, anchor="center")

    else:
        showing_default = False
        delete_btn.destroy()
        add_s.destroy()
        sel_song.destroy()
        slist.destroy()


def remove_song():
    curr_se.pop(slist.curselection()[0])
    slist.delete(slist.curselection()[0])


def add_song_def():
    global path
    global curr_se
    path = filedialog.askopenfile()
    song_name = path.name.split("/")[-1]
    slist.insert(len(curr_se) + 1, song_name)
    curr_se.append(path.name)


def select_song():
    global slist
    global showing_default
    global playing
    global playing_playlist
    global song_pointer
    global dur_need
    global dur
    global song_len
    global dur_scale
    global song_no
    playing_playlist = False
    s = slist.curselection()[0]
    if dur_need:
        dur = 0
        dur_need = False
    slist.destroy()
    delete_btn.destroy()
    add_s.destroy()
    sel_song.destroy()
    playing = True
    audio = MP3(curr_se[s])
    song_no = s
    song_len = audio.info.length
    dur_scale.config(state="active", from_=0, to=round(song_len))
    print(type(song_len), song_len)
    song_pointer = curr_se[s].split("/")[-1]
    status.config(text=song_pointer)
    pygame.mixer.music.load(curr_se[s])
    pygame.mixer.music.play()
    showing_default = False
    dur_need = True
    try:
        thread_dur.start()
    except:
        pass
    chk_play()


def set_vol(val):
    global mute
    vol = int(val) / 100
    pygame.mixer.music.set_volume(vol)


def select_playlist():
    global p
    global plist
    global playing_playlist
    global genre
    global playlist_thread
    global showing_list
    global playing
    global flag
    if playing_playlist:
        playing_playlist = False
        pygame.mixer.music.stop()
        select_playlist()
    else:
        p = plist.curselection()[0]
        print(genre[p])
        plist.destroy()
        sel_playlist.destroy()
        showing_list = False
        playing = True
        playlist_thread = threading.Thread(target=play_playlist)
        playlist_thread.start()
        playing_playlist = True


def play_playlist():
    global playing_playlist
    global p
    global playlist_thread
    global playing
    global status
    global song_pointer
    global genre
    p += 1
    playing = True
    playlist = []
    file_data = []
    f = open("playlist_data.csv", "r")
    reader = csv.reader(f)
    flag = 0
    for i in reader:
        if flag == 0:
            flag = 1
        else:
            file_data.append(i)
    for i in file_data:
        if len(i) > 1 and len(i[p]) >= 1:
            playlist.append((i[0], i[p]))
    imp_play = []
    for i in playlist:
        l = []
        dur = eval(i[1])
        for j in dur:
            s = j.split(":")
            s1 = []
            for k in s:
                s1.append(eval(k))
            l.append(s1)
        imp_play.append((i[0], l))
    chk_play()
    while playing and playing_playlist:
        n = random.randrange(0, len(imp_play))
        if imp_play[n][1] != []:
            s = time.perf_counter()
            s = random.randrange(0, len(imp_play[n][1]))
            song_pointer = genre[p - 1] + ":" + imp_play[n][0].split("/")[-1]
            status.config(text=song_pointer)
            pygame.mixer.music.load(imp_play[n][0])
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.music.play(start=imp_play[n][1][s][0])
            print(imp_play[n][0], imp_play[n][1][s])
            while pygame.mixer.music.get_busy():
                if pygame.mixer.music.get_pos() / 100 <= 280:
                    if playing_playlist:
                        pygame.event.wait
                else:
                    pygame.mixer.music.fadeout(600)
    else:
        print("closed")
        playing_playlist = False


def chk_play():
    global play_btn
    global playing
    global dur_need
    global dur_scale
    if playing:
        dur_need = True
        pygame.mixer.music.unpause()
        play_btn.config(image=pause)
    else:
        dur_need = False
        pygame.mixer.music.pause()
        play_btn.config(image=play)


def forward_():
    global dur
    dur += 10
    pygame.mixer.music.rewind()
    pygame.mixer.music.set_pos(dur)


def backward_():
    global dur
    dur -= 10
    if dur < 0:
        dur = 0
    pygame.mixer.music.rewind()
    pygame.mixer.music.set_pos(dur)


def duration_control():
    global dur
    global song_pointer
    global dur_scale
    global playing
    global song_len
    while True:
        if song_pointer != "NO PLAYING MEDIA" or song_pointer != "":
            pass
        else:
            dur_scale.set(0)
            dur_scale.config(state="disabled")
        if playing_playlist:
            dur_scale.config(state="disabled")
        while dur_need:
            time.sleep(1)
            dur += 1
            if song_len <= dur:
                queue()
            if not playing_playlist:
                if song_pointer != "NO PLAYING MEDIA":
                    dur_scale.set(dur)
                else:
                    dur_scale.config(state="disabled")
            else:
                dur_scale.set(0)
                dur_scale.config(state="disabled")

        if not playing:
            time.sleep(0.2)


def dur_val(val):
    global dur
    global dur_scale
    if dur_scale["state"] == "active" and song_pointer != "NO PLAYING MEDIA":
        if abs(int(val) - dur) > 0:
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(dur)
            dur = int(val)


def queue(i="o"):
    global song_no
    global curr_se
    global dur
    global dur_scale
    global playing
    global song_len
    global dur_need
    global song_pointer
    if playback_state == "normal":
        if i != "p":
            if song_no != len(curr_se) - 1:
                song_no = song_no + 1
            else:
                song_no = 0
        else:
            if song_no != 0:
                song_no = song_no - 1
            else:
                song_no = len(curr_se) - 1
    elif playback_state == "shuffle":
        n = random.randrange(0, len(curr_se))
        if n != song_no:
            song_no = n
        else:
            song_no = song_no + 1
    elif playback_state == "loop":
        song_no = song_no
        if i == "n":
            if song_no != len(curr_se) - 1:
                song_no += 1
            else:
                song_no = 0
        elif i == "p":
            if song_no != 0:
                song_no = song_no - 1
            else:
                song_no = len(curr_se) - 1
    audio = MP3(curr_se[song_no])
    song_len = audio.info.length
    dur_scale.config(state="active", from_=0, to=round(song_len))
    pygame.mixer.music.load(curr_se[song_no])
    dur = 0
    dur_need = True
    song_pointer = curr_se[song_no].split("/")[-1]
    playing = True
    pygame.mixer.music.play()
    status.config(text=curr_se[song_no].split("/")[-1])


def playback_():
    global playback_state
    if playback_state == "normal":
        playback_state = "shuffle"
        playback.config(image=shuffle)
    elif playback_state == "shuffle":
        playback_state = "loop"
        playback.config(image=loop)
    elif playback_state == "loop":
        playback_state = "normal"
        playback.config(image=normal)


def create_playlist():
    create_playlist.l = []
    create_playlist.i = 0

    def add_new():
        add_path = filedialog.askopenfile()
        create_playlist.l.append(add_path.name)
        new_playlist.insert(create_playlist.i, add_path.name.split("/")[-1])
        create_playlist.i += 1

    def remove_n():
        n = new_playlist.curselection()[0]
        new_playlist.delete(n)
        create_playlist.l.pop()

    def done_():
        data = []
        data.append(list_name.get())
        data.append(create_playlist.l)
        add.destroy()
        done.destroy()
        remove_.destroy()
        cancel.destroy()
        list_name.destroy()
        new_playlist.destroy()
        f = open("user_playlist.csv", "a")
        writer = csv.writer(f)
        writer.writerow(data)
        f.close()

        def x():
            lab.destroy()
            button.destroy()

        lab = tk.Label(wn, text="Playlist Added", font=("Arial", 15, "normal"), fg="purple")
        button = tk.Button(wn, text="OK", command=x)
        lab.place(relx=0.5, rely=0.48, anchor="center")
        button.place(relx=0.5, rely=0.54, anchor="center")

    def cancel_():
        add.destroy()
        done.destroy()
        remove_.destroy()
        list_name.destroy()
        new_playlist.destroy()
        cancel.destroy()

    new_playlist = tk.Listbox(wn, bg="white", bd=3, cursor="arrow", fg="red", relief="groove", xscrollcommand=True,
                              yscrollcommand=True, width=60)
    add = tk.Button(wn, text="Add", command=add_new)
    new_playlist.place(relx=0.5, rely=0.5, anchor="center")
    add.place(relx=0.4, rely=0.68, anchor="center")
    done = tk.Button(wn, text="Done", command=done_)
    remove_ = tk.Button(wn, text="Remove", command=remove_n)
    done.place(relx=0.54, rely=0.68, anchor="center")
    remove_.place(relx=0.47, rely=0.68, anchor="center")
    cancel = tk.Button(wn, text="Cancel", command=cancel_)
    cancel.place(relx=0.5, rely=0.29, anchor="center")
    list_name = tk.Entry(wn, font=("Arial", 13, "normal"), fg="purple")
    list_name.insert(0, "enter playlist name")
    list_name.place(relx=0.5, rely=0.331, anchor="center")


def load_playlist():
    global p_list
    global p_data

    def can_():
        p_list.destroy()
        sel.destroy()
        can.destroy()
        del1.destroy()

    def del_p():
        z = pl_data[p_list.curselection()[0]][0]
        f = open("user_playlist.csv", "r")
        data = []
        reader1 = csv.reader(f)
        for i in reader1:
            l = []
            try:
                a = i[0]
                if z == a:
                    pass
                else:
                    l.append(i[0])
                    l.append(eval(i[1]))
                    data.append(l)
            except:
                pass
        f.close()
        f = open("user_playlist.csv", "w")
        writer = csv.writer(f)
        writer.writerows(data)
        f.close()
        can_()
        load_playlist()

    def sel_():
        def can_p():
            p_list1.destroy()
            sel1.destroy()
            can1.destroy()
            add1.destroy()

        def sel_p():
            global curr_se
            global user_play
            global playing
            global dur
            global dur_need
            global song_pointer
            global song_len
            global playing_playlist
            user_play = True
            playing = True
            curr_se = p_data[1]
            playing_playlist = False
            try:
                pygame.mixer.music.load(curr_se[p_list1.curselection()[0]])
                audio = MP3(curr_se[p_list1.curselection()[0]])
                song_pointer = curr_se[p_list1.curselection()[0]].split("/")[-1]
            except:
                audio = MP3(curr_se[0])
                pygame.mixer.music.load(curr_se[0])
                song_pointer = curr_se[0].split("/")[-1]
            dur = 0
            status.config(text=song_pointer)
            song_len = audio.info.length
            dur_scale.config(state="active", from_=0, to=song_len)
            dur_need = True
            chk_play()
            pygame.mixer.music.play()
            try:
                thread_dur.start()
            except:
                pass
            can_p()

        def add_p():
            pat = filedialog.askopenfile()
            p_data[1].append(pat.name)
            p_list1.insert(len(p_data[1]) - 1, pat.name.split("/")[-1])
            f = open("user_playlist.csv", "r")
            data = []
            reader1 = csv.reader(f)
            for i in reader1:
                l = []
                try:
                    a = i[0]
                    if p_data[0] == a:
                        l.append(i[0])
                        j = eval(i[1])
                        j.append(pat.name)
                        l.append(j)
                    else:
                        l.append(i[0])
                        l.append(eval(i[1]))
                    data.append(l)
                except:
                    pass
            f.close()
            f = open("user_playlist.csv", "w")
            writer = csv.writer(f)
            writer.writerows(data)
            f.close()

        l = []
        playlist_no = p_list.curselection()[0]
        l.append(pl_data[playlist_no][0])
        l.append(eval(pl_data[playlist_no][1]))
        p_data = l
        p_list.destroy()
        sel.destroy()
        can.destroy()
        del1.destroy()
        p_list1 = tk.Listbox(wn, bg="white", bd=3, cursor="arrow", fg="red", relief="groove", xscrollcommand=True,
                             yscrollcommand=True, width=40)
        p_list1.place(relx=0, rely=0, relheight=0.4)
        for i in range(len(p_data[1])):
            p_list1.insert(i, p_data[1][i].split("/")[-1])
        sel1 = tk.Button(wn, text="Play", command=sel_p)
        sel1.place(relx=0.32, rely=0.35, anchor="w")
        can1 = tk.Button(wn, text="Cancel", command=can_p)
        can1.place(relx=0.32, rely=0.25, anchor="w")
        add1 = tk.Button(wn, text="Add Song", command=add_p)
        add1.place(relx=0.32, rely=0.3, anchor="w")

    f = open("user_playlist.csv", "r")
    pl_data = []
    reader = csv.reader(f)
    for r in reader:
        try:
            a = r[0]
            pl_data.append(r)
        except:
            pass

    f.close()
    p_list = tk.Listbox(wn, bg="white", bd=3, cursor="arrow", fg="red", relief="groove", xscrollcommand=True,
                        yscrollcommand=True, width=40)
    p_list.place(relx=0, rely=0, relheight=0.4)
    for i in range(len(pl_data)):
        p_list.insert(i, pl_data[i][0])
    sel = tk.Button(wn, text="Select", command=sel_)
    sel.place(relx=0.32, rely=0.35, anchor="w")
    can = tk.Button(wn, text="Cancel", command=can_)
    can.place(relx=0.32, rely=0.25, anchor="w")
    del1 = tk.Button(wn, text="Delete Playlist", command=del_p)
    del1.place(relx=0.32, rely=0.3, anchor="w")


def open_url():
    def download_play(url, s):
        global curr_se
        global not_down
        global down
        r = pafy.new(url)
        print(r.title)
        t = r.title
        t = t.replace("/", "_")
        t = t.replace("|", "")
        path = "downloads/" + t + ".m4a"
        op = "downloads/" + t + ".mp3"
        a = r.getbestaudio("m4a")
        print(a)
        a.download(filepath=path)
        print("downloaded")
        subprocess.call(['ffmpeg', '-i', path, op])
        if s == "load":
            not_down.append(op)
        else:
            down.append(op)
        try:
            remove(path)
        except:
            print("remove error")
        curr_se.append(op)
        open_url.status.destroy()

    def Cancel():
        l.destroy()
        url_s.destroy()
        load_btn.destroy()
        del_btn.destroy()
        down_load.destroy()

    def start_t(s):
        print("a")
        url = url_s.get()
        d_thread = threading.Thread(target=lambda: download_play(url, s))
        d_thread.start()
        open_url.status = tk.Label(wn, text="Loading song into Current Playlist")
        Cancel()
        open_url.status.place(relx=0.5, rely=0.5, anchor="center")

    l = tk.Label(wn, text="Paste URL", font=("Courier", 13, "normal"))
    url_s = tk.Entry(wn, font=("Arial", 10, "normal"), fg="purple")
    load_btn = tk.Button(wn, text="Load", command=lambda: start_t("load"))
    down_load = tk.Button(wn, text="Download_&_Load", command=lambda: start_t("download"))
    del_btn = tk.Button(wn, text="Cancel", command=Cancel)
    l.place(relx=0.5, rely=0.45, anchor="center")
    url_s.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5)
    load_btn.place(relx=0.38, rely=0.55, anchor="center")
    down_load.place(relx=0.5, rely=0.55, anchor="center")
    del_btn.place(relx=0.62, rely=0.55, anchor="center")


def import_playlist():
    def download_song(r,title):
        global busy
        busy = True
        print(r.title)
        t = r.title
        t = t.replace("/", " ")
        path ="downloads/"+title + "/" + t + ".m4a"
        op ="downloads/" + title + "/" + t + ".mp3"
        a = r.getbestaudio("m4a")
        print(a)
        a.download(filepath=path)
        print("downloaded")
        subprocess.call(['ffmpeg', '-i', path, op])
        remove(path)
        busy = False
    def Cancel():
        l.destroy()
        url_s.destroy()
        load_btn.destroy()
        del_btn.destroy()

    def i_p():
        u=url_s.get()
        pyt = pafy.get_playlist(u)
        Cancel()
        def remove_n():
            n = new_playlist.curselection()[0]
            new_playlist.delete(n)
            import_playlist.data.pop(n)
            pyt["items"].pop(n-1)

        def done_():
            a = list_name.get()
            import_playlist.data[0]=a
            print(len(import_playlist.data))
            print(import_playlist.data)
            try:
                mkdir("downloads/" + import_playlist.data[0])
            except:
                pass
            cancel_()
            i_p_status.place(relx=0.5,rely=0.5,anchor="center")
            i_p_status.config(text="Loading Playlist 0/"+str(len(import_playlist.data)-1))
            f=0
            global busy
            print(pyt["items"])
            for i in pyt["items"][:len(import_playlist.data)-1]:
                while busy:
                    time.sleep(0.09)
                else:
                    print(i["pafy"])
                    print(f, i["pafy"].title)
                    download_song(i["pafy"],import_playlist.data[0])
                    f += 1
                    i_p_status.config(text="Loading Playlist "+str(f)+"/"+str(len(import_playlist.data)-1))
                    curr_se.append(import_playlist.data[f])
            i_p_status.destroy()

            f = open("user_playlist.csv", "a")
            writer = csv.writer(f)
            l=[]
            l.append(import_playlist.data[0])
            l.append(import_playlist.data[1:])
            writer.writerow(l)
            f.close()

            def x():
                lab.destroy()
                button.destroy()

            lab = tk.Label(wn, text="Playlist Added", font=("Arial", 15, "normal"), fg="purple")
            button = tk.Button(wn, text="OK", command=x)
            lab.place(relx=0.5, rely=0.48, anchor="center")
            button.place(relx=0.5, rely=0.54, anchor="center")

        def cancel_():
            done.destroy()
            remove_.destroy()
            list_name.destroy()
            new_playlist.destroy()
            cancel.destroy()
        def start_thread():
            s=threading.Thread(target=done_)
            s.start()

        new_playlist = tk.Listbox(wn, bg="white", bd=3, cursor="arrow", fg="red", relief="groove", xscrollcommand=True,
                                  yscrollcommand=True, width=60)
        new_playlist.place(relx=0.5, rely=0.5, anchor="center")
        done = tk.Button(wn, text="Load Playlist", command=start_thread)
        remove_ = tk.Button(wn, text="Remove", command=remove_n)
        done.place(relx=0.54, rely=0.68, anchor="center")
        remove_.place(relx=0.45, rely=0.68, anchor="center")
        cancel = tk.Button(wn, text="Cancel", command=cancel_)
        cancel.place(relx=0.5, rely=0.29, anchor="center")
        list_name = tk.Entry(wn, font=("Arial", 13, "normal"), fg="purple")
        list_name.insert(0,pyt["title"])
        list_name.place(relx=0.5, rely=0.331, anchor="center",relwidth=0.4)
        i_p_status=tk.Label(wn,text="",fg="red")

        import_playlist.data = []
        import_playlist.data.append(list_name.get())

        print(pyt["title"])
        print(len(pyt["items"]))

        c = 1
        for i in pyt["items"]:
            path_ = "downloads/" + import_playlist.data[0] + "/" + i["pafy"].title + ".mp3"
            new_playlist.insert(c, i["pafy"].title + ".mp3")
            c += 1
            import_playlist.data.append(path_)
            if c==20:
                break



    s = []
    f = 0
    l = tk.Label(wn, text="Paste URL Of Playlist", font=("Courier", 13, "normal"))
    url_s = tk.Entry(wn, font=("Arial", 10, "normal"), fg="purple")
    load_btn = tk.Button(wn, text="Import Playlist", command=lambda: i_p())
    del_btn = tk.Button(wn, text="Cancel", command=Cancel)
    l.place(relx=0.5, rely=0.45, anchor="center")
    url_s.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5)
    load_btn.place(relx=0.38, rely=0.55, anchor="center")
    del_btn.place(relx=0.62, rely=0.55, anchor="center")



wn = tk.Tk()
wn.title("Pied piper")
wn.geometry("800x600")
wn.resizable(0, 0)
background_image = tk.PhotoImage(file="background.png")
background_label = tk.Label(wn, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
menu = tk.Menu(wn)
submenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=submenu)
submenu.add_command(label="Open File", command=browse)
submenu.add_command(label="Youtube URL", command=open_url)
submenu.add_command(label="Exit", command=exit)
submenu1 = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Playlist", menu=submenu1)
submenu1.add_command(label="Create playlist", command=create_playlist)
submenu1.add_command(label="Load playlist", command=load_playlist)
submenu1.add_command(label="Import Youtube Playlist", command=import_playlist)
wn.config(menu=menu)

play = tk.PhotoImage(file="play.png")
play_btn = tk.Button(wn, image=play, command=play_)
pause = tk.PhotoImage(file="pause.png")
stop = tk.PhotoImage(file="stop.png")
stop_btn = tk.Button(wn, image=stop, command=stop_)
playlist = tk.PhotoImage(file="playlist.png")
playlist_btn = tk.Button(wn, image=playlist, command=show_playlist)
add_song = tk.PhotoImage(file="add_song.png")
add_song_btn = tk.Button(wn, image=add_song, command=processing)
sound = tk.PhotoImage(file="sound.png")
mute_img = tk.PhotoImage(file="mute.png")
sound_btn = tk.Button(wn, image=sound, command=mute_unmute)
default = tk.PhotoImage(file="default.png")
default_btn = tk.Button(wn, image=default, command=show_default)
scale = tk.Scale(wn, from_=0, to=100, activebackground="silver", bg="silver", sliderlength=10, command=set_vol, width=7)
scale.set(70)
forward = tk.PhotoImage(file="forward.png")
backward = tk.PhotoImage(file="backward.png")
forward_btn = tk.Button(wn, image=forward, command=forward_)
backward_btn = tk.Button(wn, image=backward, command=backward_)
status = tk.Label(wn, text="NO PLAYING MEDIA", font=("Arial", 10, "normal"), fg="Blue")
dur_scale = tk.Scale(wn, from_=0, to=100, activebackground="blue", bg="silver", sliderlength=10, orient="horizontal",
                     width=8, state="disabled", command=dur_val)
loop = tk.PhotoImage(file="loop.png")
normal = tk.PhotoImage(file="no_shuffle.png")
shuffle = tk.PhotoImage(file="shuffle.png")
playback = tk.Button(wn, image=normal, command=playback_)
next = tk.PhotoImage(file="next.png")
previous = tk.PhotoImage(file="previous.png")
next_btn = tk.Button(wn, image=next, command=lambda: queue(i="n"))
previous_btn = tk.Button(wn, image=previous, command=lambda: queue(i="p"))
playback_state = "normal"

previous_btn.place(relx=0.03, rely=0.5, anchor="center")
next_btn.place(relx=0.97, rely=0.5, anchor="center")
playback.place(relx=0.185, rely=0.92, anchor="center")
dur_scale.place(relx=0.01, rely=0.82, relwidth=0.93, anchor="w")
play_btn.place(relx=0.392, rely=0.92, anchor="center")
stop_btn.place(relx=0.6, rely=0.92, anchor="center")
playlist_btn.place(relx=0.7, rely=0.92, anchor="center")
add_song_btn.place(relx=0.8, rely=0.92, anchor="center")
sound_btn.place(relx=0.9, rely=0.92, anchor="center")
default_btn.place(relx=0.03, rely=0.92, anchor="w")
scale.place(relx=0.974, rely=0.888, anchor="center")
forward_btn.place(relx=0.5, rely=0.92, anchor="center")
backward_btn.place(relx=0.285, rely=0.92, anchor="center")
status.place(relx=0.5, rely=0.75, anchor="center")
thread_dur = threading.Thread(target=duration_control)
bck = []
bck.append(background_image)
for i in range(1, 10):
    t = "bck" + str(i) + ".png"
    bck.append(tk.PhotoImage(file=t))


def bk():
    global bck
    s_t = time.perf_counter()
    while True:
        p_t = time.perf_counter()
        if p_t - s_t >= random.randrange(35, 45):
            background_label.config(image=bck[random.randrange(0, len(bck))])
            s_t = time.perf_counter()


try:
    mkdir("downloads")
except:
    pass
bk_thread = threading.Thread(target=bk)
bk_thread.start()
wn.protocol("WM_DELETE_WINDOW", exit)
wn.mainloop()
