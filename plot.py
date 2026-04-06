import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

def plot_results(x, y, f, e_cd, e_f, P, L, J, T,w,F,H,seq):
    # Criar um mapa de cores padronizado para todos os produtos (usando tab20 para suportar até 20 cores distintas)
    cor_map = {p: plt.cm.tab20(i % 20) for i, p in enumerate(range(P))}

    # 1. Total Production over time
    plt.figure(figsize=(10, 6))
    for p in range(P):
        prod_t = [sum(x[p, l, t].X for l in range(L)) for t in range(T)]
        plt.plot(range(T), prod_t, marker='o', label=f'Produto {p}', color=cor_map[p])
    plt.title('Produção Total na Fábrica por Produto ao Longo do Tempo')
    plt.xlabel('Período (t)')
    plt.ylabel('Quantidade Produzida')
    plt.xticks(range(T))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(r'gráficos\producao.png')

        # 2. Factory Inventory over time
    plt.figure(figsize=(10, 6))
    for p in range(P):
        est_f = [e_f[p, t].X for t in range(T)]
        plt.plot(range(T), est_f, marker='s', label=f'Produto {p}', color=cor_map[p])
    plt.title('Estoque na Fábrica por Produto ao Longo do Tempo')
    plt.xlabel('Período (t)')
    plt.ylabel('Nível de Estoque')
    plt.xticks(range(T))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(r'gráficos\estoque_fabrica.png')
    
        # 3. Workers over time
    plt.figure(figsize=(10, 6))
    work_per_t = [sum(w[l, t].X for l in range(L)) for t in range(T)]
    plt.plot(range(T),work_per_t, marker = 's', label = f'workers in time')
    plt.title('Qtd de trabalhadores ao Longo do Tempo')
    plt.xlabel('Tempo (t)')
    plt.ylabel('Qtd. Trabalhadores')
    plt.grid(True)
    plt.tight_layout()

    # 3. Accumulated CD Inventory over time
    plt.figure(figsize=(10, 6))
    for p in range(P):
        est_cd = [sum(e_cd[p, j, t].X for j in range(J)) for t in range(T)]
        plt.plot(range(T), est_cd, marker='^', label=f'Produto {p}', color=cor_map[p])
    plt.title('Estoque Agregado nos CDs por Produto ao Longo do Tempo')
    plt.xlabel('Período (t)')
    plt.ylabel('Nível de Estoque')
    plt.xticks(range(T))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(r'gráficos\estoque_cd.png')
    
    # 4. Flux from Factory to CDs over time
    fig, axes = plt.subplots(J, 1, figsize=(10, 3*J), sharex=True)
    if J == 1:
        axes = [axes]
    for j in range(J):
        for p in range(P):
            flux_t = [f[p, j, t].X for t in range(T)]
            axes[j].plot(range(T), flux_t, marker='x', label=f'Produto {p}', color=cor_map[p])
        axes[j].set_title(f'Fluxo para o CD {j}')
        axes[j].set_ylabel('Quantidade Enviada')
        axes[j].legend()
        axes[j].grid(True)
    
    plt.xlabel('Período (t)')
    plt.xticks(range(T))
    plt.tight_layout()
    plt.savefig(r'gráficos\fluxo_cd.png')

    # 5. Sequenciamento de Produtos por Linha ao Longo do Tempo
    if seq:
        plt.figure(figsize=(12, 0.8 * L + 2))
        
        # Determinar todos os produtos para a legenda 
        todos_produtos_seq = set()
        for l1, l2 in seq.values():
            todos_produtos_seq.update(l1)

        # Iterar pelo dicionário seq(l, t) = [lista_produtos, sequencia_ordenada]
        for (l, t), [_, sequencia] in seq.items():
            if not sequencia: continue
            
            n_seq = len(sequencia)
            # Cada período t tem largura 1. Dividimos essa largura entre os produtos da sequência.
            largura_prod = 0.8 / n_seq 
            
            for i, produto in enumerate(sequencia):
                # Calcular posição X: início do período t + deslocamento proporcional à ordem i
                x_inicio = t + (i * (1.0 / n_seq))
                
                plt.barh(l, largura_prod, left=x_inicio, color=cor_map[produto], 
                         edgecolor='black', height=0.6, align='center')
                
                # Adicionar ID do produto no centro da barra se houver espaço
                if largura_prod > 0.05:
                    plt.text(x_inicio + largura_prod/2, l, str(produto), 
                             va='center', ha='center', color='white', 
                             fontsize=7, fontweight='bold')

        plt.title('Sequenciamento de Produtos por Linha (Ordem de Produção)')
        plt.xlabel('Período (t)')
        plt.ylabel('Linha (l)')
        plt.yticks(range(L))
        plt.xticks(range(T))
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Criar legenda baseada nos produtos presentes no sequenciamento
        legend_patches = [mpatches.Patch(color=cor_map[p], label=f'Prod {p}') for p in sorted(todos_produtos_seq)]
        plt.legend(handles=legend_patches, title="Produtos", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize='small')
        
        plt.tight_layout()
        plt.savefig(r'gráficos\sequenciamento.png')




    print("Gráficos salvos: 'producao.png', 'trabalhadores.png', 'estoque_fabrica.png', 'estoque_cd.png', 'fluxo_cd.png' e 'sequenciamento.png'!")
    

    plt.show()
