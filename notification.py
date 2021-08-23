# -*-coding=utf-8-*-
__author__ = 'conglinfeng'


# 通知栏消息
class Notification(object):

    def __init__(self):
        self.isWindowsSystem = False
        import platform
        if platform.system() == 'Windows':
            self.isWindowsSystem = True

    def show(self, title, content, sound_name="Glass"):
        '''
        sound_name: 仅Mac有效。声音文件都在 ~/Library/Sounds /System/Library/Sounds
        '''

        if self.isWindowsSystem:
            self._showOnWin10(title, content)
        else:
            self._showOnMac(title, content, sound_name)

    def _showOnMac(self, title, content, sound_name="Glass"):
        '''
        Mac 通知栏消息
        sound_name: 声音文件都在 ~/Library/Sounds /System/Library/Sounds
        '''

        cmd = f'display notification \"{content}\"'
        if title:
            cmd = cmd + f' with title \"{title}\"'
        if sound_name:
            cmd = cmd + f' sound name \"{sound_name}\"'
        call(["osascript", "-e", cmd])

    def _showOnWin10(self, title, content):
        '''
        Win10 通知栏消息
        '''

        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, content)
