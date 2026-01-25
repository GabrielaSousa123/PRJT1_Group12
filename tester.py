class Tester:

    def __init__(self, instance):
        self.instance = instance

    def evaluate(self, solution):
        makespan = 0
        atraso_total = 0

        #Iterar pelos veículos e tarefas agendadas
        for vehicle_id, tasks in solution.lineup.items():
            if len(tasks) == 0:
                continue
            
            #O fim da última tarefa é quando o veículo fica pronto
            ultimo_fim = tasks[-1]['end']

            #Atualizar o makespan
            if ultimo_fim > makespan:
                makespan = ultimo_fim

            #Calcular atraso
            prazo = self.instance.due_dates[vehicle_id]
            atraso = max(0, ultimo_fim - prazo)
            atraso_total += atraso 
        
        #Guardar na solução
        solution.makespan = makespan
        solution.total_tardiness = atraso_total

        return makespan, atraso_total

    def verify_solution(self, solution):
        is_valid = True

        usage_operators = {}
        usage_workstations = {}

        #Inicializar listas
        for op in range (self.instance.num_operators): usage_operators[op] = []
        for ws in range (self.instance.num_workstations): usage_workstations[ws] = []

        for vehicle_id, tasks in solution.lineup.items():
            last_end_time = -1

            #Verificar data de chegada
            if tasks:
                if tasks[0]['start'] < self.instance.release_dates[vehicle_id]:
                    print(f"[ERRO] Veículo {vehicle_id} começou ao minuto {tasks[0]['start']} mas só chega ao {self.instance.release_dates[vehicle_id]}")
                    is_valid = False
                
            for t in tasks:
                tt = t['task_type']
                op = t['operator']
                ws = t['workstation']
                start = t['start']
                end = t['end']
                duracao = end - start

                #Verificar competências
                if op not in self.instance.task_operators[tt]:
                    print(f"[ERRO] Operador {op+1} não qualificado para a Tarefa Tipo {tt+1} no Veículo {vehicle_id+1}")
                    is_valid = False
                
                if ws not in self.instance.task_workstations[tt]:
                    print(f"[ERRO] Workstation {ws+1} inválida para a Tarefa Tipo {tt+1} no Veículo {vehicle_id+1}")
                    is_valid = False

                #Verificar precedência
                if start < last_end_time:
                    print(f"[ERRO] Precedência violada no Veículo {vehicle_id+1}. Tarefa começou a {start} mas a anterior acabou a {last_end_time}")
                    is_valid = False
                last_end_time = end

                #Registar uso de recursos para a verificação posterior
                usage_operators[op].append((start, end, vehicle_id))
                usage_workstations[ws].append((start,end, vehicle_id))

        #Verificar sobreposição de recursos
        #Verificar operadores
        for op, intervalos in usage_operators.items():
            intervalos.sort(key = lambda x:x[0])
            for i in range(len(intervalos) - 1):
                t1 = intervalos[i]
                t2 = intervalos[i+1]

                #Se o início do seguinte foi MENOR que o fim do anterior -> Sobreposição
                if t2[0] < t1[1]:
                    print(f"[ERRO] Operador {op+1} sobreposto! V{t1[2]+1} ({t1[0]}-{t1[1]}) colide com V{t2[2]+1} ({t2[0]}-{t2[1]})")
                    is_valid = False
        
        #Verificar workstations
        for ws, intervalos in usage_workstations.items():
            intervalos.sort(key = lambda x:x[0])
            for i in range(len(intervalos) - 1):
                t1 = intervalos[i]
                t2 = intervalos[i+1]

                if t2[0] < t1[1]:
                    print(f"[ERRO] Workstation {ws+1} sobreposta! V{t1[2]+1} ({t1[0]}-{t1[1]}) colide com V{t2[2]+1} ({t2[0]}-{t2[1]})")
                    is_valid = False
        
        if is_valid:
            print(" -> Solução Válida: Todas as restrições são respeitadas.")
        else:
            print(" -> Solução Inválida: Corrigir erros acima.")
        return is_valid




