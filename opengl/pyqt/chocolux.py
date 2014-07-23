# PyQT/OpenGL example
# shaders from here: http://www.iquilezles.org/www/material/nvscene2008/rwwtt.pdf
#
# Author: Peter Bouda, http://www.peterbouda.eu

import time

from PyQt5.QtMultimedia import *
from PyQt5 import QtCore, QtGui, QtWidgets


class OpenGLWindow(QtGui.QWindow):
    def __init__(self, parent=None):
        super(OpenGLWindow, self).__init__(parent)

        self.m_update_pending = False
        self.m_animating = False
        self.m_context = None
        self.m_gl = None

        self.setSurfaceType(QtGui.QWindow.OpenGLSurface)

    def initialize(self):
        pass

    def setAnimating(self, animating):
        self.m_animating = animating

        if animating:
            self.renderLater()

    def renderLater(self):
        if not self.m_update_pending:
            self.m_update_pending = True
            QtGui.QGuiApplication.postEvent(self, QtCore.QEvent(QtCore.QEvent.UpdateRequest))

    def renderNow(self):
        if not self.isExposed():
            return

        self.m_update_pending = False

        needsInitialize = False

        if self.m_context is None:
            self.m_context = QtGui.QOpenGLContext(self)
            self.m_context.setFormat(self.requestedFormat())
            self.m_context.create()

            needsInitialize = True

        self.m_context.makeCurrent(self)

        if needsInitialize:
            version = QtGui.QOpenGLVersionProfile()
            version.setVersion(2, 0)
            self.m_gl = self.m_context.versionFunctions(version)
            self.m_gl.initializeOpenGLFunctions()

            self.initialize()

        self.render(self.m_gl)

        self.m_context.swapBuffers(self)

        if self.m_animating:
            self.renderLater()

    def event(self, event):
        if event.type() == QtCore.QEvent.UpdateRequest:
            self.renderNow()
            return True

        return super(OpenGLWindow, self).event(event)

    def exposeEvent(self, event):
        self.renderNow()

    def resizeEvent(self, event):
        self.renderNow()


class ChocoWindow(OpenGLWindow):
    
    vertexShaderSource = '''
varying vec3 s[4];

void main() {
    gl_Position=gl_Vertex;
    s[0]=vec3(0);
    s[3]=vec3(sin(abs(gl_Vertex.x*.0001)),
        cos(abs(gl_Vertex.x*.0001)),0);
    s[1]=s[3].zxy;
    s[2]=s[3].zzx;
}
'''

    fragmentShaderSource = '''
varying vec3 s[4];

void main() {
    float t,b,c,h=0.0;
    vec3 m,n,p=vec3(.2),d=normalize(.001*gl_FragCoord.rgb-p);
    for(int i=0;i<4;i++) {
        t=2.0;
        for(int i=0; i<4; i++) {
            b=dot(d,n=s[i]-p);
            c=b*b+.2-dot(n,n);
            if ((b-c)<t)
                if (c>0.0) {
                    m=s[i];
                    t=b-c;
                }
        }
        p+=t*d;
        d=reflect(d,n=normalize(p-m));
        h+=pow(n.x*n.x,44.)+n.x*n.x*.2;
    }
    gl_FragColor=vec4(h,h*h,h*h*h*h,h);
}
'''

    def __init__(self, parent=None):
        super(ChocoWindow, self).__init__(parent)

    def initialize(self):
        self.program = QtGui.QOpenGLShaderProgram(self)

        self.program.addShaderFromSourceCode(QtGui.QOpenGLShader.Vertex,
                self.vertexShaderSource)
        self.program.addShaderFromSourceCode(QtGui.QOpenGLShader.Fragment,
                self.fragmentShaderSource)

        self.program.link()

        #self.sAttr = self.program.attributeLocation('s')

    def render(self, gl):
        gl.glViewport(0, 0, self.width(), self.height())
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        self.program.bind()

        t = int(time.clock()*10000)
        gl.glRecti(t, t, -t, -t)

        self.program.release()


if __name__ == '__main__':
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    
    format = QtGui.QSurfaceFormat()
    format.setSamples(4)

    window = ChocoWindow()
    window.setFormat(format)
    window.resize(640, 480)
    window.show()

    window.setAnimating(True)

    sys.exit(app.exec_())