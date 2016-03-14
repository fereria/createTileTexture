# -*- coding: utf-8 -*-
"""
v1.0 リリース版
v1.1 画像の大きさが違う場合でも結合できるようにしました
"""
import sys
import re
import os.path

from PIL import Image
from PySide import QtCore, QtGui

import ui.main_ui as main_ui


def joinTexture(savePath, joinTextureList, row, column=None, alpha=False, resize=None):
    """
    テクスチャをタイル上に並べる
    """
    if len(joinTextureList) != 0:
        if column is None:
            column = int(len(joinTextureList) / row)
        buff = Image.open(joinTextureList[0], 'r')
        if resize is not None:
            texture_X = int(resize[0] / row)
            texture_Y = int(resize[1] / column)
        else:
            texture_X = buff.size[0]
            texture_Y = buff.size[1]

        if alpha is True:
            saveImg = Image.new('RGBA', (texture_X * row, texture_Y * column), (0, 0, 0, 0))
        else:
            saveImg = Image.new('RGB', (texture_X * row, texture_Y * column), (0, 0, 0))
        # 画像を結合
        num = 0
        for tex in joinTextureList:
            x = num % row
            y = int(num / row)
            buff = Image.open(tex, 'r')
            if resize is not None:
                buff = buff.resize((texture_X, texture_Y))
            if alpha is True and buff.mode == "RGBA":
                saveImg.paste(buff, (x * texture_X, y * texture_Y))
            else:
                saveImg.paste(buff, (x * texture_X, y * texture_Y))
            num += 1
        ext = os.path.splitext(savePath)[1]

        if resize is not None:
            saveImg = saveImg.resize(resize)

        # jpgの場合は、高品位にする
        if ext.lower() == ".jpg" or ext.lower() == ".jpeg":
            saveImg.save(savePath, 'JPEG', quality=100, optimize=True)
        else:
            saveImg.save(savePath, re.sub("\.", "", ext.lower()))


class MainUI(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(u"タイルテクスチャ作成くん v1.1")

        self.setAcceptDrops(True)

        self.model = QtGui.QStringListModel()
        self.ui.textureList.setModel(self.model)
        self.ui.textureList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.ui.textureList.customContextMenuRequested.connect(self.contextMenu)
        self.ui.createBtn.clicked.connect(self.saveBtn)

        self.ui.checkBox.clicked.connect(self.resizeClicked)

    def resizeClicked(self):

        self.ui.resize_w.setEnabled(self.ui.checkBox.isChecked())
        self.ui.resize_h.setEnabled(self.ui.checkBox.isChecked())

    def contextMenu(self, pos):

        menu = QtGui.QMenu(self.ui.textureList)
        m = menu.addAction(u"選択しているファイルを削除")
        actionlist = []
        action = menu.exec_(self.ui.textureList.mapToGlobal(pos))
        actionlist.append(action)
        if m == action:
            self.deleteSelectList()

    def deleteSelectList(self):

        clicked = [i.data() for i in self.ui.textureList.selectedIndexes()]
        now_list = self.model.stringList()
        for i in clicked:
            now_list.remove(i)
        self.model.setStringList(now_list)

    def dropEvent(self, event):

        mimedata = event.mimeData()
        img_exp = [".png", ".bmp", ".tga", ".jpg", ".jpeg",
                   ".JPG", ".PNG", ".TGA", ".JPEG", ".BMP"]
        urllist = [re.sub("^/", "", x.path()) for x in mimedata.urls() if os.path.splitext(x.path())[1] in img_exp]
        urllist.sort()
        set_path = urllist + self.model.stringList()

        self.model.setStringList(set_path)

    def dragEnterEvent(self, event):

        mime = event.mimeData()
        if mime.hasUrls() is True:
            event.accept()
        else:
            event.ignore()

    def saveBtn(self):

        save_file = QtGui.QFileDialog.getSaveFileName(self, filter="PNG(*.png);;BMP(*.bmp);;JPG(*.jpg);;TGA(*.tga);;")
        resize = None
        if self.ui.checkBox.isChecked() is True:
            resize = (self.ui.resize_w.value(), self.ui.resize_h.value())
        joinTexture(save_file[0],
                    self.model.stringList(),
                    self.ui.tileNum.value(),
                    self.ui.tileNumB.value(),
                    self.ui.addAlpha.isChecked(),
                    resize)


def main():

    sys.setrecursionlimit(100000)

    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForLocale())
    win = MainUI()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':

    main()
