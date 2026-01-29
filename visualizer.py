import matplotlib.pyplot as plt
import os

def generate_gantt_chart(solution, filename, pasta_destino="Gantt_Charts"):

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    fig, (ax1,ax2) = plt.subplots(2,1,figsize=(12,10),sharex=True)

    cores = ['red','blue','green','orange','yellow','brown','cyan','gray','pink','magenta','indigo', 'salmon','olive','teal','turquoise']
    #Percorrer cada veículo e as respetivas tarefas na solução
    for vehicle_id, tasks in solution.lineup.items():
        cor_atual = cores[vehicle_id % len(cores)] #Selecionar a cor com base no ID do veículo

        for t in tasks:
            #Extrair os dados da tarefa (recursos e tempos)
            op=t['operator']
            ws=t['workstation']
            inicio=t['start']
            duracao=t['end']-t['start']
            meio_x=inicio+(duracao/2) #Calcular a posição média para centrar o texto
            #Desenhar barras no gráfico
            ax1.barh(y=op, width=duracao, left=inicio, color=cor_atual, edgecolor='black',height=0.6)
            ax1.text(meio_x,op,f"V{vehicle_id+1}",ha='center',va='center',color='black',fontsize=7)

            ax2.barh(y=ws, width=duracao, left=inicio, color=cor_atual, edgecolor='black', height=0.6)
            ax2.text(meio_x,ws,f"V{vehicle_id+1}",ha='center',va='center',color='black',fontsize=7)
    #Configurar o eixo Y dos operadores
    num_ops=solution.instance.num_operators
    ax1.set_yticks(range(num_ops))
    nome_ops=[]
    for i in range(num_ops):
        nome_ops.append(f"Op {i+1}")
    ax1.set_yticklabels(nome_ops)
    ax1.set_title(f"Ocupação dos Operadores - {filename}")
    ax1.grid(True, axis='x', linestyle='--',alpha=0.5)
    
    num_ws=solution.instance.num_workstations
    ax2.set_yticks(range(num_ws))
    nome_ws=[]
    for i in range(num_ws):
        nome_ws.append(f"Ws {i+1}")
    ax2.set_yticklabels(nome_ws)
    ax2.set_title(f"Ocupação dos Postos de Trabalho - {filename}")
    ax2.grid(True, axis='x', linestyle='--',alpha=0.5)
    ax2.set_xlabel("Tempo (minutos)")
    
    plt.tight_layout()

    caminho = os.path.join(pasta_destino, f"Gantt_{filename}.png")
    plt.savefig(caminho)
    plt.close()
    print(f" -> Gráficos guardados: {caminho}")