# -*-coding=utf-8-*-
__author__ = 'conglinfeng'

from subprocess import call


# Mac通知栏消息
class Notification(object):

    def show(self, title, content, sound_name="Glass"):
        '''
        sound_name: 声音文件都在 ~/Library/Sounds /System/Library/Sounds
        '''

        cmd = f'display notification \"{content}\"'
        if title:
            cmd = cmd + f' with title \"{title}\"'
        if sound_name:
            cmd = cmd + f' sound name \"{sound_name}\"'
        call(["osascript", "-e", cmd])
