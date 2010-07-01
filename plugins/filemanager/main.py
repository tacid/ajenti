from ajenti.ui import *
from ajenti.com import implements
from ajenti.app.api import ICategoryProvider
from ajenti.app.helpers import *

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.formatters import HtmlFormatter

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
        self._viewfile = None
        self._filename = None

    def get_ui(self):
        panel = UI.PluginPanel(UI.Label(text=''), title='File Manager', icon='/dl/filemanager/icon.png')
        if self._viewfile is not None:
            data = self._viewfile.get_content(self._filename)
            if data is None:
                panel.appendChild(UI.ErrorBox(title='Error open file "'+self._filename+'"', text='Sorry...'))
            else:
                #try:
                #    lexer = get_lexer_for_filename(self._filename)
                #except:
                #    lexer = TextLexer()
                #formatter = HtmlFormatter(linenos=True, cssclass="source")
                #print formatter.get_style_defs(arg='')
                panel.appendChild(
                        UI.VContainer(
                            UI.LinkLabel(text="Back to File Manager", id="close_fileview"),
                            UI.TextInputArea(
                                        #text=highlight(data, lexer, formatter),
                                        text=data.replace("\n", "[br]"),
                                        width="600",
                                        height="600",
                                        name="code"
                                    )
                            )
                        )
        else:
            mainTable = UI.LayoutTable(
                            UI.LayoutTableRow(
                                UI.LayoutTableCell(self.build_panel(self._left_fs, 'left'), width="50%"),
                                UI.LayoutTableCell(self.build_panel(self._right_fs, 'right'), width="50%")
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
        elif params[0] == "left_viewfile":
            name = vars.getvalue('filename', None)
            if name is not None:
                self._viewfile= self._left_fs
                self._filename = name                
        elif params[0] == "right_viewfile":
            name = vars.getvalue('filename', None)
            if name is not None:
                self._viewfile= self._right_fs
                self._filename = name
        elif params[0] == "close_fileview":
            self._viewfile = None
        

    def build_panel(self, fs, id):
        pathSelect = UI.HContainer()
        for p in fs.split_path():
            pathSelect.appendChild(
                    UI.LinkLabel(text=p[0]+" > ", id=id+"_chdir/?folder="+p[1]) if p[1] is not None else UI.Label(text=p[0])
                )
        freeSpace = UI.Label(text="Free "+pretty_size_view(fs.free_space())+" of "+pretty_size_view(fs.total_space()) )
        table = UI.DataTable(
                    UI.DataTableRow(
                            UI.Label(text=" "),
                            UI.Label(text="Name", bold=True),
                            UI.Label(text="Size", bold=True),
                            UI.Label(text="Perms", bold=True),
                            UI.Label(text="Owner/Group", bold=True),
                            UI.Label(text="Actions", bold=True),
                            header=1
                        ),
                    width="100%"
                )
        folders = fs.get_folders()
        for folder in sorted(folders.keys()):
            table.appendChild(
                    UI.DataTableRow(
                            UI.CheckBox(name=id+'+file[]') if folders[folder]['name'] != '..' else UI.DataTableCell(),
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
                            UI.DataTableCell(UI.LinkLabel(text='['+files[file]['name']+']', id=id+"_viewfile/?filename="+files[file]['name'])
                                        ),
                            UI.Label(text=files[file]['size']),
                            UI.Label(text=files[file]['perms']),
                            UI.Label(text=files[file]['owner']+'/'+files[file]['group']),
                            UI.Label(text='info')
                        )
                )
        return UI.VContainer(freeSpace, pathSelect, table, width="100%")


class FileManagerContent(ModuleContent):
    module = 'filemanager'
    path = __file__
