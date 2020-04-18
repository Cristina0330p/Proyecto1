import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure

from PyQt5.uic import loadUi

from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io as sio
import numpy as np
from Modelo import Biosenal
# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
        
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        
    #este metodo me grafica al senal senoidal 
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
    #hay que crear un metodo para graficar lo que quiera
    def graficar_gatos(self,datos):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.plot(datos)
        #y lo graficamos
        print("datos")
        print(datos)
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:]+c*10)
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()

        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    senales=[] 
    canalLoaded=''
    senalLoaded=[]
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('anadir_grafico.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite aÃ±adir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        layout2 = QVBoxLayout()
        #se aÃ±ade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        self.campo_grafico2.setLayout(layout2)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        self.__sc2 = MyGraphCanvas(self.campo_grafico2, width=5, height=4, dpi=100)
        #se aÃ±ade el campo de graficos
        layout.addWidget(self.__sc)
        layout2.addWidget(self.__sc2)
        
        #se organizan las seÃ±ales 
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_aumentar.clicked.connect(self.aumentar_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal)   
        self.loadCanal.clicked.connect(self.cargar_senal)
        self.filtrar.clicked.connect(self.filtrar_senal)
        #hay botones que no deberian estar habilitados si no he cargado la senal
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.canal.setEnabled(False)
        self.loadCanal.setEnabled(False)
        self.filtrado_tipo.setEnabled(False)
        self.filtrar.setEnabled(False)
        #cuando cargue la senal debo volver a habilitarlos
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
    def adelante_senal(self):
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def atrasar_senal(self):
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def aumentar_senal(self):
        #en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
        #extraigo por fuera mi funcion de grafico puede leer los valores
        self.__sc.graficar_gatos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,2))
    def disminuir_senal(self):
        self.__sc.graficar_gatos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,0.5))
    
        
    def energy(signal):
        energy = np.sum(np.power(signal,2),0);
        return energy;    
    
    def filtrar_senal(self):
        #Codigo de umbral para wavelet para el filtrado de la señal cargada, para quitar datos dejar la señal mas limpia. 
        wavelet_inv = [1/np.sqrt(2) , -1/np.sqrt(2)];
        scale_inv = [1/np.sqrt(2) , 1/np.sqrt(2)];
        scale = [1/np.sqrt(2) , 1/np.sqrt(2)];
        wavelet = [-1/np.sqrt(2) , 1/np.sqrt(2)];
        signal= np.squeeze(self.senalLoaded)
        
        longitud_original=signal.shape[0]
        
        signal_descomp=signal
        if (signal_descomp.shape[0] % 2) != 0:
            print("Anadiendo ceros");
            signal_descomp = np.append(signal_descomp, 0);
        Aprox = np.convolve(signal_descomp,scale,'full');
        Aprox = Aprox[1::2];
        
        Detail = np.convolve(signal_descomp,wavelet,'full');
        Detail = Detail[1::2];
        signal_descomp = Aprox;
        if (signal_descomp.shape[0] % 2) != 0:
            print("Anadiendo ceros");
            signal_descomp = np.append(signal_descomp, 0);
        Aprox2 = np.convolve(signal_descomp,scale,'full');
        Aprox2 = Aprox2[1::2];
        Detail2 = np.convolve(signal_descomp,wavelet,'full');
        Detail2 = Detail2[1::2];
        signal_descomp = Aprox2;
        if (signal_descomp.shape[0] % 2) != 0:
            print("Anadiendo ceros");
            signal_descomp = np.append(signal_descomp, 0);
        Aprox3 = np.convolve(signal_descomp,scale,'full');
        Aprox3 = Aprox3[1::2];
        Detail3 = np.convolve(signal_descomp,wavelet,'full');
        Detail3 = Detail3[1::2];
        
        Num_samples = Aprox3.shape[0] +  Detail3.shape[0] + Detail2.shape[0] + Detail.shape[0]
        #hr = np.sqrt(2*(np.log(Num_samples)))
        thr=0.3936 + 0.1829*((np.log(Num_samples))/np.log(2))
        
        stdc = np.zeros((4,1));

        stdc[1] = (np.median(np.absolute(Detail3)))/0.6745;
        stdc[2] = (np.median(np.absolute(Detail2)))/0.6745;
        stdc[3] = (np.median(np.absolute(Detail)))/0.6745;
        
        npoints_aprox = Aprox3.shape[0];
        Aprox_inv3 = np.zeros((2*npoints_aprox));
        Aprox_inv3[0::2] = Aprox3;
        Aprox_inv3[1::2] = 0;

        APROX3 = np.convolve(Aprox_inv3,scale_inv,'full');

        npoints_aprox = Detail3.shape[0];
        Detail_inv3 = np.zeros((2*npoints_aprox));
        Detail_inv3[0::2] = Detail3;
        Detail_inv3[1::2] = 0;

        DETAIL3 = np.convolve(Detail_inv3,wavelet_inv,'full');

        X3 = APROX3 + DETAIL3;
        
        if X3.shape[0] > Detail2.shape[0]:
            print("Quitando ceros");
            X3 = X3[0:Detail2.shape[0]];

        npoints_aprox = X3.shape[0];
        Aprox_inv2 = np.zeros((2*npoints_aprox));
        Aprox_inv2[0::2] = X3;
        Aprox_inv2[1::2] = 0;
        APROX2 = np.convolve(Aprox_inv2,scale_inv,'full');
        
        npoints_aprox = Detail2.shape[0];
        Detail_inv2 = np.zeros((2*npoints_aprox));
        Detail_inv2[0::2] = Detail2;
        Detail_inv2[1::2] = 0;
        DETAIL2 = np.convolve(Detail_inv2,wavelet_inv,'full');
        
        X2 = APROX2 + DETAIL2;
        
        if X2.shape[0] > Detail.shape[0]:
            print("Quitando ceros");
            X2 = X2[0:Detail.shape[0]];

        npoints_aprox = X2.shape[0];
        Aprox_inv = np.zeros((2*npoints_aprox));
        Aprox_inv[0::2] = X2;
        Aprox_inv[1::2] = 0;
        APROX = np.convolve(Aprox_inv,scale_inv,'full');
        
        npoints_aprox = Detail.shape[0];
        Detail_inv = np.zeros((2*npoints_aprox));
        Detail_inv[0::2] = Detail;
        Detail_inv[1::2] = 0;
        DETAIL = np.convolve(Detail_inv,wavelet_inv,'full');
        
        SIGNAL = APROX + DETAIL;
        SIGNAL = SIGNAL[0:longitud_original];
        
        Detail3[Detail3 < thr*stdc[1]] = 0;
        Detail2[Detail2 < thr*stdc[2]] = 0;
        Detail[Detail < thr*stdc[3]] = 0;
        print('___________________') 
        SIGNAL=np.reshape(SIGNAL,(1,len(SIGNAL)))
        print(SIGNAL.shape)
        print(self.senalLoaded.shape)
        print(signal.shape)
        
        self.__coordinador.recibirDatosSenal(SIGNAL)
        self.__x_min=0
        self.__x_max=2000            
       #graficar utilizando el controlador
        self.__sc2.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
       
        
    def cargar_senal(self):
        #se abre el cuadro de dialogo para cargar archivos .mat
        
        if(len(self.senales)==0):
            archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir seÃ±al","","Todos los archivos (*);;Archivos mat (*.mat)*")
            if archivo_cargado != "":
                #cuando se carga la señal, se habilitan los botones para seguir con el proceso de filtrado
                data = sio.loadmat("C001R_EP_reposo.mat")
               
                
                data = data["data"]
               
                #se vuelven continuos los datos
          
                sensores,puntos,p=data.shape
                senal_continua=np.reshape(data,(sensores,puntos*p),order="F")
                self.senales=np.array(senal_continua)
                #canal1=senal_continua[0]
                self.senales=senal_continua
                self.canal.setEnabled(True)
                self.loadCanal.setEnabled(True)
                
                
        else:
            
            #el coordinador recibe y guarda la senal en su propio .py, por eso no 
            #necesito una variable que lo guarde en el .py interfaz
            canal=self.canal.text()
            self.canalLoaded=canal
            
            if(canal=='*'):
                self.__coordinador.recibirDatosSenal(self.senales)
            elif(canal=='1'):             
                self.__coordinador.recibirDatosSenal(self.senales[0:1])
                self.senalLoaded=self.senales[0:1]                
            elif(canal=='2'):             
                self.__coordinador.recibirDatosSenal(self.senales[1:2])
                self.senalLoaded=self.senales[1:2] 
            elif(canal=='3'):             
                self.__coordinador.recibirDatosSenal(self.senales[2:3])
                self.senalLoaded=self.senales[2:3] 
            elif(canal=='4'):             
                self.__coordinador.recibirDatosSenal(self.senales[3:4])
                self.senalLoaded=self.senales[3:4] 
            elif(canal=='5'):             
                self.__coordinador.recibirDatosSenal(self.senales[4:5])
                self.senalLoaded=self.senales[4:5] 
            elif(canal=='6'):             
                self.__coordinador.recibirDatosSenal(self.senales[5:6])
                self.senalLoaded=self.senales[5:6] 
            elif(canal=='7'):             
                self.__coordinador.recibirDatosSenal(self.senales[6:7])
                self.senalLoaded=self.senales[6:7] 
            elif(canal=='8'):             
                self.__coordinador.recibirDatosSenal(self.senales[7:])
                self.senalLoaded=self.senales[7:] 
                
            if(canal=='*'):
                self.filtrado_tipo.setEnabled(False)
                self.filtrar.setEnabled(False)
            else:
                self.filtrado_tipo.setEnabled(True)
                self.filtrar.setEnabled(True)
                
            self.__x_min=0
            self.__x_max=2000
            #graficar utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
            self.boton_adelante.setEnabled(True)
            self.boton_atras.setEnabled(True)
            self.boton_aumentar.setEnabled(True)
            self.boton_disminuir.setEnabled(True)
           
       
        
        

