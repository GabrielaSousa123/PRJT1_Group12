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
                    
                    if is_better:
                        min_makespan=mk
                        min_changes=changes
                        min_espera=espera
                        best_sol=sol
                        best_rule=r
                
                if best_sol is None:
                    best_sol = fallback_sol
                    best_rule = fallback_rule
                    print(f"FALLBACK: Nenhuma regra evitou atrasos. Selecionada {best_rule} (Menor atraso: {best_sol.total_tardiness})")
                else:
                    print(f"SUCESSO: Regra {best_rule} cumpriu todos os prazos")
                        
                temp_exec = time.time() - start

                if best_sol is not None:
                    save_file_for_solution(best_sol,filename)
                    viewdays(best_sol,filename)
                    generate_gantt_chart(best_sol, f"{filename}","graficos")

                    print(f" -> Vencedora: {best_rule}")
                    print(f" -> Makespan: {best_sol.makespan} | Trocas: {best_sol.total_changes} | Espera: {best_sol.total_tempo_espera}")
                    print(f" -> A validar a melhor solução ({best_rule})...")
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
