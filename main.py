import os
import time
from data_reader import load_txt, Instance
from lineup import LineUp
from tester import Tester
from data_writer import save_file_for_solution, save_summary_file, viewdays

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
                min_tardiness = float('inf')
                min_makespan = float('inf')

                for r in regras:

                    #Criar solução com a regra R
                    sol = lineup.criar_solucao(rule = r)

                    #Avaliar
                    mk, tard = tester.evaluate(sol)

                    if sol == best_sol:
                        tester.verify_solution(sol)

                    #Decidir se é melhor
                    if tard < min_tardiness:
                        min_tardiness = tard
                        min_makespan = mk
                        best_sol = sol
                        best_rule = r

                    elif tard == min_tardiness:
                        if mk < min_makespan:
                            min_makespan = mk
                            best_sol = sol
                            best_rule = r
                
                temp_exec = time.time() - start
