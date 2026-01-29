import os

class Instance:
    def __init__(self,shop_params,inst_params):
        #Inicializar as variáveis e converter os parâmetros principais para inteiros
        self.time_day = int(shop_params['timeDay'])
        self.num_tasks_types = int(shop_params['numTypeTasks'])
        self.num_operators = int(shop_params['numOperators'])
        self.num_workstations = int(shop_params['numWorkstations'])

        self.task_operators = shop_params['taskOperators']
        self.efficiency = shop_params['efficiencyTaskOperator']
        self.task_workstations = shop_params['taskWorkstations']

        self.num_vehicles = int(inst_params['numVehicles'])
        self.vehicle_tasks = inst_params['tasks']
        self.processing_times = inst_params['processingTimes']
        self.release_dates = inst_params['releaseDate']
        self.due_dates = inst_params['dueDate']
        #Executar o método para processar e limpar os dados
        self.process_data()

    def process_data(self):
        #Verificar se existe apenas um veículo e garantir que os dados sejam listas
        if self.num_vehicles == 1 and isinstance(self.vehicle_tasks[0],str):
            self.vehicle_tasks = [self.vehicle_tasks]
            self.processing_times = [self.processing_times]
        #Garantir a formatação correta de listas para operadores e estações    
        if isinstance(self.task_operators[0],str):
            self.task_operators = [self.task_operators]
        if isinstance(self.task_workstations[0],str):
            self.task_workstations = [self.task_workstations]
        #Ajustar os índices dos operadores de base 1 para base 0    
        clean_operators = []
        for row in self.task_operators:
            new_row = []
            for x in row:
                new_row.append(int(x)-1)
            clean_operators.append(new_row)
        self.task_operators = clean_operators

        clean_workstations = []
        for row in self.task_workstations:
            new_row = []
            for x in row:
                new_row.append(int(x)-1)
            clean_workstations.append(new_row)
        self.task_workstations = clean_workstations
        
        clean_tasks = []
        for row in self.vehicle_tasks:
            new_row = []
            for x in row:
                new_row.append(int(x)-1)
            clean_tasks.append(new_row)
        self.vehicle_tasks = clean_tasks
        #Converter todos os tempos de processamento para inteiros
        clean_times = []
        for row in self.processing_times:
            new_row = []
            for x in row:
                new_row.append(int(x))
            clean_times.append(new_row)
        self.processing_times = clean_times
        #Normalizar datas de libertação e entregar para listas de inteiros
        if isinstance(self.release_dates, str): self.release_dates = [self.release_dates]
        if isinstance(self.due_dates, str): self.due_dates = [self.due_dates]

        self.release_dates = [int(x) for x in self.release_dates]
        self.due_dates = [int(x) for x in self.due_dates]
        #Converter valores para float e '----' para None
        clean_efficiency = []
        eff_inicial = self.efficiency
        if not isinstance(eff_inicial[0], list):
            eff_inicial = [eff_inicial]
        for row in eff_inicial:
            clean_row = []
            for x in row:
                if x == '----':
                    clean_row.append(None)
                else:
                    clean_row.append(float(x))
            clean_efficiency.append(clean_row)
        self.efficiency = clean_efficiency

class Solution:
    def __init__(self,instance):
        #Definir a estrutura base para armazenar os resultados da solução
        self.instance = instance
        self.lineup = {}
        self.makespan = 0.0
        self.total_tardiness = 0.0
        self.op_occu = 0.0
        self.ws_occu = 0.0

def load_txt(filename):
    parameters = {}
    current_key = None
    data_buffer = []
    #Tentar ler o ficheiro usando utf-8, com alternativa para latin-1
    try:
        f = open(filename, 'r', encoding='utf-8-sig')
        lines = f.readlines()
        f.close()
    except:
        f = open(filename, 'r', encoding='latin-1')
        lines = f.readlines()
        f.close()
        
    for line in lines:
        line = line.strip()
        if not line: continue
        #Identificar o início de uma nova secção de dados
        if line.startswith('['):
            if current_key:
                if len(data_buffer)==1: #Processar e guarda os dados da secção anterior no dicionário
                    if len(data_buffer[0])==1:
                        parameters[current_key]=data_buffer[0][0]
                    else:
                        parameters[current_key]=data_buffer[0]
                else:
                    parameters[current_key]=data_buffer
            current_key=line.replace('[','').replace(']','') #Atualizar a chave atual e reinicia o buffer
            data_buffer=[]
        else:
            data_buffer.append(line.split()) #Adicionar a linha atual ao buffer de dados
    #Guardar o último bloco de dados após o fim do loop    
    if current_key and data_buffer:
        if len(data_buffer)==1:
            if len(data_buffer[0])==1:
                parameters[current_key]=data_buffer[0][0]
            else:
                parameters[current_key]=data_buffer[0]
        else:
            parameters[current_key]=data_buffer
    return parameters

