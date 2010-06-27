from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

from api import *


class FileManagerPlugin(CategoryPlugin):
    implements((ICategoryProvider, 120))

    text = 'FileManager'
    icon = '/dl/filemanager/icon.png'
    
    def on_init(self):
        pass

    def on_session_start(self):
        self._left_fs = LocalFS()
        self._right_fs = LocalFS()
        self._show_hidden = True

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=''), title='File Manager', icon='/dl/filemanager/icon.png')
        mainTable = UI.LayoutTable(
                        UI.LayoutTableRow(
                            UI.LayoutTableCell(self.build_panel(self._left_fs, 'left')),
                            UI.LayoutTableCell(self.build_panel(self._right_fs, 'right'))
                        )
                )
        panel.appendChild(mainTable)
        return panel

    @event('linklabel/click')
    def on_click(self, event, params, vars=None):
        print params
        print vars
        if params[0] == "left_chdir":
            self._left_fs.chdir(vars.getvalue('folder', None))
        elif params[0] == "right_chdir":
            self._right_fs.chdir(vars.getvalue('folder', None))
        elif params[0] == "right_up":
            self._right_fs.up()
        elif params[0] == "left_up":
            self._left_fs.up()
        

    def build_panel(self, fs, id):
        pathSelect = UI.HContainer()
        for p in fs.split_path():
            pathSelect.appendChild(
                    UI.LinkLabel(text=p[0]+" > ", id=id+"_chdir/?folder="+p[1]) if p[1] is not None else UI.Label(text=p[0])
                )
        freeSpace = UI.Label(text="Free "+pretty_size_view(fs.free_space())+" of "+pretty_size_view(fs.total_space()) )
        table = UI.DataTable(
                    UI.DataTableRow(
                            UI.Label(text="A"),
                            UI.Label(text="Name", bold=True),
                            UI.Label(text="Size", bold=True),
                            UI.Label(text="Perms", bold=True),
                            UI.Label(text="Owner/Group", bold=True),
                            UI.Label(text="Actions", bold=True),
                            header=1
                        )
                )
        folders = fs.get_folders()
        for folder in sorted(folders.keys()):
            table.appendChild(
                    UI.DataTableRow(
                            UI.CheckBox(name=id+'+file[]'),
                            UI.DataTableCell(UI.Image(file="/dl/filemanager/"+ ("folder.png"  if folders[folder]['name'] != '..' else 'up.png')),
                                             UI.LinkLabel(text='['+folders[folder]['name']+']' if folders[folder]['name'] != '..' else '[up]',
                                                          id=(id+"_chdir/?folder="+folder) if folders[folder]['name'] != '..' else id+'_up')
                                        ),
                            UI.Label(text='DIR'),
                            UI.Label(text=folders[folder]['perms']),
                            UI.Label(text=folders[folder]['owner']+'/'+folders[folder]['group']),
                            UI.Label(text="Info")
                        )
                )
        files = fs.get_files()
        for file in sorted(files.keys()):
            table.appendChild(
                    UI.DataTableRow(
                            UI.CheckBox(name=id),
                            UI.DataTableCell(UI.LinkLabel(text='['+files[file]['name']+']', id=id+"_showfile/"+files[file]['name']+"?abc=1")
                                        ),
                            UI.Label(text=files[file]['size']),
                            UI.Label(text=files[file]['perms']),
                            UI.Label(text=files[file]['owner']+'/'+files[file]['group']),
                            UI.Label(text='info')
                        )
                )
        return UI.VContainer(freeSpace, pathSelect, table)


class FileManagerContent(ModuleContent):
    module = 'filemanager'
    path = __file__
