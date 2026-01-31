from data_reader import Solution

class LineUp:

    def __init__(self, instance):
        self.instance = instance
    
    def criar_solucao(self, rule = "SPT"):

        solution = Solution(self.instance)

        #Inicializar listas vazias para cada veículo
        for vehicle in range (self.instance.num_vehicles):
            solution.lineup[vehicle] = []

        #'Controladores' de tempo livre
        operators_free_time = [0] * self.instance.num_operators
        workstation_free_time = [0] * self.instance.num_workstations
        vehicle_free_time = list(self.instance.release_dates)

        #Para guardar {vehicle_id}: {'op': id, 'ws': id}} da última tarefa realizada
        last_resources = {}

        #Qual é a próxima tarefa a fazer de cada veículo
        next_task_id = [0] * self.instance.num_vehicles

        #Veículos que ainda têm tarefas por fazer
        vehicles_undone_tasks = list(range(self.instance.num_vehicles))

        sequencia_log = []

        while len(vehicles_undone_tasks) > 0 :
            candidates = []

            #Ver qual é a próxima tarefa de cada veículo disponível
            for vehicle_id in vehicles_undone_tasks:
                task_id = next_task_id[vehicle_id]
                task_type = self.instance.vehicle_tasks[vehicle_id][task_id]

                score = 0

                #Lógica das regras
                if rule == "SPT":
                    #Menor tempo = melhor
                    score = self.instance.processing_times[vehicle_id][task_id]
                elif rule == "EDD":
                    #Menor data de entrega = melhor
                    score = self.instance.due_dates[vehicle_id]
                elif rule == "FOLGA":
                    #Calcular quanto trabalho falta
                    tempo_restante = 0
                    for k in range(task_id, len(self.instance.vehicle_tasks[vehicle_id])):
                        tempo_restante += self.instance.processing_times[vehicle_id][k]
                    #Folga = Prazo - (Tempo Atual - Trabalho Restante)
                    score = self.instance.due_dates[vehicle_id] - vehicle_free_time[vehicle_id] - tempo_restante
                elif rule == "LPT":
                    #Contrário de SPT, dá prioridade ao maior tempo
                    score = - self.instance.processing_times[vehicle_id][task_id]
                elif rule == "MOPNR":
                    #Most Operations Remaining
                    #Quantas tarefas faltam deste índice para a frente
                    tarefas_restantes = len(self.instance.vehicle_tasks[vehicle_id]) - task_id
                    #Queremos dar "prioridade" a quem tem mais tarefas
                    score = - tarefas_restantes
                elif rule == "MWKR":
                    #Most Work Remaining (soma do tempo dos trabalhos restante)
                    trabalho_total = 0
                    for k in range (task_id, len(self.instance.vehicle_tasks[vehicle_id])):
                        trabalho_total += self.instance.processing_times[vehicle_id][k]
                    #Queremos o maior trabalho
                    score = - trabalho_total
                elif rule == "SRPT":
                    #Shortest Remaining Work Time
                    #Queremos o MENOR tempo total restante
                    tempo_restante = 0
                    for k in range(task_id, len(self.instance.vehicle_tasks[vehicle_id])):
                        tempo_restante += self.instance.processing_times[vehicle_id][k]
                    score = tempo_restante
                elif rule == "CR":
                    #Critical Racio
                    tempo_restante = 0.001
                    for k in range(task_id, len(self.instance.vehicle_tasks[vehicle_id])):
                        tempo_restante += self.instance.processing_times[vehicle_id][k]
                    tempo_disponivel = self.instance.due_dates[vehicle_id] - vehicle_free_time[vehicle_id]
                    score = tempo_disponivel/tempo_restante
                elif rule == "LFJ":
                    #Least Flexible Job
                    num_operators = len(self.instance.task_operators[task_type])
                    num_workstations = len(self.instance.task_workstations[task_type])
                    score = num_operators + num_workstations
                
                #Guardar candidato
                candidates.append({
                    'vehicle_id':vehicle_id,
                    'task_id': task_id,
                    'task_type': task_type,
                    'score': score,
                    'std_time': self.instance.processing_times[vehicle_id][task_id]
                })

            #Escolher o melhor candidato
            best_candidate = None
            best_score = float('inf') #Começar com infinito

            for candidato in candidates:
                if candidato['score'] < best_score:
                    best_score = candidato['score']
                    best_candidate = candidato
                elif candidato['score'] == best_score:
                    if best_candidate is None:
                        best_candidate = candidato
                    else:
                        #Usar SPT como desempate
                        temp_candidato = candidato['std_time']
                        temp_best = best_candidate['std_time']
                        if temp_candidato < temp_best:
                            best_candidate = candidato
                        #Se continuarem empatados até no tempo, usa o ID
                        elif temp_candidato == temp_best:
                            if candidato['vehicle_id'] < best_candidate['vehicle_id']:
                                best_candidate = candidato
                
            #Recuperar dados do 'vencedor'
            vehicle_id = best_candidate['vehicle_id']
            task_type = best_candidate['task_type']
            std_time = best_candidate['std_time']

            #Encontrar o melhor recurso
            best_end = float('inf')
            best_start = -1
            best_op = -1
            best_ws = -1

            #Fator de desempate (pequeno bónus para manter o mesmo recurso)
            bonus_continuidade = 0.1

            ops = self.instance.task_operators[task_type]
            wss = self.instance.task_workstations[task_type]

            #Verificar quem foram os últimos recursos usados por este veículo
            prev_op = last_resources.get(vehicle_id, {}).get('op', -1)
            prev_ws = last_resources.get(vehicle_id, {}).get('ws', -1)

            for op in ops:
                eff = self.instance.efficiency[task_type][op]
                if eff is None: continue

                duracao_real = int(round(std_time * eff))

                #Quando o operador e o veículo estão livres
                start_op = max(vehicle_free_time[vehicle_id], operators_free_time[op])

                for ws in wss:
                    #Quando a workstation está livre
                    start_final = max(start_op, workstation_free_time[ws])
                    end_final = start_final + duracao_real

                    #Cálculo do custo ajustado (para desempate)
                    custo_comparacao = end_final

                    #Se não for o mesmo operador, penalizamos
                    if op != prev_op and prev_op != -1:
                        custo_comparacao += bonus_continuidade
                        
                    #Se não for a mesma workstation, penalizamos
                    if ws != prev_ws and prev_ws != -1:
                        custo_comparacao += bonus_continuidade 
                        
                    #Se houver um tempo final menor, atualizamos
                    if custo_comparacao < best_end:
                        best_end = custo_comparacao
                        real_best_end =  end_final
                        best_start = start_final
                        best_op = op
                        best_ws = ws
                    
            #Agendar tarefa
            if best_op != -1:
                #Criar registo de tarefa
                task_data = {
                    'task_type': task_type,
                    'start': best_start,
                    'end': real_best_end,
                    'operator': best_op,
                    'workstation': best_ws
                }
                solution.lineup[vehicle_id].append(task_data)
                sequencia_log.append(vehicle_id+1)

                #Atualiza tempos livres
                operators_free_time[best_op] = real_best_end
                workstation_free_time[best_ws] = real_best_end
                vehicle_free_time[vehicle_id] = real_best_end

                #Atualiza o rastreio de recursos
                last_resources[vehicle_id] = {'op': best_op, 'ws': best_ws}

                #Avançar para a próxima tarefa
                next_task_id[vehicle_id] += 1

                #Se acabarem as tarefas deste veículo, é removido da lista
                if next_task_id[vehicle_id] >= len(self.instance.vehicle_tasks[vehicle_id]):
                    vehicles_undone_tasks.remove(vehicle_id)
            else:
                print(f"Erro: Não foi possível agendar a tarefa {task_type} do veículo {vehicle_id}")
                vehicles_undone_tasks.remove(vehicle_id)

        sequencia_unica = []                        
        for v in sequencia_log:
            if v not in sequencia_unica:
                sequencia_unica.append(v)
        print(f"[{rule}] Ordem de Entrada de Veículos: {'-'.join(map(str,sequencia_unica))}")

        return solution