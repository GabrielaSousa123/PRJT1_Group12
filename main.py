import os
import time
from data_reader import load_txt, Instance
from lineup import LineUp
from tester import Tester
from data_writer import save_file_for_solution, save_summary_file, viewdays
from visualizer import generate_gantt_chart

def main():

    #As regras que vamos testar
    regras = ["EDD", "SPT", "FOLGA", "LPT", "MOPNR", "MWKR", "SRPT", "CR", "LFJ"]

    #Caminho das pastas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    file_shop = os.path.join(input_dir, "Automotive_Repair_Shop.txt")

    #Limpar log antigo
    if os.path.exists("results/ViewDays.txt"):
        os.remove("results/ViewDays.txt")

    print("--- A ler dados da Oficina ---")
    raw_shop = load_txt(file_shop)
    print("Dados da Oficina lidos com sucesso!\n")

    lista_resultados = []

    #Ver todos os ficheiros na pasta input
    for root, dirs, files in os.walk(input_dir):
        for filename in sorted(files):
            if filename.startswith("Inst_") and filename.endswith(".txt"):
                full_path = os.path.join(root, filename)
                print(f"A processar: {filename}")

                start = time.time()

                #Carregar instância
                raw_inst = load_txt(full_path)
                instance = Instance(raw_shop, raw_inst)

                lineup = LineUp(instance)
                tester = Tester(instance)

                #Competição de regras
                best_sol = None
                best_rule = ""

                #Valores iniciais "piores" para garantir que o primeiro teste guarda
                min_makespan = float('inf')
                min_changes = float('inf')
                min_espera = float('inf')
                
                #Variáveis para se não der mesmo para o atraso ser zero
                fallback_sol = None
                fallback_rule = ""
                min_tard_fallback = float('inf')
                min_mk_fallback = float('inf')

                #Percorrer todas as regras definidas na lista
                for r in regras:

                    #Criar solução com a regra R
                    sol = lineup.criar_solucao(rule = r)

                    #Avaliar
                    mk, tard, changes, espera = tester.evaluate(sol)
                    
                    #Variáveis para se o atraso não puder ser zero
                    if tard < min_tard_fallback:
                        min_tard_fallback=tard
                        min_mk_fallback=mk
                        fallback_sol=sol
                        fallback_rule=r
                    elif tard == min_tard_fallback and mk<min_mk_fallback:
                        min_mk_fallback=mk
                        fallback_sol=sol
                        fallback_rule=r
                    
                    #Verificar a validade das restrições
                    sol_valida = tester.verify_solution(sol)
                    if not sol_valida:
                        print(f" -> Regra {r} REJEITADA: Viola restrições")
                        continue

                    #Decidir se é melhor
                    is_better = False
                    if best_sol is None:
                        is_better = True
                    elif mk<min_makespan:
                        is_better=True
                    elif mk == min_makespan:
                        if changes < min_changes:
                            is_better=True
                        elif changes == min_changes:
                            if espera < min_espera:
                                is_better=True
                    #Atualizar a melhor solução se os critérios forem cumpridos
                    if is_better:
                        min_makespan=mk
                        min_changes=changes
                        min_espera=espera
                        best_sol=sol
                        best_rule=r
                #Selecionar a solução de recurso se nenhuma regra cumpriu o prazo
                if best_sol is None:
                    best_sol = fallback_sol
                    best_rule = fallback_rule
                    print(f"FALLBACK: Nenhuma regra evitou atrasos. Selecionada {best_rule} (Menor atraso: {best_sol.total_tardiness})")
                else:
                    print(f"SUCESSO: Regra {best_rule} cumpriu todos os prazos")

                if best_sol is not None:
                    from tabu_search_logic import run_tabu_search

                    #1. Avaliamos a solução da Fase 1 para ter uma base de comparação
                    mk_f1, tard_f1, ch_f1, esp_f1 = tester.evaluate(best_sol)
                    print(f"\n[Fase 2] A otimizar com Tabu Search (Base: {best_rule} - MK: {mk_f1:.2f}...")

                    initial_seq = [v-1 for v in best_sol.sequencia_log]

                    #2. Chamada à TS com o novo parâmetro de tempo (max_seconds)
                    #Definimos 120s (2 min) por ficheiro para não demorar "meia hora" no total
                    ts_seq, ts_sol, ts_history = run_tabu_search(
                        instance, tester, lineup, initial_seq,
                        iterations = 100000, #Aumentamos para explorar mais
                        tabu_size = 30,
                        max_seconds = 20 #Para automaticamente após 2 minutos
                    )

                    #3. Avaliamos o resultado da Tabu Search
                    mk_ts, tard_ts, ch_ts, esp_ts = tester.evaluate(ts_sol)

                    # 4. CRITÉRIO DE ACEITAÇÃO: Seguimos a prioridade do enunciado [cite: 63, 67]
                    # Só aceitamos se: não piorar o atraso E (melhorar o Makespan OU diminuir trocas)
                    is_ts_better = False
                    if tard_ts < tard_f1:
                        is_ts_better = True
                    elif tard_ts == tard_f1:
                        if mk_ts < mk_f1:
                            is_ts_better = True
                        elif mk_ts == mk_f1 and ch_ts < ch_f1: #Desempate pelo Objetivo 2
                            is_ts_better = True

                    if is_ts_better:
                        best_sol = ts_sol
                        best_rule = f"TS_{best_rule}"
                        print(f" -> [SUCESSO] TS melhorou a solução: MK {mk_f1:.2f} -> {mk_ts:.2f}")

                    else:
                        #Se a TS não melhorou nada, mantemos o best_sol que já tínhamos da Fase 1
                        print(f" -> [MANTER] TS não superou a Fase 1. Mantida regra {best_rule} (MK{mk_f1:.2f})")

                temp_exec = time.time() - start

                if best_sol is not None:
                    
                    save_file_for_solution(best_sol,filename) #Guardar os ficheiros de resultados e gerar o gráfico
                    viewdays(best_sol,filename)
                    generate_gantt_chart(best_sol, f"{filename}","graficos")

                    print(f" -> Vencedora: {best_rule}")
                    print(f" -> Makespan: {best_sol.makespan:.2f} | Trocas: {best_sol.total_changes} | Espera: {best_sol.total_tempo_espera:.2f}")
                    print(f" -> A validar a melhor solução ({best_rule})...")
                    #Validar a solução vencedora e comparar com os bechmarks
                    tester.verify_solution(best_sol)
                    bench_data = tester.comparacao_benchmark(best_sol,filename)
                    print()
                

                    lista_resultados.append({
                        'instance': filename,
                        'makespan': best_sol.makespan,
                        'tardiness': best_sol.total_tardiness,
                        'time': temp_exec,
                        'rule': best_rule,
                        'OccuO(%)': best_sol.op_occu,
                        'RefOccuO': bench_data['RefOccuO'],
                        'DiffO': bench_data['DiffO'],
                        'OccuW(%)': best_sol.ws_occu,
                        'RefOccuW': bench_data['RefOccuW'],
                        'DiffW': bench_data['DiffW'],
                    })
                else:
                    print(f"Aviso : Nenhuma regra conseguiu atraso zero para {filename}")  

        save_summary_file(lista_resultados)
        print("Tudo concluído. Verifique a pasta results/.")

if __name__ == "__main__":
    main()
