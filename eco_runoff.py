# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECORunoff
                                 A QGIS plugin
 This tool automatize surface runoff simulations based on SCS methods
                              -------------------
        begin                : 2016-11-09
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jéssica Ribeiro Fontoura, Daniel Allasia, Vitor Geller, Robson Leo Pachaly
        email                : jessica.ribeirofontoura@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from eco_runoff_dialog import ECORunoffDialog
import os.path

from PyQt4 import QtCore
from PyQt4 import QtGui
from qgis.core import *
from qgis.gui import *
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterTableField
import os
import sys

#import Informacoes
#import Ajuda
#import Auxiliar
import Operacoes
import Hydrolib
#from progressbar import *
import shutil
import numpy as np

class ECORunoff:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ECORunoff_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dlg= ECORunoffDialog()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ECO-Runoff')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ECORunoff')
        self.toolbar.setObjectName(u'ECORunoff')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        self.dlg.comboBox_4.activated.connect(self.onLayerChange)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ECORunoff', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        #self.dlg = ECORunoffDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ECORunoff/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Surface Runoff Simulator'),
            callback=self.run,
            parent=self.iface.mainWindow())
            
    def onLayerChange (self):
        #ativa os layers adicionados ao canvas
        layers = self.iface.legendInterface().layers()
        selectedLayerIndex = self.dlg.comboBox_4.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        fields = selectedLayer.pendingFields()
        fieldnames = [field.name() for field in fields]
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(fieldnames)#preenche a comboBox com a lista dos campos do layer selecionado
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_2.addItems(fieldnames)
        self.dlg.comboBox_3.clear()
        self.dlg.comboBox_3.addItems(fieldnames)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ECO-Runoff'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def select_output_file(self):
        
        self.dlg = ECORunoffDialog()
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","Entrada_MHE", '*.hyd')
        self.dlg.lineEdit.setText(filename)

    def run(self):
        """Run method that performs all the real work"""
        layers = self.iface.legendInterface().layers()#ativa os layers adicionados ao canvas
        layer_list = []
       
        for layer in layers:
            layer_list.append(layer.name())#preenche a comboBox com a lista dos layers
        self.dlg.comboBox_4.clear()
        self.dlg.comboBox_4.addItems(layer_list)
        
        # selectedLayerIndex = self.dlg.comboBox_4.currentIndex()
        # selectedLayer = layers[selectedLayerIndex]
        
        # fields = selectedLayer.pendingFields()
        # fieldnames = [field.name() for field in fields]
        # self.dlg.comboBox.clear()
        # self.dlg.comboBox.addItems(fieldnames)
        # self.dlg.comboBox_2.clear()
        # self.dlg.comboBox_2.addItems(fieldnames)
        # self.dlg.comboBox_3.clear()
        # self.dlg.comboBox_3.addItems(fieldnames)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            n_int_tempo = self.dlg.lineEdit_2.text()
            duracao_int = self.dlg.lineEdit_3.text()
            n_int_cm_ch = self.dlg.lineEdit_4.text()
            local_chuva = self.dlg.lineEdit_5.text()
            parametro_a = self.dlg.lineEdit_6.text()
            parametro_b = self.dlg.lineEdit_7.text()
            parametro_c = self.dlg.lineEdit_8.text()
            parametro_d = self.dlg.lineEdit_9.text()
            tempo_retorno = self.dlg.lineEdit_10.text()
            posicao_pico = self.dlg.lineEdit_11.text()
            CN_bacia = self.dlg.lineEdit_12.text()
            area_bacia = self.dlg.lineEdit_13.text()
            tempo_concentracao = self.dlg.lineEdit_14.text()
            cenarios = self.dlg.lineEdit_16.text()
             
            filename = self.dlg.lineEdit.text()
            output_file = open(filename, 'w')
            self.pathname = os.path.dirname(filename)
            output_file.write("INICIO; " + n_int_tempo + "; " + duracao_int + "; " + "1; " + n_int_cm_ch + "; " + "1" +";\n"+ "CENARIOS; "+ cenarios + ";\n"+ "CHUVA; " + "1; " + 
            local_chuva +";\n" + "IDF; " + "1; "+ posicao_pico + "; " + tempo_retorno + "; " +  parametro_a + "; " + parametro_b + "; " + parametro_c + "; " + parametro_d + ";\n"
            + "OPERACAO; " + "1; " + local_chuva + ";\n" + "PQ; " + "1;\n" + "CN; " + CN_bacia + ";\n" + "HUT; " + area_bacia + "; " + tempo_concentracao + ";\n"  )
            #arquivo_entrada = open(filename, 'r')
            #output_file.close()
            ######
            output_file.close()
            #arquivo_entrada = open(filename, 'r')
            ######
            #self.executar_operacoes(arquivo_entrada) #rodar funcao "rodarHidroWeb"
            self.executar_operacoes(filename) #rodar funcao "rodarHidroWeb"
            
    def executar_operacoes(self,arquivo_entrada):
        
        Operacoes = OperacoesHidrologicas(arquivo_entrada,self.pathname)
        Operacoes.__init__(arquivo_entrada,self.pathname)
        
class OperacoesHidrologicas:
    
    def __init__(self, arquivo_entrada,pathname):
    
        #self.plotar_graficos = plotar_graficos
        self.arquivo_entrada = arquivo_entrada #criar/resetar a variavel
        self.caminho_arquivo_entrada = pathname
        self.arquivo_entrada = open(self.arquivo_entrada, 'r')
        
        #print "\n\tSelecione o arquivo de entrada.\n"
        #self.arquivo_entrada = tkFileDialog.askopenfile(mode='r') #procurar arquivo de entrada
        
       # if self.arquivo_entrada == None:g
            #print "\tATENCAO: Nenhum arquivo de entrada foi selecionado!"
            #tkMessageBox.showinfo("Erro.", "Selecione um arquivo de entrada válido.") #"Voce e' burro." ahahhahahaha
            
        #else:
            #print "\tArquivo selecionado.\n"
            #self.caminho_arquivo_entrada = os.path.dirname(self.arquivo_entrada.name) #define o path de trabalho igual ao do arquivo de entrada
        self.nome_arquivo_entrada = str(self.arquivo_entrada.name.split('/')[-1]) #nome_arquivo_entrada = nome.extensao
        extensao_arquivo_entrada = str(self.nome_arquivo_entrada.split(".")[-1])
 
            #if (not extensao_arquivo_entrada == "txt") and (not extensao_arquivo_entrada == "hyd"):
               # print "\tERRO: Formato do arquivo de entrada nao e' compativel.\n\tFormatos aceitos: .txt ou .hyd\n"
                #tkMessageBox.showinfo("Erro.", "Selecione um arquivo de entrada válido.\nFormatos: .txt ou .hyd") #"Voce e' burro." ahahhahahaha
            
           # else:
                #self.nome_arquivo_entrada = str(self.nome_arquivo_entrada.split(".")[0])
                
        #if (self.plotar_graficos) == 1: #se vou plotar novos eu deleto os antigos, se nao for , deixo os antigos como estavam.
            #self.deletarDiretoriosGraficos() #deletar o diretorio e antigas plotagens nestas pastas.
    
                    #Rodar o programa
        self.lerArquivoEntrada()
                
                    #Depois de rodar, fechar arquivo de entrada
        self.arquivo_entrada.close()
                
               # print "\n\n\tProcessamento encerrado. Simulacoes calculadas com sucesso.\n"
                #print "\n--------------------------------------------------------------------------------\n\n"
        
#-----------------------------------------------------------
    
    def ragequit(self):
        
#        self.master.destroy()  #esta linha foi desabilitada temporariamente pois ela faz com que ocorra erro (OperacoesHidrologicas instance has no attribute 'master')
        sys.exit()
        
#-----------------------------------------------------------

    def deletarDiretoriosGraficos(self):
        
            #se existe a pasta, delete-a. Isto e' feito para deletar plotagens de simulacoes antigas. A responsabilidade de remover as plotagens desta pasta e' do usuario.
        if os.path.exists(str(self.caminho_arquivo_entrada) + "/PlotagensPQ"):
            shutil.rmtree(str(self.caminho_arquivo_entrada) + "/PlotagensPQ")
            
            #se existe a pasta, delete-a. Isto e' feito para deletar plotagens de simulacoes antigas. A responsabilidade de remover as plotagens desta pasta e' do usuario.
        if os.path.exists(str(self.caminho_arquivo_entrada) + "/PlotagensPULS"):
            shutil.rmtree(str(self.caminho_arquivo_entrada) + "/PlotagensPULS")
            
            #se existe a pasta, delete-a. Isto e' feito para deletar plotagens de simulacoes antigas. A responsabilidade de remover as plotagens desta pasta e' do usuario.
        if os.path.exists(str(self.caminho_arquivo_entrada) + "/PlotagensMKC"):
            shutil.rmtree(str(self.caminho_arquivo_entrada) + "/PlotagensMKC")
            
            #se existe a pasta, delete-a. Isto e' feito para deletar plotagens de simulacoes antigas. A responsabilidade de remover as plotagens desta pasta e' do usuario.
        if os.path.exists(str(self.caminho_arquivo_entrada) + "/PlotagensJUNCAO"):
            shutil.rmtree(str(self.caminho_arquivo_entrada) + "/PlotagensJUNCAO")
                
#-----------------------------------------------------------

    def criarVariaveisPQ(self, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_PORD):
        
            #contar quantas operacoes PQ temos
        numero_operacoes_pq = 0
        
        for i in xrange(len(ORDEM_OPERACOES_HIDROLOGICAS)):
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "PQ":
                numero_operacoes_pq += 1
            
                #declarar variaveis que armazenarao as respostas
            #PQ
        HIDROGRAMAS_SAIDA_PQ  = np.array([[float(0.) for i in xrange( NUMERO_INTERVALOS_TEMPO )] for y in xrange( numero_operacoes_pq )], np.float64) #variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
        PRECIPITACAO_ORDENADA = [[ 0 for x in xrange(NUMERO_INTERVALOS_TEMPO) ] for y in xrange( len(NUMERO_PORD) )] #Variavel que armazena valores de precipitacao ordenada
                                                                                                                      #Objetivo e' armazenar somente 1 serie para cada chuva utilizada (sem repetir)
        return HIDROGRAMAS_SAIDA_PQ, PRECIPITACAO_ORDENADA
        
#-----------------------------------------------------------

    def criarVariaveisPULS(self, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO):
        
            #contar quantas operacoes PULS temos
        numero_operacoes_puls = 0
        
        for i in xrange(len(ORDEM_OPERACOES_HIDROLOGICAS)):
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "PULS":
                numero_operacoes_puls += 1
            
                #declarar variaveis que armazenarao as respostas
            #PULS
        HIDROGRAMAS_SAIDA_PULS = np.array([[float(0.) for i in xrange(0, NUMERO_INTERVALOS_TEMPO)] for y in xrange( numero_operacoes_puls )], np.float64) #variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
                
        return HIDROGRAMAS_SAIDA_PULS
        
#-----------------------------------------------------------

    def criarVariaveisMKC(self, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO):
        
            #contar quantas operacoes MKC temos
        numero_operacoes_mkc = 0
        
        for i in xrange(len(ORDEM_OPERACOES_HIDROLOGICAS)):
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "MKC":
                numero_operacoes_mkc += 1
            
                #declarar variaveis que armazenarao as respostas
            #MKC
        HIDROGRAMAS_SAIDA_MKC = np.array([[float(0.) for i in xrange(0, NUMERO_INTERVALOS_TEMPO)] for y in xrange( numero_operacoes_mkc )], np.float64) #variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
                
        return HIDROGRAMAS_SAIDA_MKC
        
#-----------------------------------------------------------

    def criarVariaveisJUNCAO(self, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO):
        
            #contar quantas operacoes JUNCAO temos
        numero_operacoes_juncao = 0
        
        for i in xrange(len(ORDEM_OPERACOES_HIDROLOGICAS)):
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "JUNCAO":
                numero_operacoes_juncao += 1
            
                #declarar variaveis que armazenarao as respostas
            #JUNCAO
        HIDROGRAMAS_SAIDA_JUNCAO = np.array([[float(0.) for i in xrange(0, NUMERO_INTERVALOS_TEMPO)] for y in xrange( numero_operacoes_juncao )], np.float64) #variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
        
        return HIDROGRAMAS_SAIDA_JUNCAO
#-----------------------------------------------------------

    def gerarPrecipOrdenada(self, NUMERO_INTERVALOS_TEMPO_CHUVA ,DURACAO_INTERVALO_TEMPO, PARAMETRO_A, PARAMETRO_B, PARAMETRO_C, PARAMETRO_D, POSPICO, TR):
        
            #CALCULAR A PRECIPITACAO_DESACUMULADA
        PRECIPITACAO_DESACUMULADA = Hydrolib.calcular_PrecipitacaoDesacumulada( NUMERO_INTERVALOS_TEMPO_CHUVA, DURACAO_INTERVALO_TEMPO, TR, PARAMETRO_A, PARAMETRO_B, PARAMETRO_C, PARAMETRO_D )
                                                
            #ordeno a chuva pelos blocos alternados e coloca na matriz da chuva 
        PRECIPITACAO_ORDENADA = Hydrolib.aplicar_BlocosAlternados( PRECIPITACAO_DESACUMULADA, NUMERO_INTERVALOS_TEMPO_CHUVA, POSPICO )  #P na verdade e' PRECIPITACAO_ORDENADA....                                         
        
        return PRECIPITACAO_ORDENADA
        
#-----------------------------------------------------------

    def rodarCenariosPQ(self, NUMERO_INTERVALOS_TEMPO_CHUVA, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO, CN, TC, AREA, PRECIPITACAO_ORDENADA):
        #Executar uma operacao de cada vez....
        
                #CALCULAR A PRECIPITACAO_EFETIVA
        PRECIPITACAO_EFETIVA = Hydrolib.calcular_PrecipitacaoEfetiva_CN( CN, PRECIPITACAO_ORDENADA, NUMERO_INTERVALOS_TEMPO, NUMERO_INTERVALOS_TEMPO_CHUVA )
                
            #Calcular HUT da operacao
        TEMPO_SUBIDA, VAZAO_PICO_HUT, TEMPO_BASE = Hydrolib.calcular_HUT_SCS( TC, AREA, DURACAO_INTERVALO_TEMPO ) #Caracteristicas do HUT para convolucao
                
            #Calular Hidrograma da operacao
        HIDROGRAMAS = Hydrolib.aplicar_Convolucao( TEMPO_BASE, VAZAO_PICO_HUT, TEMPO_SUBIDA, DURACAO_INTERVALO_TEMPO, NUMERO_INTERVALOS_TEMPO, PRECIPITACAO_EFETIVA ) #Convolucao para HUT
                                         
        
        return HIDROGRAMAS  #a efetiva so' e' retornada por que ela e' necessaria na plotagem do grafico.

#-----------------------------------------------------------

    def rodarOperacaoPQ(self, NUMERO_INTERVALOS_TEMPO_CHUVA, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO, CN, TC, AREA, PRECIPITACAO_ORDENADA, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico):
        
        #Executar uma operacao de cada vez....
        
            #CALCULAR A PRECIPITACAO_EFETIVA
        PRECIPITACAO_EFETIVA = Hydrolib.calcular_PrecipitacaoEfetiva_CN( CN, PRECIPITACAO_ORDENADA, NUMERO_INTERVALOS_TEMPO, NUMERO_INTERVALOS_TEMPO_CHUVA )
        
            #Calcular HUT da operacao
        TEMPO_SUBIDA, VAZAO_PICO_HUT, TEMPO_BASE = Hydrolib.calcular_HUT_SCS( TC, AREA, DURACAO_INTERVALO_TEMPO ) #Caracteristicas do HUT para convolucao
                
            #Calular Hidrograma da operacao
        HIDROGRAMAS = Hydrolib.aplicar_Convolucao( TEMPO_BASE, VAZAO_PICO_HUT, TEMPO_SUBIDA, DURACAO_INTERVALO_TEMPO, NUMERO_INTERVALOS_TEMPO, PRECIPITACAO_EFETIVA ) #Convolucao para HUT
                                          #Tempo_base, Vazao_pico_HUT, Tempo_subida, dt                     , nint_tempo             , Pef
                                          
        #if (self.plotar_graficos) == 1:
                #Plotar grafico chuva vazao da operacao
                    #plotagem (TC, Hidrograma, P, Pef, QIDF, nint_tempo, dt, pathname,nome_posto,simulacao) 
                        #se e' algo que ja' esta' definido anter de rodar o programa, usa-se [dados_utilizados]; Se e' algo que esta' definido agora (como HIDROGRAMAS), usa-se [contador_manual];
                        
        Hydrolib.plotar_Hidrogramas_PQ(HIDROGRAMAS, PRECIPITACAO_ORDENADA, PRECIPITACAO_EFETIVA, NUMERO_INTERVALOS_TEMPO, 
                                DURACAO_INTERVALO_TEMPO, self.caminho_arquivo_entrada, NOMES_OPERACOES_HIDROLOGICAS,  numero_do_grafico  )
            
        
        return HIDROGRAMAS  #a efetiva so' e' retornada por que ela e' necessaria na plotagem do grafico.
        
#-----------------------------------------------------------

#    def rodarOperacaoPULS(self, HIDROGRAMA_ENTRA, COTAS_FUNDO, COTAS_INICIAL, ESTRUTURAS_PULS, CURVA_COTA_VOLUME, DURACAO_INTERVALO_TEMPO, NUMERO_INTERVALOS_TEMPO, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico):
    def rodarOperacaoPULS(self, HIDROGRAMA_ENTRA, COTA_INICIAL, ESTRUTURAS_PULS, CURVA_COTA_VOLUME, DURACAO_INTERVALO_TEMPO, NUMERO_INTERVALOS_TEMPO, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico):
        
            #obter a curva de vazoes
        curva_de_vazoes, alturas_vazoes_calculadas = Hydrolib.calcular_VazaoSaida_Puls(ESTRUTURAS_PULS, CURVA_COTA_VOLUME[0]) # curva_cota_volume[0] por que nesta etapa nao preciso de volume, so' de cota.
        
            #aplicar puls
        HIDROGRAMA_SAI = Hydrolib.aplicar_Puls(CURVA_COTA_VOLUME, HIDROGRAMA_ENTRA, curva_de_vazoes, alturas_vazoes_calculadas, COTA_INICIAL, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO)
        
        if (self.plotar_graficos) == 1:
                #Plotar grafico puls da operacao
                #se e' algo que ja' esta' definido antes de rodar o programa, usa-se [dados_utilizados]; Se e' algo que esta' definido agora (como HIDROGRAMAS), usa-se [contador_manual];
                        
            Hydrolib.plotar_Hidrogramas_PULS( HIDROGRAMA_ENTRA, HIDROGRAMA_SAI, NUMERO_INTERVALOS_TEMPO, self.caminho_arquivo_entrada, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico )
            
        
            #retornar hidrograma de saida
        return HIDROGRAMA_SAI
        
#-----------------------------------------------------------

    def rodarOperacaoMKC(self, HIDROGRAMA_ENTRA, DIFERENCA_COTA, COMPRIMENTO_CANAL, LARGURA_CANAL, COEF_RUGOSIDADE, DURACAO_INTERVALO_TEMPO, NUMERO_INTERVALOS_TEMPO, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico):
        
            #aplicar puls
        HIDROGRAMA_SAI = Hydrolib.aplicar_MuskingunCunge(HIDROGRAMA_ENTRA, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO, DIFERENCA_COTA, COMPRIMENTO_CANAL, LARGURA_CANAL, COEF_RUGOSIDADE)
        
        if (self.plotar_graficos) == 1:
                #Plotar grafico mkc da operacao
                #se e' algo que ja' esta' definido antes de rodar o programa, usa-se [dados_utilizados]; Se e' algo que esta' definido agora (como HIDROGRAMAS), usa-se [contador_manual];
                
            Hydrolib.plotar_Hidrogramas_MKC( HIDROGRAMA_ENTRA, HIDROGRAMA_SAI, NUMERO_INTERVALOS_TEMPO, self.caminho_arquivo_entrada, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico )
            
        
            #retornar hidrograma de saida
        return HIDROGRAMA_SAI

#-----------------------------------------------------------

    def rodarOperacaoJUNCAO(self, valores_hidrogramas_da_juncao, NUMERO_INTERVALOS_TEMPO, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico):
        
            #aplicar juncao
        HIDROGRAMA_SAI = Hydrolib.somar_Hidrogramas( NUMERO_INTERVALOS_TEMPO, valores_hidrogramas_da_juncao )
        
        if (self.plotar_graficos) == 1:
                #Plotar grafico junao da operacao
                #se e' algo que ja' esta' definido antes de rodar o programa, usa-se [dados_utilizados]; Se e' algo que esta' definido agora (como HIDROGRAMAS), usa-se [contador_manual];
                
            Hydrolib.plotar_somar_Hidrogramas( HIDROGRAMA_SAI, valores_hidrogramas_da_juncao, NUMERO_INTERVALOS_TEMPO, self.caminho_arquivo_entrada, NOMES_OPERACOES_HIDROLOGICAS, numero_do_grafico )
            
        
            #retornar hidrograma de saida
        return HIDROGRAMA_SAI

#-----------------------------------------------------------

    def escreverSaidaCENARIOS(self, HIDROGRAMAS, CENARIOS_ANOS, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_INTERVALOS_TEMPO_CHUVA, DURACAO_INTERVALO_TEMPO, NOMES_OPERACOES_HIDROLOGICAS):
        
            #preparo arquivo de saida
        saidaCENARIOS, fileExtension = os.path.splitext(self.caminho_arquivo_entrada +"/"+ self.nome_arquivo_entrada + "_Cenarios_" + str(NOMES_OPERACOES_HIDROLOGICAS))
        saidaCENARIOS               += ".ohy" #arquivo saida igual ao de entrada + o(output) hy(drology)
        saidaCENARIOS                = open( saidaCENARIOS, 'w', buffering = 0 )

        saidaCENARIOS.write ("\n                           MODELO HYDROLIB\n             RESULTADOS DOS CENARIOS DOS POSTOS DE CHUVA")
        saidaCENARIOS.write ("\n------------------------------------------------------------------------\n\n")


                #Escrevo os resultados da chuva no arquivo de saida
                
                #escrevo os parametros no arquivo de saida
        saidaCENARIOS.write("\n ---- PARAMETROS GERAIS DA SIMULACAO  ----\n\n")
        saidaCENARIOS.write("Numero de intervalos de tempo           : "+str(NUMERO_INTERVALOS_TEMPO)+"\n")
        saidaCENARIOS.write("Numero de intervalos de tempo com chuva : "+str(NUMERO_INTERVALOS_TEMPO_CHUVA)+"\n")
        saidaCENARIOS.write("Duracao do intervalo de tempo (seg)     : "+str(DURACAO_INTERVALO_TEMPO)+"\n")
        saidaCENARIOS.write("Numero total de simulacoes hidrologicas : "+str(len(ORDEM_OPERACOES_HIDROLOGICAS))+"\n")
        saidaCENARIOS.write("Numero de cenarios                      : "+str(len(HIDROGRAMAS))+"\n\n")

        saidaCENARIOS.write("\n-------------------------------------------------------------------------\n")
        saidaCENARIOS.write("\n ---- CENARIOS DOS HIDROGRAMAS DE PROJETO PARA AS BACIAS CALCULADAS A PARTIR DE IDF ----\n\n")

        saidaCENARIOS.write("\n\t\t\tPOSTO:" +str( NOMES_OPERACOES_HIDROLOGICAS )+"\n\n")  #CORRIGIR ESTA LINHA: "RESULTADO DA OPERACAO 1  - Taruma - Montante"
        
        cabecalho_tabela = []
        for x in xrange( len(CENARIOS_ANOS)):
            
            if ((CENARIOS_ANOS[x]<10)):
                
                aux = ["        TR = "+str(CENARIOS_ANOS[x])] #"        Posto"+str(x)
                cabecalho_tabela.insert(x,aux[0])
                
            else:
                aux = ["       TR = "+str(CENARIOS_ANOS[x])] #"        Posto"+str(x)
                cabecalho_tabela.insert(x,aux[0])
                
            
        saidaCENARIOS.write("      dt "+','.join(cabecalho_tabela))
        saidaCENARIOS.write(" \n")
                
                        #Escrevo os Maximos dos Cenarios no arquivo de saida
        for dt in xrange( NUMERO_INTERVALOS_TEMPO ): #valor
            saidaCENARIOS.write("%8d" %int(dt+1))
                    
            for coluna in xrange(len(CENARIOS_ANOS)): #Cenario #nao devia ter usado OPERACAO como contadora.. Talvez coluna fosse melhor
                saidaCENARIOS.write("%15.8f" %float( HIDROGRAMAS[coluna][dt] )) #Escrevo valores que devem ser escritos ;)
                
            saidaCENARIOS.write("\n")
                
        saidaCENARIOS.write("\n--------------------------------------------------------------------------------------\n\n")
                
        saidaCENARIOS.close()
        
#-----------------------------------------------------------

    def escreverSaidaPQ(self, HIDROGRAMAS_SAIDA_PQ, PRECIPITACAO_ORDENADA, ORDEM_OPERACOES_HIDROLOGICAS, CHUVA_OPERACAO_CORRESPONDENTE, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO, NUMERO_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO_CHUVA):
    
            #preparo arquivo de saida
        saidaPQ, fileExtension = os.path.splitext(self.caminho_arquivo_entrada +"/"+ self.nome_arquivo_entrada + "_Saida_Chuva-vazao")
        saidaPQ               += ".ohy" #arquivo saida igual ao de entrada + o(output) hy(drology)
        saidaPQ                = open( saidaPQ, 'w', buffering = 0 )

        saidaPQ.write ("\n                          MODELO HYDROLIB\n                     RESULTADOS DA MODELAGEM")
        saidaPQ.write ("\n------------------------------------------------------------------------\n\n")


                #Escrevo os resultados da chuva no arquivo de saida
                
                #escrevo os parametros no arquivo de saida
        saidaPQ.write("\n ---- PARAMETROS GERAIS DA SIMULACAO  ----\n\n")
        saidaPQ.write("Numero de intervalos de tempo           : "+str(NUMERO_INTERVALOS_TEMPO)+"\n")
        saidaPQ.write("Numero de intervalos de tempo com chuva : "+str(NUMERO_INTERVALOS_TEMPO_CHUVA)+"\n")
        saidaPQ.write("Duracao do intervalo de tempo (seg)     : "+str(DURACAO_INTERVALO_TEMPO)+"\n")
        saidaPQ.write("Numero total de simulacoes hidrologicas : "+str(len(ORDEM_OPERACOES_HIDROLOGICAS))+"\n")
        saidaPQ.write("Numero de simulacoes chuva-vazao        : "+str(len(HIDROGRAMAS_SAIDA_PQ))+"\n\n")

                
        saidaPQ.write("\n ---- INFORMACOES DAS SIMULACOES CHUVA-VAZAO ---- \n\n")

                #faz parte do cabecalho do programa
        for i in xrange( len(ORDEM_OPERACOES_HIDROLOGICAS) ):

            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "PQ":
                saidaPQ.write("Hidrograma "+str(i+1)+": Calculada atraves da serie de chuva " + str((CHUVA_OPERACAO_CORRESPONDENTE[i]+1)) + ".\n")


        saidaPQ.write("\n\n") #Deixar espaco em branco apos \n
        aux = ["  Chuva"+str(x+1) for x in xrange( len(PRECIPITACAO_ORDENADA) )] #Esta linha pode estar errada quando postos >= 10 .... sair da coluna
        saidaPQ.write("      dt"+' '.join(aux)) 
        saidaPQ.write("\n") 

                #escrevo a chuva no arquivo de saida
        print "\n\n\tEscrevendo series de chuva no arquivo de saida."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_INTERVALOS_TEMPO_CHUVA)).start()
        
        for j in xrange( NUMERO_INTERVALOS_TEMPO_CHUVA ):
            saidaPQ.write("%8d" %int(j+1))
                    
            for i in PRECIPITACAO_ORDENADA: #i assume os valores de cada sublista da lista principal
                saidaPQ.write(" %8.3f" %float(i[j])) #escreva  o termo j da sublista i (que por sua vez e' uma lista do conjunto de listas que formam a P_ord)
                        
            saidaPQ.write('\n')
            
            #pbar.update(j + 1)
        #pbar.finish()
        
        saidaPQ.write("\n-------------------------------------------------------------------------------------------\n")
        saidaPQ.write("\n\t\t ---- HIDROGRAMAS CHUVA-VAZAO ----\n\n")
                
        aux = [] #precisa ser declarada
            
        for x in xrange( len(HIDROGRAMAS_SAIDA_PQ) ):
            if x >= 9:
                aux = aux +[" Hidrograma"+str(x+1)]
                
            else:
                aux = aux +["  Hidrograma"+str(x+1)]
                    
        saidaPQ.write("      dt "+' '.join(aux)) 
        saidaPQ.write(" \n")
                                
                #escrevo a chuva no arquivo de saida
        print "\n\n\tEscrevendo os hidrogramas das operacoes chuva-vazao no arquivo de saida."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_INTERVALOS_TEMPO)).start()
        
        for x in xrange( NUMERO_INTERVALOS_TEMPO ):
            saidaPQ.write("%8d" %int(x+1))
                    
            for coluna in HIDROGRAMAS_SAIDA_PQ: #nao devia ter usado OPERACAO como contadora.. Talvez coluna fosse melhor
                saidaPQ.write("%14.8f" %float(coluna[x])) #coluna assume a serie inteira de um hidrograma de projeto, o [x] indica qual valor da serie sera' escrito.
                        
            saidaPQ.write('\n')
            
            #pbar.update(x + 1)
        #pbar.finish()
        
        saidaPQ.close()
        
#-----------------------------------------------------------

    def escreverSaidaPULS(self, HIDROGRAMAS_SAIDA_PQ, HIDROGRAMAS_SAIDA_PULS, HIDROGRAMAS_SAIDA_MKC, HIDROGRAMAS_SAIDA_JUNCAO, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_OPERACOES_HIDROLOGICAS, DURACAO_INTERVALO_TEMPO, HIDROGRAMAS_ENTRADA_PULS, ORDEM_EXECUCAO_PQ, ORDEM_EXECUCAO_PULS, ORDEM_EXECUCAO_MKC, ORDEM_EXECUCAO_JUNCAO):
        
            #preparo arquivo de saida
        saidaPULS, fileExtension = os.path.splitext(self.caminho_arquivo_entrada +"/"+ self.nome_arquivo_entrada + "_Saida_Puls")
        saidaPULS               += ".ohy" #arquivo saida igual ao de entrada + o(output) hy(drology)
        saidaPULS                = open( saidaPULS, 'w', buffering = 0 )

        saidaPULS.write ("\n                          MODELO HYDROLIB\n                     RESULTADOS DA MODELAGEM")
        saidaPULS.write ("\n------------------------------------------------------------------------\n\n")
        
                #Escrevo os resultados da chuva no arquivo de saida
                
                #escrevo os parametros no arquivo de saida
        saidaPULS.write("\n ---- PARAMETROS GERAIS DA SIMULACAO  ----\n\n")
        saidaPULS.write("Numero de intervalos de tempo           : "+str(NUMERO_INTERVALOS_TEMPO)+"\n")
        saidaPULS.write("Duracao do intervalo de tempo (seg)     : "+str(DURACAO_INTERVALO_TEMPO)+"\n")
        saidaPULS.write("Numero total de simulacoes hidrologicas : "+str(len(ORDEM_OPERACOES_HIDROLOGICAS))+"\n")
        saidaPULS.write("Numero de simulacoes PULS               : "+str(len(HIDROGRAMAS_SAIDA_PULS))+"\n\n")
        
        
        print "\n\n\tEscrevendo hidrogramas das operacoes de Puls no arquivo de saida."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_OPERACOES_HIDROLOGICAS)).start()
        
        for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS):
            
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "PULS":
                
                    #saber qual e' o indice da operacao em ordem crescente-----> e' diferente da ordem da execucao.....
                indice_hidrograma_saida = ORDEM_EXECUCAO_PULS.index(i)

                saidaPULS.write("\n-------------------------------------------------------------------------------------------\n")
                saidaPULS.write("Operacao hidrologica numero: " + str(i+1))
                
                if (type(HIDROGRAMAS_ENTRADA_PULS[i]) == int): #se entrar neste loop e' porque o hidrograma de entrada do puls que sera' escrito e' oriundo de outra operacao
                    saidaPULS.write("\nHidrograma de entrada oriundo da operacao hidrologica numero: " + str(i))
                    
                        #Tenho que descobrir se e' oriundo de um chuva-vazao, puls ou mkc (nao incluso ainda)
                    if (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_PULS[i])] == "PQ"): #e' oriundo de chuva-vazao
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do puls i e' oriundo de uma operacao chuva-vazao
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_PQ.index(HIDROGRAMAS_ENTRADA_PULS[i])#temos que descobrir qual e' o hidrograma que e' usado...
                        
                        saidaPULS.write("\n\n")
                        saidaPULS.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaPULS.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_PQ[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                
                
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de puls tambem
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_PULS[i])] == "PULS"): #se e' oriundo de outro PULS
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do puls i e' oriundo de outra operacao de puls
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_PULS.index(HIDROGRAMAS_ENTRADA_PULS[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaPULS.write("\n\n")
                        saidaPULS.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaPULS.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de muskigun-cunge
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_PULS[i])] == "MKC"): #se e' oriundo de MKC
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do puls i e' oriundo de outra operacao de mkc
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_MKC.index(HIDROGRAMAS_ENTRADA_PULS[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaPULS.write("\n\n")
                        saidaPULS.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaPULS.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de JUNCAO
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_PULS[i])] == "JUNCAO"): #se e' oriundo de JUNCAO
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do puls i e' oriundo de outra operacao de juncao
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_JUNCAO.index(HIDROGRAMAS_ENTRADA_PULS[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaPULS.write("\n\n")
                        saidaPULS.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaPULS.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                else: #hidrograma de entrada do puls a ser escrito e' fornecido pelo usuario, em um arquivo de texto que deve ser lido novamente (troco memoria por velocidade de processamento)
                    saidaPULS.write("\nHidrograma fornecido pelo usuario. Diretorio: " + str(HIDROGRAMAS_ENTRADA_PULS[i]))
                    
                        #o hidrograma observado sera' lido novamente, pois desta forma eu economizo memoria em troca de velocidade de processamento.
#                       #e' um hidrograma observador, deve-se ler o arquivo.

                        #contar quantas linhas tem o arquivo
                    numero_linhas  = sum(1 for linha in open(HIDROGRAMAS_ENTRADA_PULS[i],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                    arquivo_hidrograma = open(HIDROGRAMAS_ENTRADA_PULS[i], 'r')                 #abrir o arquivo para le-lo.
                    
                        #criar variavel para armazenar o hidrograma entrada
                    hidrograma_usado_neste_puls = [0. for termos in xrange(NUMERO_INTERVALOS_TEMPO)]

                        #loop para ler linhas do arquivo da curva cota-volume
                    for linha in xrange(numero_linhas):
                        conteudo_hidrograma = arquivo_hidrograma.readline().split(";")     #ler a linha e dividir 
                        hidrograma_usado_neste_puls[linha] = conteudo_hidrograma[0]        #valores de hidrograma
                    
                    arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.
                        
                    saidaPULS.write("\n\n")
                    saidaPULS.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                    
                    for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                        saidaPULS.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(hidrograma_usado_neste_puls[i2]), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_saida][i2])) ) #escrever os intervalos

            #pbar.update(i + 1)
        #pbar.finish()

        saidaPULS.close()
        
#-----------------------------------------------------------

    def escreverSaidaMKC(self, HIDROGRAMAS_SAIDA_PQ, HIDROGRAMAS_SAIDA_PULS, HIDROGRAMAS_SAIDA_MKC, HIDROGRAMAS_SAIDA_JUNCAO, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_OPERACOES_HIDROLOGICAS, DURACAO_INTERVALO_TEMPO, HIDROGRAMAS_ENTRADA_MKC, ORDEM_EXECUCAO_PQ, ORDEM_EXECUCAO_PULS, ORDEM_EXECUCAO_MKC, ORDEM_EXECUCAO_JUNCAO):
        
            #preparo arquivo de saida
        saidaMKC, fileExtension = os.path.splitext(self.caminho_arquivo_entrada +"/"+ self.nome_arquivo_entrada + "_Saida_Muskingun-Cunge")
        saidaMKC               += ".ohy" #arquivo saida igual ao de entrada + o(output) hy(drology)
        saidaMKC                = open( saidaMKC, 'w', buffering = 0 )

        saidaMKC.write ("\n                          MODELO HYDROLIB\n                     RESULTADOS DA MODELAGEM")
        saidaMKC.write ("\n------------------------------------------------------------------------\n\n")
        
                #Escrevo os resultados da chuva no arquivo de saida
                
                #escrevo os parametros no arquivo de saida
        saidaMKC.write("\n ---- PARAMETROS GERAIS DA SIMULACAO  ----\n\n")
        saidaMKC.write("Numero de intervalos de tempo           : "+str(NUMERO_INTERVALOS_TEMPO)+"\n")
        saidaMKC.write("Duracao do intervalo de tempo (seg)     : "+str(DURACAO_INTERVALO_TEMPO)+"\n")
        saidaMKC.write("Numero total de simulacoes hidrologicas : "+str(len(ORDEM_OPERACOES_HIDROLOGICAS))+"\n")
        saidaMKC.write("Numero de simulacoes Muskingun-Cunge    : "+str(len(HIDROGRAMAS_SAIDA_MKC))+"\n\n")
        
        
        print "\n\n\tEscrevendo hidrogramas das operacoes de Muskingun-Cunge no arquivo de saida."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_OPERACOES_HIDROLOGICAS)).start()
        
        for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS):
            
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "MKC":
                
                    #saber qual e' o indice da operacao em ordem crescente-----> e' diferente da ordem da execucao.....
                indice_hidrograma_saida = ORDEM_EXECUCAO_MKC.index(i)

                saidaMKC.write("\n-------------------------------------------------------------------------------------------\n")
                saidaMKC.write("Operacao hidrologica numero: " + str(i+1))
                
                if (type(HIDROGRAMAS_ENTRADA_MKC[i]) == int): #se entrar neste loop e' porque o hidrograma de entrada do puls que sera' escrito e' oriundo de outra operacao
                    saidaMKC.write("\nHidrograma de entrada oriundo da operacao hidrologica numero: " + str(i))
                    
                        #Tenho que descobrir se e' oriundo de um chuva-vazao, puls ou mkc (nao incluso ainda)
                    if (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_MKC[i])] == "PQ"): #e' oriundo de chuva-vazao
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do mkc i e' oriundo de uma operacao chuva-vazao
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_PQ.index(HIDROGRAMAS_ENTRADA_MKC[i])#temos que descobrir qual e' o hidrograma que e' usado...
                        
                        saidaMKC.write("\n\n")
                        saidaMKC.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaMKC.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_PQ[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                
                
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de puls tambem
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_MKC[i])] == "PULS"): #se e' oriundo de outro PULS
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do mkc i e' oriundo de outra operacao de puls
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_PULS.index(HIDROGRAMAS_ENTRADA_MKC[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaMKC.write("\n\n")
                        saidaMKC.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaMKC.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de muskigun-cunge
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_MKC[i])] == "MKC"): #se e' oriundo de MKC
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do mkc i e' oriundo de outra operacao de mkc
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_MKC.index(HIDROGRAMAS_ENTRADA_MKC[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaMKC.write("\n\n")
                        saidaMKC.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaMKC.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                        #caso o hidrograma de entrada da operacao X for oriundo da operacao Y que por sua vez e' de JUNCAO
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[(HIDROGRAMAS_ENTRADA_MKC[i])] == "JUNCAO"): #se e' oriundo de JUNCAO
                    
                            #Se entrou aqui, e' porque o hidrograma de entrada do mkc i e' oriundo de outra operacao de juncao
                        indice_hidrograma_entrada = ORDEM_EXECUCAO_JUNCAO.index(HIDROGRAMAS_ENTRADA_MKC[i])#temos que descobrir qual e' o hidrograma que e' usado...
                    
                        saidaMKC.write("\n\n")
                        saidaMKC.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                        
                        for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                            saidaMKC.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma_entrada][i2]), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_saida][i2])) ) #escrever os intervalos
                    
                    
                else: #hidrograma de entrada do puls a ser escrito e' fornecido pelo usuario, em um arquivo de texto que deve ser lido novamente (troco memoria por velocidade de processamento)
                    saidaMKC.write("\nHidrograma fornecido pelo usuario. Diretorio: " + str(HIDROGRAMAS_ENTRADA_MKC[i]))
                    
                        #o hidrograma observado sera' lido novamente, pois desta forma eu economizo memoria em troca de velocidade de processamento.
#                       #e' um hidrograma observador, deve-se ler o arquivo.

                        #contar quantas linhas tem o arquivo
                    numero_linhas  = sum(1 for linha in open(HIDROGRAMAS_ENTRADA_MKC[i],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                    arquivo_hidrograma = open(HIDROGRAMAS_ENTRADA_MKC[i], 'r')                 #abrir o arquivo para le-lo.
                    
                        #criar variavel para armazenar o hidrograma entrada
                    hidrograma_usado_neste_mkc = [0. for termos in xrange(NUMERO_INTERVALOS_TEMPO)]

                        #loop para ler linhas do arquivo da curva cota-volume
                    for linha in xrange(numero_linhas):
                        conteudo_hidrograma = arquivo_hidrograma.readline().split(";")     #ler a linha e dividir 
                        hidrograma_usado_neste_mkc[linha] = conteudo_hidrograma[0]        #valores de hidrograma
                    
                    arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.
                        
                    saidaMKC.write("\n\n")
                    saidaMKC.write("      dt, Hidro_Entrada, Hidrogr_Saida\n")
                    
                    for i2 in xrange(NUMERO_INTERVALOS_TEMPO):
                        saidaMKC.write("%8d,%14.8f,%14.8f\n" %((i2+1), float(hidrograma_usado_neste_mkc[i2]), float(HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_saida][i2])) ) #escrever os intervalos

            #pbar.update(i + 1)
        #pbar.finish()

        saidaMKC.close()

#-----------------------------------------------------------

    def escreverSaidaJUNCAO(self, HIDROGRAMAS_SAIDA_PQ, HIDROGRAMAS_SAIDA_PULS, HIDROGRAMAS_SAIDA_MKC, HIDROGRAMAS_SAIDA_JUNCAO, ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_OPERACOES_HIDROLOGICAS, DURACAO_INTERVALO_TEMPO, JUNCOES_HIDROGRAMAS, ORDEM_EXECUCAO_PQ, ORDEM_EXECUCAO_PULS, ORDEM_EXECUCAO_MKC, ORDEM_EXECUCAO_JUNCAO):
        
            #preparo arquivo de saida
        saidaJUNCAO, fileExtension = os.path.splitext(self.caminho_arquivo_entrada +"/"+ self.nome_arquivo_entrada + "_Saida_Juncao")
        saidaJUNCAO               += ".ohy" #arquivo saida igual ao de entrada + o(output) hy(drology)
        saidaJUNCAO                = open( saidaJUNCAO, 'w', buffering = 0 )

        saidaJUNCAO.write ("\n                          MODELO HYDROLIB\n                     RESULTADOS DA MODELAGEM")
        saidaJUNCAO.write ("\n------------------------------------------------------------------------\n\n")
        
                #Escrevo os resultados da chuva no arquivo de saida
                
                #escrevo os parametros no arquivo de saida
        saidaJUNCAO.write("\n ---- PARAMETROS GERAIS DA SIMULACAO  ----\n\n")
        saidaJUNCAO.write("Numero de intervalos de tempo           : "+str(NUMERO_INTERVALOS_TEMPO)+"\n")
        saidaJUNCAO.write("Duracao do intervalo de tempo (seg)     : "+str(DURACAO_INTERVALO_TEMPO)+"\n")
        saidaJUNCAO.write("Numero total de simulacoes hidrologicas : "+str(len(ORDEM_OPERACOES_HIDROLOGICAS))+"\n")
        saidaJUNCAO.write("Numero de simulacoes Juncao             : "+str(len(HIDROGRAMAS_SAIDA_JUNCAO))+"\n\n")
        
        
        print "\n\n\tEscrevendo hidrogramas das operacoes de Juncao no arquivo de saida."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_OPERACOES_HIDROLOGICAS)).start()
        
        for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS):
            
            if ORDEM_OPERACOES_HIDROLOGICAS[i] == "JUNCAO":
                
#                #   Esta condicao diz: Se JUNCOES_HIDROGRAMAS == 0, nao e' operacao de juncao, pois esta variavel acompanha NUMERO_OPERACOES
#                if not (JUNCOES_HIDROGRAMAS[i] == 0): #NAO SEI SE NAO DA PAU, POIS SE O USUARIO SOMAR SOMENTE O PRIMEIRO HIDROGRAMA ELE PODE INTERPRETAR QUE NAO HA' SOMA!!

                saidaJUNCAO.write("\n-------------------------------------------------------------------------------------------\n\n")
                saidaJUNCAO.write("Operacao hidrologica numero: " + str(i+1))
        
                valores_hidrogramas_da_juncao = [[0. for nint_tempo in xrange(NUMERO_INTERVALOS_TEMPO)] for numero_hidrogramas in xrange(len(JUNCOES_HIDROGRAMAS[i]))]
                        
                #    loop para comecar a copiar os valores
                for numero_hidrograma in xrange(len(JUNCOES_HIDROGRAMAS[i])):
        
                    #        Analisar de onde eu pego o hidrograma.... Este loop e' necessario pois temos hidrogramas oriundo de ate' 4 variaveis e dados por txt...
                    #        Este algoritmo seleciona a parte interessante do algoritmo para facilitar o proximo algoritmo (escrever).. se isso nao fosse feito,
                    #    seria necessario varios IFs que seriam testados a cada NUMERO_INTERVALO_TEMPO, deixando o programa mais lento.
                    
                    #   Analisar o tipo de hidrograma que entra na juncao
                    if (type(JUNCOES_HIDROGRAMAS[i][numero_hidrograma]) == int):
                        
                        #   analisar de onde pego o hidrograma
                        if ((JUNCOES_HIDROGRAMAS[i][numero_hidrograma]) >= 0 ):  #entra um hidrograma de outra operacao, esta operacao ja' esta' calculada (verificado anteriormente)
                
                            if (JUNCOES_HIDROGRAMAS[i][numero_hidrograma] in ORDEM_EXECUCAO_PQ): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de alguma PQ
                                indice_hidrograma_entrada = ORDEM_EXECUCAO_PQ.index(JUNCOES_HIDROGRAMAS[i][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_PQ[indice_hidrograma_entrada][valor]
                        
                            elif(JUNCOES_HIDROGRAMAS[i][numero_hidrograma] in ORDEM_EXECUCAO_PULS): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de algum PULS
                                indice_hidrograma_entrada = ORDEM_EXECUCAO_PULS.index(JUNCOES_HIDROGRAMAS[i][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_PULS[indice_hidrograma_entrada][valor]
                            
                            elif(JUNCOES_HIDROGRAMAS[i][numero_hidrograma] in ORDEM_EXECUCAO_MKC): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de algum MKC
                                indice_hidrograma_entrada = ORDEM_EXECUCAO_MKC.index(JUNCOES_HIDROGRAMAS[i][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_MKC[indice_hidrograma_entrada][valor]
                                    
                            elif (JUNCOES_HIDROGRAMAS[i][numero_hidrograma] in ORDEM_EXECUCAO_JUNCAO): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de outra JUNCAO
                                indice_hidrograma_entrada = ORDEM_EXECUCAO_JUNCAO.index(JUNCOES_HIDROGRAMAS[i][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma_entrada][valor]
                
                        #POR ENQUANTO DEIXA DESATIVADO
                    #   Se entrar aqui, e' pra entrar com um hidrograma observado...
                    else:  #e' um hidrograma observado, deve-se ler o arquivo.
                            #contar quantas linhas tem o arquivo
                        numero_linhas  = sum(1 for linha in open(JUNCOES_HIDROGRAMAS[i][numero_hidrograma],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                        
                            #Nao sei se isto e' necessario, mas se o arquivo fornecido pelo usuario nao tiver o mesmo numero de termos que NUMERO_INTERVALOS_TEMPO, o programa deve ser finalizado, pois nao sei como proceder neste caso.
                        if (not numero_linhas == NUMERO_INTERVALOS_TEMPO): #ERRO?
                            tkMessageBox.showinfo("Verifique os arquivos de entrada das operações Junção!", "Um dos hidrogramas fornecidos pelo usuário (arquivo .txt) não tem o mesmo número de termos (linhas) que o número de intervalos de tempo da simulação.") #"Voce e' burro." ahahhahahaha
                            tkMessageBox.showinfo("O modelo será finalizado.", "Revise os arquivos de hidrogramas e tente novamente.\nDica: Não deixe linhas em branco no final do arquivo.") #"Voce e' burro." ahahhahahaha
                            self.ragequit()
                        
                        arquivo_hidrograma = open(JUNCOES_HIDROGRAMAS[i][numero_hidrograma], 'r') #abrir o arquivo para le-lo.
                        
                            #loop para ler linhas do arquivo da curva cota-volume
                        for linha in xrange(numero_linhas):
                            conteudo_hidrograma = arquivo_hidrograma.readline().split(";")            #ler a linha e dividir 
                            valores_hidrogramas_da_juncao[numero_hidrograma][linha] = float(conteudo_hidrograma[0])        #valores de hidrograma
                        
                        arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.

                #   Fazer algoritmo para escrever o conteudo no arquivo de saida
                
                #    saber qual e' o indice da operacao em ordem crescente-----> e' diferente da ordem da execucao.....
                indice_hidrograma_saida = ORDEM_EXECUCAO_JUNCAO.index(i)  #usado pra variavel de saida do juncao
                
                saidaJUNCAO.write("\n\n\n\t\t--- HIDROGRAMAS SOMADOS NESTA JUNCAO ---\n\n")
                
                for cabecalho in xrange(len(JUNCOES_HIDROGRAMAS[i])):
                    if type(JUNCOES_HIDROGRAMAS[i] == int):
                        saidaJUNCAO.write("Hidrograma " + (str(cabecalho+1)) + ": " + str((JUNCOES_HIDROGRAMAS[i][cabecalho]) + 1) + "\n")
                    else:
                        saidaJUNCAO.write("Hidrograma " + (str(cabecalho+1)) + ": " + str(JUNCOES_HIDROGRAMAS[i][cabecalho]) + "\n")
                
                saidaJUNCAO.write("\n\n\t\t\t---- DETALHAMENTO ----\n\n")
                        
                aux = ["   HIDResultante"] #precisa ser declarada
                    
                #   Loop para montar o cacecalho do detalhamento
                for x in xrange( len(JUNCOES_HIDROGRAMAS[i]) ):
                    if x >= 9:
                        aux = aux +[" Hidrograma" + str(x+1)]
                        
                    else:
                        aux = aux +["  Hidrograma" + str(x+1)]
                            
                saidaJUNCAO.write("      dt"+ ' '.join(aux)) 
                saidaJUNCAO.write("\n")
                
                #   Loop para as linhas
                for valor in xrange(NUMERO_INTERVALOS_TEMPO):
                    saidaJUNCAO.write( "%8d, %14.8f" %((valor+1), HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma_saida][valor]) )
                
                    #   Loop para colunas
                    for numero_hidrograma in xrange(len(JUNCOES_HIDROGRAMAS[i])):
                        saidaJUNCAO.write( "%14.8f" %(valores_hidrogramas_da_juncao[numero_hidrograma][valor])) #varia o hidrograma e o intervalo de tempo fica fixo.
                    saidaJUNCAO.write("\n")
                
            #pbar.update(i + 1)
        #pbar.finish()

        saidaJUNCAO.close()
                
#-----------------------------------------------------------
    
    def lerArquivoEntrada(self):
        

        
        #conteudo_linha = self.arquivo_entrada.readline().split(";") # so' leio, mas nao faco nada com isso....
        conteudo_linha = self.arquivo_entrada.readline().split(";") # so' leio, mas nao faco nada com isso....
        
        while str(conteudo_linha[0]) != "INICIO": #possibilita criar um cabecalho com quantas linhas o usuario desejar
            conteudo_linha = self.arquivo_entrada.readline().split(";")
        
        if conteudo_linha[0] == "INICIO": #E' CRUCIAL QUE EXISTA UMA LINHA DO ARQUIVO DE ENTRADA QUE COMECE COM "INICIO;" (SEM ACENTO E EM LETRAS MAIUSCULAS) PARA QUE O PROGRAMA COMECE A TRABALHAR
                
                #parametros gerais
            NUMERO_INTERVALOS_TEMPO       = int(conteudo_linha[1])  #numero de intervalos de tempo
            DURACAO_INTERVALO_TEMPO       = int(conteudo_linha[2])  #duracao do delta t em segundos
            NUMERO_CHUVAS                 = int(conteudo_linha[3])  #numero de postos de chuva (numero de IDF's)
            NUMERO_INTERVALOS_TEMPO_CHUVA = int(conteudo_linha[4])  #duracao da chuva
            NUMERO_OPERACOES_HIDROLOGICAS = int(conteudo_linha[5])  #numero de operacoes hidrologicas
            CONTROLE_HIDROGRAMAS          = [0 for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)] #armazena 0 e 1; Se 0 -> operacao nao calculada; Se 1 -> operacao calculada.
            
            
                #variaveis da logica do programa
            ORDEM_OPERACOES_HIDROLOGICAS  = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)] #sera' substituido pelo codigo das operacoes: "PQ, PULS, MKC...."
#            CHUVA_OPERACAO_CORRESPONDENTE = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)] #sera' substituido pelo numero da chuva que a operacao sera feita
            CHUVA_OPERACAO_CORRESPONDENTE = [None for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)] #sera' substituido pelo numero da chuva que a operacao sera feita
            CHUVA_IDF_OU_OBS              = [0. for i in xrange(NUMERO_CHUVAS)] #recebera "IDF" ou "OBS"... Sera' zero se nao utilizada
            NOMES_OPERACOES_HIDROLOGICAS  = ["nome nao informado" for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)] #usado nas plotagens
            NUMERO_PORD                   = [] #guardara quantas e quais P_ord terei. Esta variavel difere da CHUVA_OPERACAO_CORRESPONDENTE pois ela nao guarda elementos repetidos
            
            
                #variaveis das IDFs
            PARAMETRO_A = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            PARAMETRO_B = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            PARAMETRO_C = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            PARAMETRO_D = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            TIPO_IDF    = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            POSPICO     = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            TR          = [0. for i in xrange(NUMERO_CHUVAS)] #se for chuva observada, os parametros serao 0.0
            
            
                    #Variaveis das operacoes hidrologicas
                    
                #Chuva-Vazao
            HIDROGRAMAS_SAIDA_PQ    = None
            ORDEM_EXECUCAO_PQ       = []                                                   #deixe esta variável assim mesmo, sem tamanho declarado. Armazena postos ORDENADOS
            CONTROLE_HIDROGRAMAS_PQ = []                                                   #deixe esta variável assim mesmo, sem tamanho declarado. Armazena postos PQ NAO ordenados
            CN                      = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #CN somente e' utilizado no chuva-vazao, se a operacao nao for de chuva-vazao, o valor do CN e' ZERO
            AREA                    = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #se nao for usado, seu valor sera' zero.
            TC                      = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #se nao for usado, seu valor sera' zero.
                #Chuva-vazao e Muskingun-Cunge
            DIFERENCA_COTA          = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #se nao for usado, seu valor sera' zero.
            COMPRIMENTO_CANAL       = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #se nao for usado, seu valor sera' zero.


                #PULS
            HIDROGRAMAS_SAIDA_PULS      = None
            ORDEM_EXECUCAO_PULS         = []                                                   #deixe esta variável assim mesmo, sem tamanho declarado. Armaneza as operacoes puls sem ORDENADA
            CONTROLE_HIDROGRAMAS_PULS   = []                                                   #deixe esta variável assim mesmo, sem tamanho declarado. Armaneza as operacoes puls sem NAO ORDENADA
            CURVA_COTA_VOLUME           = []                                                   #Armazenara' todos os valores de todas as curvas cota-volume.... cada termo dela e' uma curva.
            ESTRUTURAS_PULS             = [0 for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]   #ARMAZENA O NUMERO DE ESTRUTURAS DE SAIDA DE CADA PULS, SE FOR 0 E' PORQUE ESTA OPERACAO NAO E' PULS
#            COTAS_FUNDO                 = [0 for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]   #ARMAZENA AS COTAS DE FUNDO DOS RESERVATORIOS. SE O VALOR FOR INTEIRO E' PORQUE NAO E' OPERACAO DE PULS
            COTAS_INICIAIS              = [0 for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]   #ARMAZENA AS COTAS INICIAIS DOS PULS.... SE FOR 0 E' PORQUE A OPERACAO NAO E' PULS (OU A COTA REALMENTE E' ZERO)
            HIDROGRAMAS_ENTRADA_PULS    = ['' for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]  #VAI SER TUDO ''... AS OPERACOES DE PULS RECEBERAM NUMERO OU DIRETORIO, SE FICAR '' E' PORQUE NAO A OPERACAO NAO E' DE PULS
                                                                                               #Esta variavel nao e' declarada com 0, pois 0 e' usado no python como posicao de variaveis.  

            
                #MUSKINGUM-CUNGE
            HIDROGRAMAS_SAIDA_MKC      = None
            ORDEM_EXECUCAO_MKC         = []                                                     #deixe esta variável assim mesmo, sem tamanho declarado. Armazena postos ORDENADOS
            CONTROLE_HIDROGRAMAS_MKC   = []                                                     #deixe esta variável assim mesmo, sem tamanho declarado.
            HIDROGRAMAS_ENTRADA_MKC    = ['' for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]    #VAI SER TUDO ''... AS OPERACOES DE MKC RECEBERAM NUMERO OU DIRETORIO, SE FICAR '' E' PORQUE NAO A OPERACAO NAO E' DE MKC
            LARGURA_CANAL              = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]   #armazena a largura dos canais, em metro
            COEF_RUGOSIDADE            = [0. for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]   #armazena os coeficientes de rugosidade dos canais (operacoes MKC)
            
            
                #JUNCAO
            HIDROGRAMAS_SAIDA_JUNCAO    = None
            JUNCOES_HIDROGRAMAS         = [0 for i in xrange(NUMERO_OPERACOES_HIDROLOGICAS)]     #armazena em listas as juncoes. Cada lista e' uma juncao, que pode ser de ate' 5 hidrogramas.
            ORDEM_EXECUCAO_JUNCAO       = []                                                     #deixe esta variável assim mesmo, sem tamanho declarado. Armazena postos ORDENADOS
            CONTROLE_HIDROGRAMAS_JUNCAO = []                                                     #deixe esta variável assim mesmo, sem tamanho declarado.
        
        conteudo_linha = self.arquivo_entrada.readline().split(";") #ler a segunda linha, deve ser a dos cenarios....
        CENARIOS_ANOS = [] #auxiliar do Cenarios, possui QUAIS os anos de cenarios
        
        
        if conteudo_linha[0] == "CENARIOS": # informacoes dos cenarios
            
            if ((conteudo_linha[1] != " 0") and (conteudo_linha[1] != '') and (conteudo_linha[1] != '0') and (conteudo_linha[1] != '\n')):    
                for i in xrange(1, len(conteudo_linha)):
                    
                    if ((conteudo_linha[i] != '0') and (conteudo_linha[i] != ' 0') and (conteudo_linha[i] != '') and (conteudo_linha[i] != '\n')): #cenario 0 nao rola....
                        CENARIOS_ANOS.append(int(conteudo_linha[i]))


        numero_blocos = (NUMERO_CHUVAS + NUMERO_OPERACOES_HIDROLOGICAS) #saber quantos blocos de linhas deverei ler... cada bloco pode ser uma chuva ou uma operacao
        
        print "\n\n\tLendo arquivo de entrada."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(numero_blocos)).start()
        
        for i in xrange(numero_blocos): #botar barra de progresso para leitura do arquivo de entrada
            conteudo_linha = self.arquivo_entrada.readline().split(";") #lera' "CHUVA" ou "OPERACAO" e a chuva que corresponde

            #*--------------------------------- Ler CHUVA ---------------------------------*#
            
            if conteudo_linha[0] == "CHUVA": #e' pra colocar chuva observada ou idf
                numero_chuva_correspondente = (int(conteudo_linha[1]) -1)
                conteudo_linha = self.arquivo_entrada.readline().split(";") #ler IDF e parametros ou OBS
                        
                if conteudo_linha[0] == "IDF":
                    
                    CHUVA_IDF_OU_OBS[numero_chuva_correspondente] = "IDF"
                    
                    TIPO_IDF[numero_chuva_correspondente] = (int(conteudo_linha[1]))
                    POSPICO[numero_chuva_correspondente]  = (float(conteudo_linha[2])) #muda em cada posto
                    TR[numero_chuva_correspondente]       = (int(conteudo_linha[3])) #muda em cada posto
                            
                    PARAMETRO_A[numero_chuva_correspondente] = float(conteudo_linha[4])
                    PARAMETRO_B[numero_chuva_correspondente] = float(conteudo_linha[5])
                    PARAMETRO_C[numero_chuva_correspondente] = float(conteudo_linha[6])
                    PARAMETRO_D[numero_chuva_correspondente] = float(conteudo_linha[7])
                            
                elif conteudo_linha[0] == "OBS": #depois eu faco
                    
                    CHUVA_IDF_OU_OBS[numero_chuva_correspondente] = "OBS"
                    
                    raw_input("Foi detectado um erro no manejo dos dados de chuva observada e por isso esta funcionalidade foi desativada.\nEla sera' corrigida e reativada em versoes futuras.")
                    self.ragequit()

            #*--------------------------------- Ler OPERACAO ---------------------------------*#
                
            elif conteudo_linha[0] == "OPERACAO": #e' uma operacao hidrologica
                numero_operacao = (int(conteudo_linha[1]) -1) #guarda a ordem que as operacoes sao entradas no programa.... e' o valor seguido de "OPERACAO;"
                
                if len(conteudo_linha) >= 3: 
                    NOMES_OPERACOES_HIDROLOGICAS[numero_operacao] = str(conteudo_linha[2]) #o nome e' o terceiro termo da linha
                    
                conteudo_linha = self.arquivo_entrada.readline().split(";") #ler qual operacao (PQ, PULS....) e qual e' a chuva que ela utiliza
                    
                #*--------------------------------- Ler PQ ---------------------------------*#

                if conteudo_linha[0] == "PQ":
                    
                    CONTROLE_HIDROGRAMAS_PQ.append(numero_operacao)  #ja' esta' reduzido 1!
                    operacao_usa_chuva = int(conteudo_linha[1]) #guarda o numero que nos diz qual chuva sera' usada nesta operacao
                    
                    ORDEM_OPERACOES_HIDROLOGICAS[numero_operacao]  = "PQ"
                    CHUVA_OPERACAO_CORRESPONDENTE[numero_operacao] = operacao_usa_chuva - 1
                    
                    conteudo_linha = self.arquivo_entrada.readline().split(";") #le qual sera o algoritmo de separacao de escoamento utilizado (1:CN-SCS, se CN do LADO o valor do CN)
                    
                    if conteudo_linha[0] == "CN":
                        CN[numero_operacao] = float(conteudo_linha[1])
                    
                    else:
                        raw_input("Algoritmo de separacao de escoamento nao identificada. \nPressione enter para fechar o programa.")
                        self.ragequit()
                    
                    conteudo_linha = self.arquivo_entrada.readline().split(";") #le qual sera' o algoritmo de propagacao do escoamento superficial e valores de tc
                    
                    if conteudo_linha[0] == "HUT":
                        AREA[numero_operacao] = float(conteudo_linha[1])
                        
                        if conteudo_linha[2] == "KIRPICH":
                            
                            DIFERENCA_COTA[numero_operacao]    = float(conteudo_linha[3])
                            COMPRIMENTO_CANAL[numero_operacao] = float(conteudo_linha[4])
                            
                            TC[numero_operacao] = Hydrolib.calcular_TC_Kirpich( DIFERENCA_COTA, COMPRIMENTO_CANAL )
                        
                        else: #entrando com TC em horas
                            TC[numero_operacao] = float(conteudo_linha[2])
                            
                #*--------------------------------- Ler PULS ---------------------------------*#
                                                
                elif conteudo_linha[0] == "PULS":  #OPERACAO DE PULS!!!
                    
                    CONTROLE_HIDROGRAMAS_PULS.append(numero_operacao) #ja' esta' reduzido 1!
                    ORDEM_OPERACOES_HIDROLOGICAS[numero_operacao]  = "PULS"
                    
                    try:
                        HIDROGRAMAS_ENTRADA_PULS[numero_operacao] = (int(conteudo_linha[1]) - 1) #variavel que armazena os hidrogramas que entrarao nas operacoes puls (ja' esta reduzido 1!!).... se esta variavel tiver valor '' significa que esta operacao nao e' puls
                        
                    except:
                        while (conteudo_linha[1][0] == ' '): #correcao de bug: se o diretorio fornecido pelo usuario comecar com espaco ' ', o programa nao encontra o arquivo
                            conteudo_linha[1] = conteudo_linha[1][1:]  #remover todos os espacos que estao antes do diretorio
                        
                        HIDROGRAMAS_ENTRADA_PULS[numero_operacao] = conteudo_linha[1] #variavel que armazena os hidrogramas que entrarao nas operacoes puls (EM STRING!!).... se esta variavel tiver valor '' significa que esta operacao nao e' puls
                    
#                    COTAS_FUNDO[numero_operacao] = float(conteudo_linha[2])    
                    COTAS_INICIAIS[numero_operacao] = int(conteudo_linha[2]) #armazenar a cota inicial desta operacao puls... se for 0 nao e' puls (pode ser que seja, com cota inicial zero)
                    estruturas_desta_operacao = [[0,0,0,0,0] for i2 in xrange(int(conteudo_linha[3]))] #variavel que deve ser resetada a cada nova operacao puls
                    
                    for estrutura in xrange(int(conteudo_linha[3])):
                        conteudo_linha = self.arquivo_entrada.readline().split(";")          #ler cada estrutura
                        estruturas_desta_operacao[estrutura][0] = (conteudo_linha[0])        #Armazenar "VERTEDOR" ou "ORIFICIO"
                        estruturas_desta_operacao[estrutura][1] = (float(conteudo_linha[1])) #Armazenar coeficiente da estrutura
                        estruturas_desta_operacao[estrutura][2] = (float(conteudo_linha[2])) #Armazenar informacoes da estrutura
                        estruturas_desta_operacao[estrutura][3] = (float(conteudo_linha[3])) #Armazenar informacoes da estrutura
                        estruturas_desta_operacao[estrutura][4] = (float(conteudo_linha[4])) #Armazenar informacoes da estrutura
                        
                    ESTRUTURAS_PULS[numero_operacao] = (estruturas_desta_operacao) #ORGANIZADA DE MANEIRA QUE CADA TERMO E' UMA OPERACAO, E CADA LISTA DENTRO DE CADA TERMO E' UMA ESTRUTURA
                        #                                                                                                              #
                        #     Exemplo: 3 operacoes: A primeira com 3 estruturas. A segunda com 1 estrutura. A terceira com 2 estruturas#
                        #ESTRUTURAS_PULS = [ [ [],[],[] ], [ [] ], [ [],[] ] ]  <--- Estrutura da variavel                             #
                        #                    (          ), (    ), (       )   <--- Conteudo de cada OPERACAO                          #
                        #                      (),(),()      ()      (),()   <--- Conteudo de cada ESTRUTURA                           #
                        ################################################################################################################
                        
                    conteudo_linha = self.arquivo_entrada.readline().split(";") #ler o diretorio do arquivo de cota-vazao
 
                    diretorio_curva_cotavolume = conteudo_linha[0]  #diretorio armazenado, abra ele agora.
                    
                        #contar quantas linhas tem o arquivo
                    numero_linhas    = sum(1 for linha in open(diretorio_curva_cotavolume,'r'))      #contar o numero de linhas do arquivo da curva cota-volume
                    curva_provisoria = [[0 for i3 in xrange(numero_linhas)] for i4 in xrange(2)]     #cria uma lista com 2 termos, cada um deles com numero_linhas linhas.
                    arquivo_curva    = open(diretorio_curva_cotavolume, 'r')                         #abrir o arquivo para le-lo.
                    
                        #loop para ler linhas do arquivo da curva cota-volume
                    for linha in xrange(numero_linhas):
                        conteudo_curva = arquivo_curva.readline().split(";")    #ler a linha e dividir 
                        curva_provisoria[0][linha] = float(conteudo_curva[0])   #valores de cota
                        curva_provisoria[1][linha] = float(conteudo_curva[1])   #valores de volume
                    
                    arquivo_curva.close() #fechar o arquivo -> poupar memoria.
                    CURVA_COTA_VOLUME.append(curva_provisoria) #somente havera' curva se for puls, logo, usar contador manual aqui.###############################################
                        #                                                                                                                                                        #
                        #CURVA_COTA_VOLUME = [ [ [...],[...] ], [ [...],[...] ], [ [...],[...] ], ... ]                                                                          #
                        #                      (             ), (             ), (             )  <--- Conteudo de cada curva cota-volume, cada puls com seu (    )              #
                        #                        (...),(...)      (...),(...)      (...),(...)    <--- Conteudo das curvas, o primeiro (...) e' cota, o segundo (...) e' volume. #
                        ##########################################################################################################################################################
                    
                #*--------------------------------- Ler MKC ---------------------------------*#
                                                
                elif conteudo_linha[0] == "MKC":  #OPERACAO DE MUSKINGUN-CUNGE!!
                    
                    CONTROLE_HIDROGRAMAS_MKC.append(numero_operacao) #ja' esta' reduzido 1!
                    ORDEM_OPERACOES_HIDROLOGICAS[numero_operacao]  = "MKC"
                    
                    try:
                        HIDROGRAMAS_ENTRADA_MKC[numero_operacao] = (int(conteudo_linha[1]) - 1) #variavel que armazena os hidrogramas que entrarao nas operacoes mkc (ja' esta reduzido 1!!).... se esta variavel tiver valor '' significa que esta operacao nao e' mkc
                        
                    except:
                        while (conteudo_linha[1][0] == ' '): #correcao de bug: se o diretorio fornecido pelo usuario comecar com espaco ' ', o programa nao encontra o arquivo
                            conteudo_linha[1] = conteudo_linha[1][1:]  #remover todos os espacos que estao antes do diretorio
                        
                        HIDROGRAMAS_ENTRADA_MKC[numero_operacao] = conteudo_linha[1] #variavel que armazena os hidrogramas que entrarao nas operacoes mkc (EM STRING!!).... se esta variavel tiver valor '' significa que esta operacao nao e' mkc
                    
                    DIFERENCA_COTA[numero_operacao]    = float(conteudo_linha[2]) #armazenar a diferenta de cota do canal em metros.
                    COMPRIMENTO_CANAL[numero_operacao] = float(conteudo_linha[3]) #armazenar o comprimento do canal em quilometros.
                    LARGURA_CANAL[numero_operacao]     = float(conteudo_linha[4]) #armazenar a largura canal em metros.
                    COEF_RUGOSIDADE[numero_operacao]   = float(conteudo_linha[5]) #armazenar o coeficiente de rugosidade de manning.
                
                #*--------------------------------- Ler JUNCAO ---------------------------------*#
                
                #OPERACAO; n; Nome/local operacao
                #JUNCAO;2;3;    ou    #JUNCAO;2;3;;;;
                
                elif conteudo_linha[0] == "JUNCAO": #OPERACAO DE JUNCAO DE HIDROGRAMAS
                    
                    CONTROLE_HIDROGRAMAS_JUNCAO.append(numero_operacao) #numero_operacao ja' esta' com 1 reduzido.
                    ORDEM_OPERACOES_HIDROLOGICAS[numero_operacao]  = "JUNCAO"

                    #   E' -2 pois o primeiro termo e' a escrita "JUNCAO" e o ultimo e' um enter (que sempre ha' apos o ultimo ;) 
                    if conteudo_linha[-1] == ";" :
                        hidrogramas_juncao = [-1 for indices in xrange((len(conteudo_linha)-1))] # Vai ser sempre [ -1, -1, -1, ... ]; Fazer as verificacoes com >= 0 !!!
                        
                    else:
                        hidrogramas_juncao = [-1 for indices in xrange((len(conteudo_linha)-2))] # Vai ser sempre [ -1, -1, -1, ... ]; Fazer as verificacoes com >= 0 !!!
                    
                    #   Loop dos hidrogramas
                    for ler_hid in xrange(1,(len(conteudo_linha)-1)): #vai de 1 a len(conteudo_linha)-1 pois tem um enter depois do ultimo ; 
                        
                        try:
                            hidrogramas_juncao[(ler_hid-1)] = (int(conteudo_linha[ler_hid]) - 1) #sempre reduzir 1 pois os indices em python comecam em ZERO.
                        
 
                        except ValueError: #nao consegue converter o conteudo em numero: caso -> JUNCAO;x;y;;;;
                            
                            while (conteudo_linha[(ler_hid)][0] == ' '): #correcao de bug: se o diretorio fornecido pelo usuario comecar com espaco ' ', o programa nao encontra o arquivo
                                conteudo_linha[ler_hid] = conteudo_linha[ler_hid][1:]  #remover todos os espacos que estao antes do diretorio
                                
                            hidrogramas_juncao[(ler_hid-1)] = str(conteudo_linha[ler_hid]) #caso ter texto escrito (diretorio entrada)
                            
                            
                        except IndexError: #nao ha' mais termos na linha: caso -> JUNCAO;x;y; .... Deve ocorrer se nenhum numero for colocado ou ';' estiver faltando.....
                            hidrogramas_juncao[(ler_hid-1)] = -1
                        
                        #Armazenar os numeros dos hidrogramas que serao somados.
                    JUNCOES_HIDROGRAMAS[numero_operacao] = hidrogramas_juncao
                
                
            #pbar.update(i + 1)
        #pbar.finish()
            
        ############# --- terminei de ler tudo. --- #############
        
        ############# --- CRIAR VARIAVEIS DAS RESPOSTAS --- #############
            
                #As variaveis somente sao criadas se necessario (se houver a operacao no arquivo de entrada)
                #Aqui tambem e' o espaco destinado para preparacao de variaveis que serao utilizadas nas operacoes e plotadas na saida, logo devem ser declaradas e armazenadas.
                
            #PQ
        if "PQ" in ORDEM_OPERACOES_HIDROLOGICAS:
            
                #Logica para verificar quantas series de Pord serao necessarias (objetivo: alcancar o menor numero possivel. Se alguma repetir, nao calcularemos de novo);
            for i in xrange(len(ORDEM_OPERACOES_HIDROLOGICAS)):
                if ((ORDEM_OPERACOES_HIDROLOGICAS[i] == "PQ") and (not CHUVA_OPERACAO_CORRESPONDENTE[i] in NUMERO_PORD)): #ou seja, se for operacao PQ ->E<- ela nao esta' nas numero_pord;
                    NUMERO_PORD.append(CHUVA_OPERACAO_CORRESPONDENTE[i]) #aqui eu terei somente UM numero de cada posto que FOR DA OPERACAO PQ
                    
                #Crio as variaveis com zeros (armazenar espaco na memoria)
            HIDROGRAMAS_SAIDA_PQ, PRECIPITACAO_ORDENADA = self.criarVariaveisPQ(ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO, NUMERO_PORD)
            
                    #calcular as series de chuvas ordenadas
            print "\n\n\tCalculando series de chuva ordenadas."
            #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(len(NUMERO_PORD))).start()
        
                #aqui e' para calcular as Pord. Uma de cada que for necessaria. Caso duas operacoes utilizem a mesma Pord, utilizo a mesma lista em ambas operacoes;
            for i in xrange(len(NUMERO_PORD)):
                dados_utilizados = ( int(NUMERO_PORD[i]) )
                
#                print "\n"
#                print "dados_utilizados = " + str(dados_utilizados)
#                print "CHUVA_OPERACAO_CORRESPONDENTE = " + str(CHUVA_OPERACAO_CORRESPONDENTE)
#                print "NUMERO_PORD = " + str(NUMERO_PORD)
#                print "PARAMETRO_A = " + str(PARAMETRO_A)
#                print "\n"
                
                
                
                
                PRECIPITACAO_ORDENADA[i][:] = self.gerarPrecipOrdenada( NUMERO_INTERVALOS_TEMPO_CHUVA, 
                                                                        DURACAO_INTERVALO_TEMPO, 
                                                                        PARAMETRO_A[dados_utilizados], 
                                                                        PARAMETRO_B[dados_utilizados], 
                                                                        PARAMETRO_C[dados_utilizados], 
                                                                        PARAMETRO_D[dados_utilizados],
                                                                        POSPICO[dados_utilizados], 
                                                                        TR[dados_utilizados]         )
                #pbar.update(i + 1)    #isto e' da barra de progresso
            #pbar.finish()            #isto e' da barra de progresso
        
            #-----------------------------------------------------------------------------------------------------------------------
            
                #        1 - Calcular cenarios SE habilitado.... logica aqui vai ser substituida a fim de poupar memoria... 
                #        2 - O programa trabalha de passo em passo, mas para os cenarios, calcularemos de posto em posto, escrevendo o arquivo de saida assim que todos os cenarios de 
                #    um posto forem calculadas (desta forma, eu economizo em espaco na minha matriz que armazena os resultados).

            
            if len(CENARIOS_ANOS) > 0 : #tem cenarios? 
                
                print "\n\n\tCalculando chuva-vazao para os anos dos cenarios."
                #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=((NUMERO_OPERACOES_HIDROLOGICAS*len(CENARIOS_ANOS)))).start()
                
                for operacao in xrange(NUMERO_OPERACOES_HIDROLOGICAS): #em todas as operacoes
                    
                    if ORDEM_OPERACOES_HIDROLOGICAS[operacao] == "PQ":  #somente as operacoes PQ
                        
                        CEN_HIDROGRAMAS_SAIDA = [[0. for x in xrange(NUMERO_INTERVALOS_TEMPO)] for x2 in xrange(len(CENARIOS_ANOS))] #declarar a variavel que armazenara' os resultados (hidrogramas)
                        dados_utilizados = ( int(CHUVA_OPERACAO_CORRESPONDENTE[operacao]) ) #saber qual serie de dados dentre as series de dados que sera' usada nesta simulacao de chuva vazao
                        
                        for calculos in xrange(len(CENARIOS_ANOS)):
                            
                            CEN_P_ORD = self.gerarPrecipOrdenada( NUMERO_INTERVALOS_TEMPO_CHUVA, 
                                                                  DURACAO_INTERVALO_TEMPO, 
                                                                  PARAMETRO_A[dados_utilizados], 
                                                                  PARAMETRO_B[dados_utilizados], 
                                                                  PARAMETRO_C[dados_utilizados], 
                                                                  PARAMETRO_D[dados_utilizados], 
                                                                  POSPICO[dados_utilizados], 
                                                                  CENARIOS_ANOS[calculos]      )
                                                                  
                            CEN_HIDROGRAMAS_SAIDA[calculos] = self.rodarCenariosPQ( NUMERO_INTERVALOS_TEMPO_CHUVA, 
                                                                                    NUMERO_INTERVALOS_TEMPO, 
                                                                                    DURACAO_INTERVALO_TEMPO, 
                                                                                    CN[operacao], 
                                                                                    TC[operacao], 
                                                                                    AREA[operacao], 
                                                                                    CEN_P_ORD                    ) #operacao recebe o valor da operacao feita no loop. Ele vai servir pra dizer a algumas variaveis qual valor deve ser pego nesta operacao.
                                                                                    
                            #pbar.update( ((calculos+1)+((operacao)*len(CENARIOS_ANOS))) )    #isto e' da barra de progresso

                        self.escreverSaidaCENARIOS( CEN_HIDROGRAMAS_SAIDA, 
                                                    CENARIOS_ANOS, 
                                                    ORDEM_OPERACOES_HIDROLOGICAS, 
                                                    NUMERO_INTERVALOS_TEMPO, 
                                                    NUMERO_INTERVALOS_TEMPO_CHUVA, 
                                                    DURACAO_INTERVALO_TEMPO, 
                                                    NOMES_OPERACOES_HIDROLOGICAS[operacao] )

                        #if (self.plotar_graficos) == 1:
                            #Plotar grafico chuva vazao da operacao
                            #plotagem (TC, Hidrograma, P, Pef, QIDF, nint_tempo, dt, pathname,nome_posto,simulacao) 
                            #se e' algo que ja' esta' definido anter de rodar o programa, usa-se [dados_utilizados]; Se e' algo que esta' definido agora (como HIDROGRAMAS), usa-se [contador_manual];
                            
                        Hydrolib.plotar_Cenarios_PQ( CEN_HIDROGRAMAS_SAIDA, 
                                                         CENARIOS_ANOS, 
                                                         NUMERO_INTERVALOS_TEMPO, 
                                                         self.caminho_arquivo_entrada,
                                                         NOMES_OPERACOES_HIDROLOGICAS[operacao], 
                                                         (operacao+1)                          )
    
                #pbar.finish()            #isto e' da barra de progresso
                
                        
            #PULS
        if "PULS" in ORDEM_OPERACOES_HIDROLOGICAS:
            HIDROGRAMAS_SAIDA_PULS = self.criarVariaveisPULS(ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO)
        
            #Muskigun-Cunge
        if "MKC" in ORDEM_OPERACOES_HIDROLOGICAS:
            HIDROGRAMAS_SAIDA_MKC  = self.criarVariaveisMKC(ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO)
         
            #Juncao de hidrogramas
        if "JUNCAO" in ORDEM_OPERACOES_HIDROLOGICAS:
            HIDROGRAMAS_SAIDA_JUNCAO = self.criarVariaveisJUNCAO(ORDEM_OPERACOES_HIDROLOGICAS, NUMERO_INTERVALOS_TEMPO)
            
        ############# --- terminei de criar e calcular cenarios (se houverem) --- #############
        
        ############# --- BOTAR O PROGRAMA PRA RODAR AS OPERACOES HIDROLOGICAS (PQ, PULS E MKC)--- #############
        

            #calcular as operacoes hidrologicas
        print "\n\n\tCalculando operacoes hidrologicas."
        #pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=(NUMERO_OPERACOES_HIDROLOGICAS)).start()
        
        contador_manual_pq     = 0 #usada como variavel de posicao para HIDROGRAMAS_SAIDA_PQ, PRECIPITACAO_ORDENADA e OUTRAS... (elas nao tem NUMERO_OPERACOES_HIDROLOGICAS termos, economizando memoria)
        contador_manual_puls   = 0 #usada como variavel de posicao para HIDROGRAMAS_SAIDA_PULS (que nao tem NUMERO_OPERACOES_HIDROLOGICAS termos, economizando memoria)
        contador_manual_mkc    = 0 #usada como variavel de posicao para HIDROGRAMAS_SAIDA_MKC  (que nao tem NUMERO_OPERACOES_HIDROLOGICAS termos, economizando memoria)
        contador_manual_juncao = 0 #usada como variavel de posicao para HIDROGRAMAS_SAIDA_JUNCAO (que nao tem NUMERO_OPERACOES_HIDROLOGICAS termos, economizando memoria)
        
            #loop para rodar operacoes.... selecionar a que deve ser calculada antes e meter bala.
        for operacao in xrange(NUMERO_OPERACOES_HIDROLOGICAS): #aqui eu coloco a barra de progresso para processos
            
                    #            O algoritmo a seguir serve para que o modelo acerte a ordem de execucao das operacoes hidrologicas, pois desta forma, o usuario
                    #    pode entrar com as operacoes em ordem aleatoria, que mesmo assim o programa sabera' qual deve ser calculada antes. A seguir segue um exemplo
                    #    de como o algorimo funciona: Operacao 5 recebe o resultado da operacao 9, a operacao 9 por sua vez, precisa do hidrograma gerado pela operacao 3,
                    #    entao, o modelo calculara' a operacao 3, em seguida, a operacao 9 e por final a operacao 5. Apos, ele seguira' normalmente, pulando aquelas
                    #    operacoes que ja' foram calculadas.
            
            operacao_a_calcular = 0 #comeca sempre em zero, assim, eu garanto que nao faltara' nenhuma operacao (ao custo de ter que que rodar varios while's ate' achar uma operacao nao calculada).
            decisao = False         #variavel que diz se o modelo ja' decidiu qual operacao calcular.
    
            while(decisao == False): #assumo que o programa nao sabe qual operacao calcular. Este loop e' rodado VARIAS vezes antes de calcular cada operacao.

                if CONTROLE_HIDROGRAMAS[operacao_a_calcular] == 1: #se cair aqui e' porque a operacao ja' foi calculada... verifique a proxima
                    operacao_a_calcular += 1                       #somar um para verificar a proxima
                    decisao = False                                #Esta linha nao e' necessaria, mas e' so' pra lembrar o programador de que a decisao continua falsa
                    
                else: # Se cair aqui, e' porque a operacao que esta' sendo avaliada ainda nao foi calculada.
                    
                    
                        ########## ------ Para PQ  ------ ########
                    if(ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "PQ"): #se for uma operacao de PQ, pode calcular, pois PQ depende somente de CHUVA e nao de outras operacoes.
                        decisao = True                                             #PQ pode calcular
                        ORDEM_EXECUCAO_PQ.append(operacao_a_calcular)              #adiciona a operacao para o controle
                    
                    
                        ########## ------ Para PULS  ------ ########
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "PULS"): #se for uma operacao PULS, avaliar se o hidrograma de entrada dela e' oriundo de outra operacao ou fornecido pelo usuario
                        
                        if (not (type(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular]) == int)): #Se nao for 'int', e' porque e' dado por pelo usuario, logo, pode calcular sem problema algum.
                            decisao = True                                                      #Manda bala!
                            ORDEM_EXECUCAO_PULS.append(operacao_a_calcular)                     #adiciona a operacao para o controle
                            
                        else: #se cair aqui, e' porque a operacao de PULS recebe o hidrograma resultante de alguma outra operacao, deve-se avaliar agora se esta outra operacao ja' foi calculada.
                            
                            if (CONTROLE_HIDROGRAMAS[(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular])] == 1): #se cair aqui, a outra operacao ja' foi calculada, pode calcular esta sem problema algum.
                                decisao = True                                                               #Manda bala!
                                ORDEM_EXECUCAO_PULS.append(operacao_a_calcular)                              #adiciona a operacao para o controle
                                
                            else: #Se cair aqui, e' porque a operacao que esta' sendo avaliada precisa do resultado oriundo de outra operacao nao calculada, logo, deve-se fazer a mesma avaliacao para esta outra operacao
                                
                                operacao_a_calcular = HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular] #digo ao programa avaliar a outra operacao em busca de requisitos dela
                                decisao = False                                                     #Esta linha nao e' necessaria, mas e' so' pra lembrar o programador de que a decisao continua falsa
                                
                                
                        ########## ------ Para MKC  ------ ########
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "MKC"):
                        if (not (type(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular]) == int)): #Se nao for 'int', e' porque e' dado por pelo usuario, logo, pode calcular sem problema algum.
                            decisao = True #Manda bala!
                            ORDEM_EXECUCAO_MKC.append(operacao_a_calcular)                     #adiciona a operacao para o controle
                            
                        else: #se cair aqui, e' porque a operacao de MKC recebe o hidrograma resultante de alguma outra operacao, deve-se avaliar agora se esta outra operacao ja' foi calculada.
                            
                            if (CONTROLE_HIDROGRAMAS[(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular])] == 1): #se cair aqui, a outra operacao ja' foi calculada, pode calcular esta sem problema algum.
                                decisao = True #mete bala!
                                ORDEM_EXECUCAO_MKC.append(operacao_a_calcular)                              #adiciona a operacao para o controle
                                
                            else: #Se cair aqui, e' porque a operacao que esta' sendo avaliada precisa do resultado oriundo de outra operacao nao calculada, logo, deve-se fazer a mesma avaliacao para esta outra operacao
                                operacao_a_calcular = HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular] #digo ao programa avaliar a outra operacao em busca de requisitos dela
                                decisao = False #Esta linha nao e' necessaria, mas e' so' pra lembrar o programador de que a decisao continua falsa
                    
                    
                        ########## ------ Para JUNCAO  ------ ########
                    elif (ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "JUNCAO"):
                        
                        # Aqui a logica muda um pouco: deve-se verificar se os hidrogramas de entrada da juncao ja foram calculados.
                            #1 - Somente se verifica os hidrogramas >= 0;
                            #2 - Se todos os >= 0 ja' estao calculados (os negativos nao existem), eu posso calcular a juncao;
                            #3 - Se durante a verificacao dos hidrogramas >= 0 haver algum nao calculado, decisao = False e se analisa esta operacao (nao calculada).
                        #OBS: nao e' necessario verificar se JUNCOES_HIDROGRAMAS = 0, pois o loop so' entra aqui quando JUNCOES_HIDROGRAMAS != 0 (quando e' de fato operacao de JUNCAO)
                        
                        calcular_juncao = True #comeco assumindo que pode-se calcular a juncao
                        analisar_esta_operacao = [] #lista que armazena as operacoes nao calculadas - usada SOMENTE se algumas das operacoes verificadas na juncao nao esta calculada.
                        
                        #    testar os 5 hidrogramas da juncao
                        for hidrograma_juncao in xrange(len(JUNCOES_HIDROGRAMAS[operacao_a_calcular])):
                            
                            #   Avaliar se este hidrograma da juncao e' um hidrograma fornecido pelo usuario....
                            if not (type(JUNCOES_HIDROGRAMAS[operacao_a_calcular][hidrograma_juncao]) == str ):
                                
                                #    testar somente os hidrogramas >= 0 (nao negativos)
                                if not JUNCOES_HIDROGRAMAS[operacao_a_calcular][hidrograma_juncao] < 0: #ou seja, se NAO NEGATIVO (pois os valores negativos representam ausencia de hidrograma - usado quando se somam menos que 5 hidrogramas)..... DEVO ANALISAR
                                    
                                    #    Verificar se a operacao ja' foi calculada.
                                    if CONTROLE_HIDROGRAMAS[(JUNCOES_HIDROGRAMAS[operacao_a_calcular][hidrograma_juncao])] == 0: #se o indice (que e' o numero dentro da variavel JUNCOES_HIDROGRAMAS) do CONTROLE_HIDROGRAMAS e' = 0, ou seja, NAO calculada.
                                        calcular_juncao = False #ja digo que nao posso calcular a juncao.
                                        analisar_esta_operacao.append(JUNCOES_HIDROGRAMAS[operacao_a_calcular][hidrograma_juncao]) #armazeno seu numero para analisar.
                                    
                        if calcular_juncao == True: #ou seja, se depois de testar os 5 hidrogramas desta juncao, todos eles estiverem calculados, eu posso mandar bala!
                            decisao = True #mete bala!
                            ORDEM_EXECUCAO_JUNCAO.append(operacao_a_calcular)  #adiciona a operacao para o controle
                        
                        else: #ou seja, se por ao acaso alguma das operacoes avaliada nao foi calculada. Devo reiniciar o loop com outro operacao_a_calcular
                            operacao_a_calcular = min(analisar_esta_operacao) #digo ao programa avaliar a outra operacao em busca de requisitos dela. Sempre do menor ao maior, por isso min(analisar_esta_operacao).
                            decisao = False #Esta linha nao e' necessaria, mas e' so' pra lembrar o programador de que a decisao continua falsa
                            
                    
                #   A partir daqui, o modelo ja' sabe qual operacao calcular, o codigo a seguir e' para executar cada operacao hidrologica.  #

            if ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "PQ":
                dados_utilizados = ( int(CHUVA_OPERACAO_CORRESPONDENTE[operacao_a_calcular])) #saber qual serie de CHUVA dentre as series de CHUVA que sera' usada nesta simulacao de chuva vazao
                                                                                      
                    # se for uma variavel criada anteriormente, usa-se [dados_utilizados]
                    # se for P ord ou HIDROGRAMA, usa-se [contador_manual_pq]
                    # Isto pq a P_ord[0] pode ter sido gerada a partir da chuva N, entao a primeira serie de P_ord (expressa por contador_manual_pq), foi calculada com a chuva N (expressa por dados_utilizados)
                    # O mesmo vale para hidrogramas. (Hidrograma[N] calculado a partir da série X, na operacao Y).
                    # Isto tudo e' feito para poupar memoria, criando-se variaveis menores.
                    # Se sao valores de cada operacao (como CN, AREA, TC....) utiliza-se "operacao", pois para cada chuva-vazao, eu pego os valores de CN,TC e AREA correspondentes da operacao.
                
                HIDROGRAMAS_SAIDA_PQ[contador_manual_pq] = self.rodarOperacaoPQ( NUMERO_INTERVALOS_TEMPO_CHUVA, 
                                                                                 NUMERO_INTERVALOS_TEMPO, 
                                                                                 DURACAO_INTERVALO_TEMPO, 
                                                                                 CN[operacao_a_calcular], 
                                                                                 TC[operacao_a_calcular], 
                                                                                 AREA[operacao_a_calcular],
                                                                                 PRECIPITACAO_ORDENADA[dados_utilizados][:], 
                                                                                 NOMES_OPERACOES_HIDROLOGICAS[operacao_a_calcular],
                                                                                 (operacao_a_calcular+1)                          )
                contador_manual_pq += 1 #usado para P_ord e HIDROGRAMAS, pois estas variaveis tem contagem diferentes ja' que nem toda operacao e' chuva vazao.... Isso foi feito para poupar memoria.
                CONTROLE_HIDROGRAMAS[operacao_a_calcular] = 1 #Digo ao programa que esta operacao foi calculada
#                CONTROLE_HIDROGRAMAS_PQ.append(operacao_a_calcular) #Armazeno quais operacoes sao de PQ para facilitar saida de dados mais tarde.
                
                
            elif ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "PULS":
                                    
                                                    # PEGAR O HIDROGRAMA CORRETO PARA APLICAR O PULS #
                                    
                hidrograma_usado_neste_puls = [0 for termos in xrange(NUMERO_INTERVALOS_TEMPO)] #variavel que recebe os valores dos hidrogramas em cada novo puls
                if (type(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular]) == int):  #entra um hidrograma de outra operacao, esta operacao ja' esta' calculada (verificado anteriormente)
                    
                    if (HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_PQ): #isto e', se a operacao N (de PULS) utilizar o hidrograma de oriundo de alguma PQ
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_PQ.index(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_puls[valor] = HIDROGRAMAS_SAIDA_PQ[indice_hidrograma][valor]
                            
                    elif(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_PULS): #isto e', se a operacao N (de PULS) utilizar o hidrograma de oriundo de outro PULS
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_PULS.index(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_puls[valor] = HIDROGRAMAS_SAIDA_PULS[indice_hidrograma][valor]
                    
                    elif(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_MKC): #isto e', se a operacao N (de PULS) utilizar o hidrograma de oriundo de algum MKC
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_MKC.index(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_puls[valor] = HIDROGRAMAS_SAIDA_MKC[indice_hidrograma][valor]
                            
                    elif(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_JUNCAO): #isto e', se a operacao N (de PULS) utilizar o hidrograma de oriundo de alguma JUNCAO
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_JUNCAO.index(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_puls[valor] = HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma][valor]
                        
                else:  #e' um hidrograma observador, deve-se ler o arquivo.
                        #contar quantas linhas tem o arquivo
                    numero_linhas  = sum(1 for linha in open(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                    
                        #Nao sei se isto e' necessario, mas se o arquivo fornecido pelo usuario nao tiver o mesmo numero de termos que NUMERO_INTERVALOS_TEMPO, o programa deve ser finalizado, pois nao sei como proceder neste caso.
                    if (not numero_linhas == NUMERO_INTERVALOS_TEMPO): #ERRO?
                        tkMessageBox.showinfo("Verifique os arquivos de entrada das operações de Puls!", "Um dos hidrogramas fornecidos pelo usuário (arquivo .txt) não tem o mesmo número de termos (linhas) que o número de intervalos de tempo da simulação.") #"Voce e' burro." ahahhahahaha
                        tkMessageBox.showinfo("O modelo será finalizado.", "Revise os arquivos de hidrogramas e tente novamente.\nDica: Não deixe linhas em branco no final do arquivo.") #"Voce e' burro." ahahhahahaha
                        self.ragequit()
                    
                    arquivo_hidrograma = open(HIDROGRAMAS_ENTRADA_PULS[operacao_a_calcular], 'r') #abrir o arquivo para le-lo.
                    
                        #loop para ler linhas do arquivo da curva cota-volume
                    for linha in xrange(numero_linhas):
                        conteudo_hidrograma = arquivo_hidrograma.readline().split(";")            #ler a linha e dividir 
                        hidrograma_usado_neste_puls[linha] = float(conteudo_hidrograma[0])        #valores de hidrograma
                    
                    arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.
                    
                
                                                            # HIDROGRAMA ESCOLHIDO, RODAR OPERACAO #
                
                HIDROGRAMAS_SAIDA_PULS[contador_manual_puls] = self.rodarOperacaoPULS( hidrograma_usado_neste_puls,
#                                                                                       COTAS_FUNDO[operacao_a_calcular], 
                                                                                       COTAS_INICIAIS[operacao_a_calcular], 
                                                                                       ESTRUTURAS_PULS[operacao_a_calcular], 
                                                                                       CURVA_COTA_VOLUME[contador_manual_puls], 
                                                                                       DURACAO_INTERVALO_TEMPO,
                                                                                       NUMERO_INTERVALOS_TEMPO,
                                                                                       NOMES_OPERACOES_HIDROLOGICAS[operacao_a_calcular], 
                                                                                       (operacao_a_calcular+1)                          )
                contador_manual_puls += 1
                CONTROLE_HIDROGRAMAS[operacao_a_calcular] = 1 #Digo ao programa que esta operacao foi calculada
                
                
            elif ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "MKC":
                
                #    PEGAR O HIDROGRAMA CORRETO PARA APLICAR O MKC #
                                    
                hidrograma_usado_neste_mkc = [0 for termos in xrange(NUMERO_INTERVALOS_TEMPO)] #variavel que recebe os valores dos hidrogramas em cada novo puls
                if (type(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular]) == int):  #entra um hidrograma de outra operacao, esta operacao ja' esta' calculada (verificado anteriormente)
                    
                    if (HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_PQ): #isto e', se a operacao N (de MKC) utilizar o hidrograma de oriundo de alguma PQ
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_PQ.index(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_mkc[valor] = HIDROGRAMAS_SAIDA_PQ[indice_hidrograma][valor]
                            
                    elif(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_PULS): #isto e', se a operacao N (de MKC) utilizar o hidrograma de oriundo de outro PULS
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_PULS.index(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_mkc[valor] = HIDROGRAMAS_SAIDA_PULS[indice_hidrograma][valor]
                    
                    elif(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_MKC): #isto e', se a operacao N (de MKC) utilizar o hidrograma de oriundo de algum MKC
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_MKC.index(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_mkc[valor] = HIDROGRAMAS_SAIDA_MKC[indice_hidrograma][valor]
                            
                    elif(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular] in CONTROLE_HIDROGRAMAS_JUNCAO): #isto e', se a operacao N (de MKC) utilizar o hidrograma de oriundo de alguma JUNCAO
                        indice_hidrograma = CONTROLE_HIDROGRAMAS_JUNCAO.index(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular])
                        for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                            hidrograma_usado_neste_mkc[valor] = HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma][valor]
                        
                else:  #e' um hidrograma observador, deve-se ler o arquivo.
                        #contar quantas linhas tem o arquivo
                    numero_linhas  = sum(1 for linha in open(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                    
                        #Nao sei se isto e' necessario, mas se o arquivo fornecido pelo usuario nao tiver o mesmo numero de termos que NUMERO_INTERVALOS_TEMPO, o programa deve ser finalizado, pois nao sei como proceder neste caso.
                    if (not numero_linhas == NUMERO_INTERVALOS_TEMPO): #ERRO?
                        tkMessageBox.showinfo("Verifique os arquivos de entrada das operações Muskingun-Cunge!", "Um dos hidrogramas fornecidos pelo usuário (arquivo .txt) não tem o mesmo número de termos (linhas) que o número de intervalos de tempo da simulação.") #"Voce e' burro." ahahhahahaha
                        tkMessageBox.showinfo("O modelo será finalizado.", "Revise os arquivos de hidrogramas e tente novamente.\nDica: Não deixe linhas em branco no final do arquivo.") #"Voce e' burro." ahahhahahaha
                        self.ragequit()
                    
                    arquivo_hidrograma = open(HIDROGRAMAS_ENTRADA_MKC[operacao_a_calcular], 'r') #abrir o arquivo para le-lo.
                    
                        #loop para ler linhas do arquivo da curva cota-volume
                    for linha in xrange(numero_linhas):
                        conteudo_hidrograma = arquivo_hidrograma.readline().split(";")            #ler a linha e dividir 
                        hidrograma_usado_neste_mkc[linha] = float(conteudo_hidrograma[0])        #valores de hidrograma
                    
                    arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.
                
                
                HIDROGRAMAS_SAIDA_MKC[contador_manual_mkc] = self.rodarOperacaoMKC( hidrograma_usado_neste_mkc, 
                                                                                    DIFERENCA_COTA[operacao_a_calcular], 
                                                                                    COMPRIMENTO_CANAL[operacao_a_calcular], 
                                                                                    LARGURA_CANAL[operacao_a_calcular],
                                                                                    COEF_RUGOSIDADE[operacao_a_calcular], 
                                                                                    DURACAO_INTERVALO_TEMPO,
                                                                                    NUMERO_INTERVALOS_TEMPO,
                                                                                    NOMES_OPERACOES_HIDROLOGICAS[operacao_a_calcular], 
                                                                                    (operacao_a_calcular+1)                          )
                
                contador_manual_mkc += 1
                CONTROLE_HIDROGRAMAS[operacao_a_calcular] = 1 #Digo ao programa que esta operacao foi calculada
                
                
            elif ORDEM_OPERACOES_HIDROLOGICAS[operacao_a_calcular] == "JUNCAO":

                #    Neste ponto o modelo ja' tem todos os hidrogramas necessarios pra soma calculados (ja' foi feita a verificacao anteriormente)
                #    Deve-se agora pegar os hidrogramas corretos.
                
                valores_hidrogramas_da_juncao = [[0. for nint_tempo in xrange(NUMERO_INTERVALOS_TEMPO)] for numero_hidrogramas in xrange(len(JUNCOES_HIDROGRAMAS[operacao_a_calcular]))]
                
                    #loop para comecar a copiar os valores
                for numero_hidrograma in xrange(len(JUNCOES_HIDROGRAMAS[operacao_a_calcular])):
                    
                    #   Analisar o tipo do hidrograma que entra na juncao...
                    if (type(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma]) == int):
                    
                            #analisar de onde eu pego o hidrograma....DETALHE: NAO POSSO ENTRAR COM O HIDROGRAMA DA PROPRIA OPERACAO, PORQUE ELE AINDA NAO EXISTE!!!
                        if ( (JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] >= 0) ):  #entra um hidrograma de outra operacao, esta operacao ja' esta' calculada (verificado anteriormente)
                            
                            if (JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] in CONTROLE_HIDROGRAMAS_PQ): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de alguma PQ
                                indice_hidrograma = CONTROLE_HIDROGRAMAS_PQ.index(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_PQ[indice_hidrograma][valor]
                                    
                            elif(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] in CONTROLE_HIDROGRAMAS_PULS): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de algum PULS
                                indice_hidrograma = CONTROLE_HIDROGRAMAS_PULS.index(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_PULS[indice_hidrograma][valor]
                            
                            elif(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] in CONTROLE_HIDROGRAMAS_MKC): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de algum MKC
                                indice_hidrograma = CONTROLE_HIDROGRAMAS_MKC.index(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_MKC[indice_hidrograma][valor]
                                    
                            elif ( (JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] in CONTROLE_HIDROGRAMAS_JUNCAO) and (not JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma] == operacao_a_calcular) ): #isto e', se a operacao N (de JUNCAO) utilizar o hidrograma de oriundo de outra JUNCAO
                                indice_hidrograma = CONTROLE_HIDROGRAMAS_JUNCAO.index(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma])
                                for valor in xrange(NUMERO_INTERVALOS_TEMPO): #passar os valores do hidrograma que sera' usado para a variavel usada na funcao
                                    valores_hidrogramas_da_juncao[numero_hidrograma][valor] = HIDROGRAMAS_SAIDA_JUNCAO[indice_hidrograma][valor]
                            
                    #   Se entrar aqui, e' pra entrar com um hidrograma observado...
                    else:  #e' um hidrograma observado, deve-se ler o arquivo.
                            #contar quantas linhas tem o arquivo
                        numero_linhas  = sum(1 for linha in open(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma],'r')) #contar o numero de linhas do arquivo da curva cota-volume
                        
                            #Nao sei se isto e' necessario, mas se o arquivo fornecido pelo usuario nao tiver o mesmo numero de termos que NUMERO_INTERVALOS_TEMPO, o programa deve ser finalizado, pois nao sei como proceder neste caso.
                        if (not numero_linhas == NUMERO_INTERVALOS_TEMPO): #ERRO?
                            tkMessageBox.showinfo("Verifique os arquivos de entrada das operações Junção!", "Um dos hidrogramas fornecidos pelo usuário (arquivo .txt) não tem o mesmo número de termos (linhas) que o número de intervalos de tempo da simulação.") #"Voce e' burro." ahahhahahaha
                            tkMessageBox.showinfo("O modelo será finalizado.", "Revise os arquivos de hidrogramas e tente novamente.\nDica: Não deixe linhas em branco no final do arquivo.") #"Voce e' burro." ahahhahahaha
                            self.ragequit()
                        
                        arquivo_hidrograma = open(JUNCOES_HIDROGRAMAS[operacao_a_calcular][numero_hidrograma], 'r') #abrir o arquivo para le-lo.
                        
                            #loop para ler linhas do arquivo da curva cota-volume
                        for linha in xrange(numero_linhas):
                            conteudo_hidrograma = arquivo_hidrograma.readline().split(";")            #ler a linha e dividir 
                            valores_hidrogramas_da_juncao[numero_hidrograma][linha] = float(conteudo_hidrograma[0])        #valores de hidrograma
                        
                        arquivo_hidrograma.close() #fechar o arquivo -> poupar memoria.
                            #contar quantas linhas tem o arquivo
                    
                HIDROGRAMAS_SAIDA_JUNCAO[contador_manual_juncao] = self.rodarOperacaoJUNCAO( valores_hidrogramas_da_juncao, 
                                                                                             NUMERO_INTERVALOS_TEMPO,
                                                                                             NOMES_OPERACOES_HIDROLOGICAS[operacao_a_calcular], 
                                                                                             (operacao_a_calcular+1)                          )
                
                contador_manual_juncao += 1
                CONTROLE_HIDROGRAMAS[operacao_a_calcular] = 1 #Digo ao programa que esta operacao foi calculada
                
                
            #pbar.update(operacao + 1)
        #pbar.finish()
        
            #aqui acabaram as operacoes, meu programa esta' com respostas para serem escritas....
            
        ############# --- terminei de calcular todas as operacoes hidrologicas --- #############
        
        ############# --- ESCREVER OS RESULTADOS EM BLOCOS DE NOTAS DISTINTOS --- #############
        
            #PQ
        if "PQ" in ORDEM_OPERACOES_HIDROLOGICAS:
            
            self.escreverSaidaPQ( HIDROGRAMAS_SAIDA_PQ, 
                                  PRECIPITACAO_ORDENADA, 
                                  ORDEM_OPERACOES_HIDROLOGICAS, 
                                  CHUVA_OPERACAO_CORRESPONDENTE, 
                                  NUMERO_INTERVALOS_TEMPO, 
                                  DURACAO_INTERVALO_TEMPO, 
                                  NUMERO_OPERACOES_HIDROLOGICAS, 
                                  NUMERO_INTERVALOS_TEMPO_CHUVA)
        
            #PULS
        if "PULS" in ORDEM_OPERACOES_HIDROLOGICAS:
            
            self.escreverSaidaPULS( HIDROGRAMAS_SAIDA_PQ, 
                                    HIDROGRAMAS_SAIDA_PULS,
                                    HIDROGRAMAS_SAIDA_MKC, 
                                    HIDROGRAMAS_SAIDA_JUNCAO, 
                                    ORDEM_OPERACOES_HIDROLOGICAS, 
                                    NUMERO_INTERVALOS_TEMPO, 
                                    NUMERO_OPERACOES_HIDROLOGICAS,
                                    DURACAO_INTERVALO_TEMPO,
                                    HIDROGRAMAS_ENTRADA_PULS,
                                    ORDEM_EXECUCAO_PQ,
                                    ORDEM_EXECUCAO_PULS,
                                    ORDEM_EXECUCAO_MKC, 
                                    ORDEM_EXECUCAO_JUNCAO        )

            #MKC
        if "MKC" in ORDEM_OPERACOES_HIDROLOGICAS:
        
           self.escreverSaidaMKC( HIDROGRAMAS_SAIDA_PQ, 
                                  HIDROGRAMAS_SAIDA_PULS, 
                                  HIDROGRAMAS_SAIDA_MKC, 
                                  HIDROGRAMAS_SAIDA_JUNCAO, 
                                  ORDEM_OPERACOES_HIDROLOGICAS, 
                                  NUMERO_INTERVALOS_TEMPO, 
                                  NUMERO_OPERACOES_HIDROLOGICAS, 
                                  DURACAO_INTERVALO_TEMPO, 
                                  HIDROGRAMAS_ENTRADA_MKC, 
                                  ORDEM_EXECUCAO_PQ, 
                                  ORDEM_EXECUCAO_PULS, 
                                  ORDEM_EXECUCAO_MKC, 
                                  ORDEM_EXECUCAO_JUNCAO        )
                                  
            #JUNCAO
        if "JUNCAO" in ORDEM_OPERACOES_HIDROLOGICAS:
            
            self.escreverSaidaJUNCAO( HIDROGRAMAS_SAIDA_PQ, 
                                      HIDROGRAMAS_SAIDA_PULS, 
                                      HIDROGRAMAS_SAIDA_MKC,
                                      HIDROGRAMAS_SAIDA_JUNCAO, 
                                      ORDEM_OPERACOES_HIDROLOGICAS, 
                                      NUMERO_INTERVALOS_TEMPO, 
                                      NUMERO_OPERACOES_HIDROLOGICAS, 
                                      DURACAO_INTERVALO_TEMPO, 
                                      JUNCOES_HIDROGRAMAS, 
                                      ORDEM_EXECUCAO_PQ, 
                                      ORDEM_EXECUCAO_PULS, 
                                      ORDEM_EXECUCAO_MKC,
                                      ORDEM_EXECUCAO_JUNCAO        )    
  
            
