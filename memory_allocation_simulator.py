import sys
import os 
from texttable import Texttable #Para poder imprimir las tablas en pantalla
from types import SimpleNamespace


#Clase que almacena la cola de nuevos procesos en espera de un espacio en memoria
class Procesador:
	def __init__(self):
		self.colaEspera= list()
		self.proceso_en_ejecucion = None
		self.estado = True


#Clase que almacena las particiones y sus tamaños
class Memoria:

	def __init__(self):
		self.partSO = Particion(100,0)
		self.lista_particiones = [Particion(250,100), Particion(120,349), Particion(60,269)]
		self.colaEspera = list()
		self.listaProcesosARemover = list()  #Almacena los procesos que ya se asignaron a Memoria y se tienen que remover
		self.listaPrioridad = list()

#Asignación de memoria Best Fit
	def asignarProcesoBF(self, proceso):
		
		diferencia = sys.maxsize  #Devuelve el máximo valor de una variable
		best_particion = None
		aux = 0
		for particion in self.lista_particiones:  #Se recorren todas las particiones
			aux = particion.size - proceso.tamanio  #Para saber cual partición genera más fragmentación interna
			if particion.size >= proceso.tamanio and particion.estado == False:  #El proceso cabe en una partición libre
				if aux < diferencia and aux >= 0: #La primera vez siempre ingresa al if
					diferencia = aux 
					best_particion = particion
					# best_particion = self.lista_particiones.index(particion)
		if best_particion != None:  #Cuando una partición fue elegida como best_part
			best_particion.asignar_proceso(proceso)
			proceso.set_particion_proceso(best_particion)
			if proceso in self.colaEspera:
				self.listaProcesosARemover.append(proceso)
			best_particion.fi = diferencia
			print(f'se asigno proceso {proceso.id} a la particion {best_particion.id}' )
			
		else:
			print(f'no hay espacio para el proceso {proceso.id} se asigno a la cola de espera' )
			if proceso not in self.listaPrioridad:
				self.listaPrioridad.append(proceso)
			if proceso is self.colaEspera:
				self.colaEspera.remove(proceso)
#Clase que almacena información de cada partición 
class Particion:
	ID= 1
	def __init__(self,unSize,dirInicio):
		self.id= Particion.ID
		self.size = unSize
		self.fi = 0
		self.procAsignado = None
		Particion.incrementarId()  
		self.dirInicio = dirInicio
		self.estado = False
	
	@classmethod
	def incrementarId(cls):
		cls.ID += 1

	def asignar_proceso(self,proc):
		self.procAsignado = proc
		self.estado = True
		self.fi = self.size - proc.tamanio
		proc.estado = 'listo'
	
class Proceso:
	# data = '{"id": "1", "tamanio": 100, "ta": "1", "ti":"3"},{}'

	ID= 1
	def __init__(self,tamanio,ta,ti):
		self.id = Proceso.ID
		self.tamanio = tamanio
		self.ta = ta
		self.ti = ti
		self.tcpu = 0
		self.estado = 'pendiente'
		self.partAsignada = None
		Proceso.incrementarId()


	@classmethod
	def incrementarId(cls):
		cls.ID += 1

	def set_particion_proceso(self,part):
		self.partAsignada = part	


class CtrlEjecucion:
	tiempoActual = 0 	 #Para comparar y saber en que instante de tiempo asignar
	def __init__(self):
		self.x=0
		self.memoria = Memoria()
		self.procesos = list()
		self.cpu = Procesador()
		self.agregarProcesos()
		self.procesosTerminados = list()
		self.simulando()

	@classmethod
	def incrementarTiempo(cls):
		cls.tiempoActual += 1

	def agregarProcesos(self):
		while True:
			if len(self.procesos) <= 10:
				print(f'No puede haber mas de 10 procesos, cantidad de procesos actuales:{len(self.procesos)}')
				tamanioP = int(input('ingresa tamanio del proceso: '))
				tArribo = int(input('ingresa tiempo de arribo: '))
				tIrrupcion = int(input('ingresa tiempo de irrupcion: '))
				if 0 < tamanioP <= 250  and 0 <= tArribo  and  0 < tIrrupcion :
					self.procesos.append(Proceso(tamanioP,tArribo,tIrrupcion))
				else:
					print('el proceso no puede ser mayor a 250kb')
					
			else:
				return print(f'No puede haber mas de 10 procesos')
				break
			opcion = (input('agregar otro proceso? S/N: '))
			if opcion == 'n' or opcion == 'N':
				break
				
	def descargarProceso(self):
		if (self.cpu.proceso_en_ejecucion):
			if CtrlEjecucion.tiempoActual == (self.cpu.proceso_en_ejecucion.ti + self.cpu.proceso_en_ejecucion.tcpu) :
				self.cpu.proceso_en_ejecucion.estado = 'terminado'
				if self.cpu.proceso_en_ejecucion not in self.procesosTerminados:
					self.procesosTerminados.append(self.cpu.proceso_en_ejecucion)
				for particion in self.memoria.lista_particiones:
					if self.cpu.proceso_en_ejecucion == particion.procAsignado:
						particion.procAsignado = None
						particion.estado = False
						particion.fi = 0
						# self.cpu.colaEspera.remove(self.cpu.proceso_en_ejecucion)
						self.cpu.proceso_en_ejecucion = None
						self.cpu.estado= True
		self.ordenarColaCPU()
						
	def cargarColaEspera(self):  
		#Ver si hay que ordenar la cola antes###################################
		for proceso in self.procesos:
			if CtrlEjecucion.tiempoActual == proceso.ta and proceso not in self.memoria.colaEspera :
				self.memoria.colaEspera.append(proceso)

	def cargarMemoria(self):
		
		for proceso in self.memoria.listaPrioridad:
			self.memoria.asignarProcesoBF(proceso)

		for proceso in self.memoria.colaEspera:
			if CtrlEjecucion.tiempoActual == proceso.ta:
				self.memoria.asignarProcesoBF(proceso)

		for proceso in self.memoria.listaProcesosARemover:
			self.memoria.colaEspera.remove(proceso)
		for proceso in self.memoria.listaProcesosARemover:
			if proceso in self.memoria.listaPrioridad:
				self.memoria.listaPrioridad.remove(proceso)
			
		self.memoria.listaProcesosARemover.clear()

	def cargarColaCPU(self):
		for particion in self.memoria.lista_particiones:
			if particion.procAsignado and (particion.procAsignado not in self.cpu.colaEspera) and particion.procAsignado.estado == 'listo' :
				self.cpu.colaEspera.append(particion.procAsignado)
		self.ordenarColaCPU()

	def ordenarColaCPU(self):
		self.cpu.colaEspera = sorted(self.cpu.colaEspera, key=lambda proceso: proceso.ti)
	
	def ejecutarProceso(self):
		if self.cpu.colaEspera and self.cpu.estado:
			self.cpu.proceso_en_ejecucion = self.cpu.colaEspera[0]
			self.cpu.colaEspera[0].estado = 'en ejecucion'
			self.cpu.estado = False
			self.cpu.colaEspera[0].tcpu = CtrlEjecucion.tiempoActual
			self.cpu.colaEspera.remove(self.cpu.colaEspera[0])
		self.ordenarColaCPU()

	def mostrarTablas(self):
		print(f'=====T actual = {CtrlEjecucion.tiempoActual} ====')
		self.mostrarTablaParticiones()
		self.mostrarTablaProcesos()
		self.mostrarTablaCPU()
		# self.mostrarTablaProcesosTerminados()
		# self.mostrarTablaColaEspera()

	def mostrarTablaColaEspera(self):
		print('============= COLA ESPERA MEM =============')
		
		tablaColaEsperaMem = Texttable()
		tablaColaEsperaMem.add_rows([['ID', 'estado','ParticionA']])
		print(tablaColaEsperaMem.draw())
		for proceso in self.memoria.colaEspera:
			tablaColaEsperaMem.add_rows([[str(proceso.id), str(proceso.estado),str(proceso.partAsignada)]])
			print(tablaColaEsperaMem.draw())

	def mostrarTablaProcesosTerminados(self):
		print('============= Procesos Terminados =============')
		
		tablaProcesosTerminados = Texttable()
		tablaProcesosTerminados.add_rows([['ID', 'estado']])
		print(tablaProcesosTerminados.draw())
		for proceso in self.procesosTerminados:
			tablaProcesosTerminados.add_rows([[str(proceso.id), str(proceso.estado)]])
			print(tablaProcesosTerminados.draw())

	def mostrarTablaParticiones(self):
		tablaParticion = Texttable()
		print('============= PARTICIONES =============')
		tablaParticion.add_rows([['ID','Tamaño', 'FI', 'Estado','Direccion_inicio','ID_proceso']])
		print(tablaParticion.draw())
		for particion in self.memoria.lista_particiones:
			idProceso = '-'
			if particion.procAsignado:
				idProceso = particion.procAsignado.id
			tablaParticion.add_rows([[str(particion.id), str(particion.size), str(particion.fi), str(particion.estado), str(particion.dirInicio), str(idProceso)]])
			print(tablaParticion.draw())

	def mostrarTablaProcesos(self):
		tablaProcesos = Texttable() 
		print('============= PROCESOS =============')
		tablaProcesos.add_rows([['ID','Tamaño', 'TA', 'TI', 'Estado','ID_particion']])
		print(tablaProcesos.draw())
		for proceso in self.procesos:
			idParticion = '-'
			if proceso.partAsignada:
				idParticion = proceso.partAsignada.id
			tablaProcesos.add_rows([[str(proceso.id), str(proceso.tamanio), str(proceso.ta), str(proceso.ti), str(proceso.estado), str(idParticion)]])
			print(tablaProcesos.draw())

	def mostrarTablaCPU(self):
		tablaCPU = Texttable()
		print('============== CPU ==============')
		tablaCPU.add_rows([['proceso_en_ejecucion', 'estado']])
		print(tablaCPU.draw())
		idProceso= '-'
		if self.cpu.proceso_en_ejecucion:
			idProceso= self.cpu.proceso_en_ejecucion.id
		tablaCPU.add_rows([[str(idProceso), str(self.cpu.estado)]])
		print(tablaCPU.draw())
		print('============== Cola de Espera CPU ==============')
		tablaCPU.add_rows([['ID', 'estado']])
		print(tablaCPU.draw())
		for proceso in self.cpu.colaEspera:
			tablaCPU.add_rows([[str(proceso.id), str(proceso.estado)]])
			print(tablaCPU.draw())

	def condicionFin(self):
		cont=0
		for proceso in self.procesos:
			if proceso.estado == 'terminado':
				cont = cont +1
		if cont == len(self.procesos):
			print('==============Todos los procesos fueron ejecutados==============')
			self.mostrarTablas()
			print('==============Fin de la Simulacion==============')
			self.x=1
	

	def simulando(self):
		if self.x != 1:
			input()
			self.descargarProceso()
			self.cargarColaEspera()
			self.cargarMemoria()
			self.cargarColaCPU()
			self.ejecutarProceso()
			self.mostrarTablas()
			CtrlEjecucion.incrementarTiempo()
			self.condicionFin()
			self.simulando()
		else:
			input()
			return 0

CtrlEjecucion()
	
	
	
# CASOS DE PRUEBA
	# 1- 
		# proceso1(60,0,1)
		# proceso2(120,0,4)
		# proceso3(230,0,3)
		# proceso4(110,3,1)
		# proceso5(100,4,1)
	# 2- 
		# proceso1(60,0,1)
		# proceso2(120,0,4)
		# proceso3(230,0,3)
		# proceso4(110,2,1)
		# proceso5(100,4,1)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	