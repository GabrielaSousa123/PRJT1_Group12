import os 
import math

def save_file_for_solution(solution,filename):
    if not os.path.exists("results"):
        os.makedirs("results")

    file_path = os.path.join ("results", f"Result_{filename}")

    total_proc_time = 0
    for tasks in solution.lineup.values():
        for t in tasks:
            total_proc_time += (t['end']-t['start'])
    
    solution.op_occu = 0.0
    solution.ws_occu = 0.0

    if solution.makespan > 0.0:
        cap_ops = solution.makespan * solution.instance.num_operators
        cap_ws = solution.makespan * solution.instance.num_workstations

        solution.op_occu = (total_proc_time/cap_ops) * 100
        solution.ws_occu = (total_proc_time/cap_ws) * 100
    
    with open(file_path, "w", encoding='utf-8') as f:
        f.write("[OccuO(%)]\n")
        f.write(f"{solution.op_occu:.2f}\n")

        f.write("[OccuW(%)]\n")
        f.write(f"{solution.ws_occu:.2f}\n")

        f.write("[Makespan]\n")
        f.write(f"{solution.makespan}\n")

        for vehicle_id in sorted(solution.lineup.keys()):
            tasks = solution.lineup[vehicle_id]
            f.write("[vehicle_id]\n")
            f.write(f"{vehicle_id+1}\n")
            f.write("[tasks\toperator\tworkstation\tprocessingTime\tstartTime\tcompleteTime]\n")

            for t in tasks:
                line = f"{t['task_type']+1}\t{t['operator']+1}\t{t['workstation']+1}\t"\
                    f"{t['end']-t['start']}\t{t['start']}\t{t['end']}\n"
                f.write(line)

def save_summary_file(results_list):
    if not os.path.exists("results"):
        os.makedirs("results")
    
    path = os.path.join("results", "Summary_Results.txt")

    with open(path,"w",encoding='utf-8') as f:
        f.write(f"{'Instance':<20}| "
                f"{'Makes':<8}| "
                f"{'Tard':<6}| " 
                f"{'Rule':<8}| "
                f"{'Op(%)':<8}{'Ref(%)':<8}{'Dif':<9}| "
                f"{'Ws(%)':<8}{'Ref(%)':<8}{'Dif':<9}| "
                f"{'Time':<8}\n")
        f.write("-" * 110 + "\n")

        for res in results_list:
            def fmt(val):
                if isinstance(val, (int,float)):
                    return f"{val:.2f}"
                return str(val)

            line= (
                f"{res['instance']:<20}| "
                f"{res['makespan']:<8}| "
                f"{res['tardiness']:<6}| "
                f"{res['rule']:<8}| "
                
                f"{fmt(res.get('OccuO(%)',0)):<8}{fmt(res.get('RefOccuO','N/A')):<8}{fmt(res.get('DiffO','N/A')):<9}| " 

                f"{fmt(res.get('OccuW(%)',0)):<8}{fmt(res.get('RefOccuW','N/A')):<8}{fmt(res.get('DiffW','N/A')):<9}| " 

                f"{res['time']:<8.4f}"
                )

            f.write(line + "\n")

def viewdays (solution, filename):
    path = os.path.join("results", "ViewDays.txt")
    day_mins = solution.instance.time_day

    with open(path,"a",encoding='utf-8') as f:
        f.write(f"\nInstance: {filename} | Makespan Global: {solution.makespan}\n")
        f.write("-" * 60 + "\n")

        for vehicle_id in sorted(solution.lineup.keys()):
            f.write(f"Veículo {vehicle_id+1}:\n")
            
            for t in solution.lineup[vehicle_id]:
                day_start = (t['start']//day_mins)+1
                min_start = t['start']%day_mins

                end_temp = t['end']
                if end_temp > 0 and end_temp % day_mins == 0:
                    day_end = (end_temp-1) // day_mins + 1
                    min_end = day_mins
                else:
                    day_end = (end_temp // day_mins) + 1
                    min_end = end_temp % day_mins

                aviso_quebra = ""
                if day_end > day_start:
                    aviso_quebra = "[Interrompida pelo Fim do Turno]"
                f.write(f"Task {t['task_type']+1:2}: Dia {day_start} ({min_start:3}m) -> Dia {day_end} ({min_end:3}m) | Op:{t['operator']+1} Ws:{t['workstation']+1} {aviso_quebra}\n")

                
