import time

def evaluate_sequence(sequence, lineup_obj, tester_obj):
    """Avalia a sequência com pesos para respeitar a hierarquia do enunciado[cite: 63, 67]."""
    sol = lineup_obj.criar_solucao(sequence=sequence)
    mk, tard, changes, espera = tester_obj.evaluate(sol)

    #Penalização severa se violar o prazo (Hard Constraint) [cite: 57, 124]
    if tard > 0:
        return (10**15 + tard), sol
    
    #Custo hierárquico: Makespan > Trocas > Espera
    cost = (mk * 10**9) + (changes *10**3) + espera
    return cost, sol

def get_critical_vehicles(solution):
    """Identifica os veículos que terminam perto do Makespan (o gargalo)."""
    mk = solution.makespan
    #Veículos que terminam nos últimos 15% do tempo total
    threshold = mk * 0.85
    return [v_id for v_id, tasks in solution.lineup.items() if tasks and tasks[-1]['end'] >= threshold]

def swap_operator(route, i, j):
    new_route = route[:]
    new_route[i], new_route[j] = new_route[j], new_route[i]
    return new_route

def insertion_operator(route, i, j):
    if i == j: return None
    new_route = route[:]
    val = new_route.pop(i)
    new_route.insert(j, val)
    return new_route

def run_tabu_search(instance, tester, lineup, initial_sequence, iterations = 500, tabu_size = 30, max_seconds = 60):
    start_ts = time.time()
    n = len(initial_sequence)

    current_seq = initial_sequence[:]
    current_cost, current_sol = evaluate_sequence(current_seq, lineup, tester)

    best_seq, best_cost, best_sol_obj = current_seq[:], current_cost, current_sol
    tabu_list = []

    print(f"    [TS] Início | MK: {best_sol_obj.makespan} | Foco: Caminho Crítico")

    for it in range(iterations):
        if time.time() - start_ts > max_seconds: break

        #Identificação de veículos no gargalo da produção
        critical_v = get_critical_vehicles(best_sol_obj)

        best_neighbor_seq = None
        best_neighbor_cost = float('inf')
        best_move = None
        temp_sol_obj = None

        for i in range(n):
            for j in range(n):
                if i == j: continue

                #SÓ EXPLORA se um dos veículos envolvidos for CRÍTICO
                if current_seq[i] not in critical_v and current_seq[j] not in critical_v:
                    continue

                moves = [
                    ('swap', min(i, j), max(i,j), swap_operator(current_seq, i, j)),
                    ('insert', i, j, insertion_operator(current_seq, i, j))
                ]

                for m_type, m_i, m_j, neighbor in moves:
                    if neighbor is None: continue
                    move_key = (m_type, m_i, m_j)
                    cost, sol_obj = evaluate_sequence(neighbor, lineup, tester)

                    #Aspiração: aceita movimento tabu se for melhor que o melhor global
                    if (move_key not in tabu_list) or (cost < best_cost):
                        if cost < best_neighbor_cost:
                            best_neighbor_cost, best_neighbor_seq, best_move, temp_sol_obj = cost, neighbor, move_key, sol_obj

            if best_neighbor_seq is None: break

            current_seq, current_cost = best_neighbor_seq, best_neighbor_cost
            tabu_list.append(best_move)
            if len(tabu_list) > tabu_size: tabu_list.pop(0)

            if current_cost < best_cost:
                best_cost, best_seq, best_sol_obj = current_cost, current_seq[:], temp_sol_obj

    print(f"    [TS] Fim | Melhor MK: {best_sol_obj.makespan}")
    return best_seq, best_sol_obj, []




