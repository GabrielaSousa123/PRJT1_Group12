class Tester:

    def __init__(self, instance):
        self.instance = instance

        self.benchmark={
            "Inst_1D_5_1.txt": (65.70, 33.31),
            "Inst_1D_5_2.txt": (64.86, 32.51),
            "Inst_1D_5_3.txt": (65.77, 34.29),
            "Inst_1D_5_4.txt": (65.61, 32.95),
            "Inst_1D_5_5.txt": (67.14, 33.92),
            "Inst_1D_5_6.txt": (64.71, 33.37),
            "Inst_1D_5_7.txt": (68.41, 34.21),
            "Inst_1D_5_8.txt": (65.11, 32.57),
            "Inst_1D_5_9.txt": (67.59, 34.56),
            "Inst_1D_5_10.txt": (65.57, 32.89),

            "Inst_1D_10_1.txt": (85.93, 43.73),
            "Inst_1D_10_2.txt": (83.24, 42.73),
            "Inst_1D_10_3.txt": (81.41, 43.66),
            "Inst_1D_10_4.txt": (77.77, 46.21),
            "Inst_1D_10_5.txt": (77.20, 40.17),
            "Inst_1D_10_6.txt": (84.14, 45.01),
            "Inst_1D_10_7.txt": (83.01, 42.33),
            "Inst_1D_10_8.txt": (90.07, 46.47),
            "Inst_1D_10_9.txt": (80.34, 42.25),
            "Inst_1D_10_10.txt": (81.93, 43.26),

            "Inst_1D_15_1.txt": (95.54, 48.11),
            "Inst_1D_15_2.txt": (72.94, 37.95),
            "Inst_1D_15_3.txt": (84.41, 43.95),
            "Inst_1D_15_4.txt": (77.49, 39.33),
            "Inst_1D_15_5.txt": (91.10, 48.61),
            "Inst_1D_15_6.txt": (78.40, 42.80),
            "Inst_1D_15_7.txt": (96.71, 48.73),
            "Inst_1D_15_8.txt": (75.34, 41.02),
            "Inst_1D_15_9.txt": (92.84, 48.36),
            "Inst_1D_15_10.txt": (88.67, 45.29),
        }
    
    def comparacao_benchmark(self, solution, filename):
        total_proc_time = 0 
        for tasks in solution.lineup.values():
            for t in tasks:
                total_proc_time += (t['end']-t['start'])
        if solution.makespan>0:
            cap_ops = solution.makespan * self.instance.num_operators
            cap_ws = solution.makespan * self.instance.num_workstations
            solution.op_occu = (total_proc_time/cap_ops)*100
            solution.ws_occu = (total_proc_time/cap_ws)*100
        else:
            solution.op_occu = 0.0
            solution.ws_occu = 0.0

        bench_vals = self.benchmark.get(filename)
        result = {
            'RefOccuO': "N/A", 'DiffO': "N/A",
            'RefOccuW': "N/A", 'DiffW': "N/A"
        }
        if bench_vals:
            bench_op, bench_ws = bench_vals
            diff_op = solution.op_occu - bench_op
            diff_ws = solution.ws_occu - bench_ws

            result['RefOccuO']=bench_op
            result['DiffO']=f"{diff_op:+.2f}%"
            result['RefOccuW']=bench_ws
            result['DiffW']=f"{diff_ws:+.2f}%"
        return result

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




