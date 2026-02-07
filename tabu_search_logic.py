import time

def evaluate_sequence(sequence, lineup_obj, tester_obj):
    #Gerar a solução baseada numa ordem específica
    sol = lineup_obj.criar_solucao(sequence=sequence)
    mk, tard, changes, espera = tester_obj.evaluate(sol)

    #Penalizar fortemente se houver atraso
    if tard > 0:
        return (10**15 + tard), sol
    
    #Custo hierárquico: Makespan > Trocas > Espera
    cost = (mk * 10**9) + (changes *10**3) + espera
    return cost, sol

def swap_operator(route, i, j):
    #Troca dois elementos de posição
    new_route = route[:]
    new_route[i], new_route[j] = new_route[j], new_route[i]
    return new_route

def insertion_operator(route, i, j):
    if i == j: return None
    #Remove de i e insere em j
    new_route = route[:]
    val = new_route.pop(i)
    new_route.insert(j, val)
    return new_route

def run_tabu_search(instance, tester, lineup, initial_sequence, iterations = 500, tabu_size = 30, max_seconds = 60):
    start_ts = time.time() #Marcar o tempo de início
    n = len(initial_sequence)
    #Avaliar a solução inicial
    current_seq = initial_sequence[:]
    current_cost, current_sol = evaluate_sequence(current_seq, lineup, tester)
    #Definir o melhor global até agora
    best_seq, best_cost, best_sol_obj = current_seq[:], current_cost, current_sol
    tabu_list = []

    print(f"    [TS] Início | MK: {best_sol_obj.makespan:.2f} | Foco: Caminho Crítico")

    for it in range(iterations):
        if time.time() - start_ts > max_seconds: break #Para se exceder o tempo limite

        best_neighbor_seq = None
        best_neighbor_cost = float('inf')
        best_move = None
        temp_sol_obj = None
        #Percorrer todos os pares para gerar vizinhança
        for i in range(n):
            for j in range(n):
                if i == j: continue
                
                #Definir moves possíveis
                moves = [
                    ('swap', min(i, j), max(i,j), swap_operator(current_seq, i, j)),
                    ('insert', i, j, insertion_operator(current_seq, i, j))
                ]

                for m_type, m_i, m_j, neighbor in moves:
                    if neighbor is None: continue
                    move_key = (m_type, m_i, m_j)
                    cost, sol_obj = evaluate_sequence(neighbor, lineup, tester) #Avaliar vizinho gerado

                    #Aspiração: aceita movimento tabu se for melhor que o melhor global
                    if (move_key not in tabu_list) or (cost < best_cost):
                        if cost < best_neighbor_cost:
                            best_neighbor_cost, best_neighbor_seq, best_move, temp_sol_obj = cost, neighbor, move_key, sol_obj

        if best_neighbor_seq is None: break
        #Atualizar solução corrente
        current_seq, current_cost = best_neighbor_seq, best_neighbor_cost
        #Atualizar lista Tabu. Se estiver cheia, remove o mais antigo
        tabu_list.append(best_move)
        if len(tabu_list) > tabu_size: tabu_list.pop(0)
        #Atualizar o melhor global se encontrar um superior
        if current_cost < best_cost:
            best_cost, best_seq, best_sol_obj = current_cost, current_seq[:], temp_sol_obj

    print(f"    [TS] Fim | Melhor MK: {best_sol_obj.makespan:.2f}")
    return best_seq, best_sol_obj, []




