from svg.path import *

class Text:
    def __init__(self, texte="", size="12pt", x=0, y=0, rotate=0, textAnchor="middle"):
        """
        Le constructeur
        """
        self.texte=texte
        self.size=size
        self.x=x
        self.y=y
        if rotate==90:
            self.writingMode="tb"
        else:
            self.writingMode="inherit"
        self.textAnchor=textAnchor
        
    def toSvg(self):
        """
        @return le code d'un élément SVG de type text
        """
        return """
  <text x="{x}" y="{y}" style="font-size: {size};text-anchor: {textAnchor}; writing-mode: {writingMode};">
        {texte}
  </text>
""".format(**self.__dict__)
    
def toSvgFile(filename, paths):
    """
    fait un fichier SVG à partir d'un chemin
    @param filename un nom de fichier
    @param paths une liste de chemins ou chemins spéciaux
    """
    with open(filename,"w") as out:
        out.write(toSvg(paths))
    return

def toSvg(paths):
    """
    fait un code SVG à partir d'un chemin
    @param paths une liste de chemins ou chemins spéciaux ; un chemin
    spécial est un tuple (chemin, attribut) où attribut est "pointille" ou
    "hachure"...
    @return une chaîne de caractères
    """
    pathTemplate="""
  <path
      style="{}"
      d="{}" />"""
    result="""\
<?xml version="1.0" encoding="UTF-8"?>
<svg
   width="210mm"
   height="297mm"
   viewBox="0 0 210 297"
   >
  <defs>
    <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" x="0" y="0" width="4" height="4">
      <path d="M0,4 l4,-4" style="stroke: black; stroke-width:0.15px; fill: none;" />
    </pattern>
  </defs>

"""
    style=""
    for p in paths:
        if isinstance(p, Path):
            style="fill:none;stroke:#000000;stroke-width:0.3px;"
            result+=pathTemplate.format(style,p.d())
        elif isinstance(p, (list,tuple)) and isinstance(p[0],Path) and len(p)>1:
            if p[1]=="tiret":
                style="fill:none;stroke:#000000;stroke-width:0.3px;stroke-dasharray:2.2,0.8;"
            if p[1]=="pointille":
                style="fill:none;stroke:#000000;stroke-width:0.3px;stroke-dasharray:0.5,1.5;"
            elif p[1]=="hachure":
                style="stroke:#000000;stroke-width:0px;fill:url(#diagonalHatch);"
            else:
                style="fill:none;stroke:#000000;stroke-width:0.3px;"
            result+=pathTemplate.format(style,p[0].d())
        elif isinstance(p, Text):
            result+=p.toSvg()
    ### fin du fichier SVG
    result+="""
</svg>
"""
    return result


    
