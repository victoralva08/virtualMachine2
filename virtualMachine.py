# Victor Ferreira Alvarenga

from random import randint
from typing import *

# ----------------------- Execução do programa -----------------------

class Programas:
    def __init__(self) -> None:
        self.ram: MemoriaRAM = MemoriaRAM(1000) # inicializa a memoria RAM com 1000 slots (blocos de memoria)
        self.cpu: CPU = CPU(16, 32, 64) # instancia a CPU

        self.numeroDeInstrucoes: int = 10000

        self.programa_aleatorio_repeticoes()

    def programa_aleatorio_repeticoes(self) -> None:
        programa: list[Instrucao] = [Instrucao(0, None, None, None)] * (self.numeroDeInstrucoes + 1)

        with open("instructions.txt", "r") as instructionsFile: 
            
            next(instructionsFile) # ignora a primeira linha, que informa o numero de instrucoes        
            indexDeInstrucao = 0

            for instructionLine in instructionsFile:
                instructionLine = instructionLine.strip().split()
                
                uma_instrucao = Instrucao(0, None, None, None) # instancia uma instrucao para o programa

                uma_instrucao.opcode = int(instructionLine[0])

                end1 = Endereco(0, 0)
                end1.endBloco = int(instructionLine[1]) # obtem endereco do bloco
                end1.endPalavra = int(instructionLine[2]) # obtem endereco da palavra dentro do bloco (o endereco da palavra esta no range 0 a 3)
                uma_instrucao.end1 = end1
                
                end2 = Endereco(0, 0)
                end2.endBloco = int(instructionLine[3])
                end2.endPalavra = int(instructionLine[4])
                uma_instrucao.end2 = end2
                
                end3 = Endereco(0, 0)
                end3.endBloco = int(instructionLine[5])
                end3.endPalavra = int(instructionLine[6])
                uma_instrucao.end3 = end3

                programa[indexDeInstrucao] = uma_instrucao
                indexDeInstrucao += 1
        
        # insere a ultima instrucao do programa: HALT
        uma_instrucao = Instrucao(0, None, None, None)
        uma_instrucao.opcode = -1 # instrucao HALT
        uma_instrucao.end1 = Endereco(0, 0)
        uma_instrucao.end2 = Endereco(0, 0)
        uma_instrucao.end3 = Endereco(0, 0)
        programa[self.numeroDeInstrucoes] = uma_instrucao

        self.cpu.set_programa(programa) # envia o programa para a CPU
        self.cpu.iniciar_processo_CPU(self.ram)


# ----------------------- Declaracao das classes de memoria -----------------------

class Endereco:
    def __init__(self, endBloco: int, endPalavra: int) -> None:
        self.endBloco: int = endBloco
        self.endPalavra: int = endPalavra

class Instrucao:
    def __init__(self, opcode: int | None, end1: Endereco | None, end2: Endereco | None, end3: Endereco | None) -> None:
        self.opcode: int = opcode
        self.end1: Endereco = end1
        self.end2: Endereco = end2
        self.end3: Endereco = end3

class BlocoDeMemoria: # um bloco de memoria comporta 4 palavras (otimizacao de esforço: trazer uma quantidade suficiente de palavras!)
    def __init__(self) -> None:
        self.palavras: list[int] = [0] * 4
        self.endBloco: int = 0
        self.atualizado: bool = False
        self.custo_de_acesso: int = 0
        self.cache_hit: int = 0
        self.ultimo_acesso: int = 0

class MemoriaRAM:
    def __init__(self, tamanhoDaRAM: int) -> None:
        self.memoria: list[BlocoDeMemoria] = [BlocoDeMemoria() for _ in range(tamanhoDaRAM)]

        for i in range(tamanhoDaRAM):
            self.memoria[i].endBloco = i
            self.memoria[i].palavras = [randint(0, 100) for _ in range(4)]

    def definir_conteudo(self, enderecoBlocoNaRAM: int, conteudo: BlocoDeMemoria) -> None:
        self.memoria[enderecoBlocoNaRAM] = conteudo
    
    def acessar_conteudo(self, enderecoBlocoNaRAM: int) -> BlocoDeMemoria:
        return self.memoria[enderecoBlocoNaRAM]
    


# ----------------------- Declaracao das classes de processamento -----------------------

tempo_global_de_execucao = 0 # contador para representar o tempo de uso, utilizado para registrar blocos mais recentemente acessados

class MMU:
    def __init__(self, tamanhoCache1: int, tamanhoCache2: int, tamanhoCache3: int) -> None:
        self.tamanhoCache1 = tamanhoCache1
        self.tamanhoCache2 = tamanhoCache2
        self.tamanhoCache3 = tamanhoCache3

    def buscar_nas_caches(self, endereco: Endereco, ram: MemoriaRAM, cache1: list[BlocoDeMemoria], cache2: list[BlocoDeMemoria], cache3: list[BlocoDeMemoria]) -> BlocoDeMemoria:
        global tempo_global_de_execucao

        for bloco in cache1:
            if bloco.endBloco == endereco.endBloco:
                bloco.ultimo_acesso = tempo_global_de_execucao
                bloco.custo_de_acesso = 10
                bloco.cache_hit = 1
                tempo_global_de_execucao += 1
                return bloco

        for i, bloco in enumerate(cache2):
            if bloco.endBloco == endereco.endBloco:
                bloco.ultimo_acesso = tempo_global_de_execucao
                bloco.custo_de_acesso = 110
                bloco.cache_hit = 2
                return self.mov_cache2_cache1(i, cache1, cache2)

        for i, bloco in enumerate(cache3):
            if bloco.endBloco == endereco.endBloco:
                bloco.ultimo_acesso = tempo_global_de_execucao
                bloco.custo_de_acesso = 1110
                bloco.cache_hit = 3
                return self.mov_cache3_cache2(i, cache1, cache2, cache3)

        return self.mov_ram_cache3(cache1, cache2, cache3, ram, endereco)

    def mov_cache2_cache1(self, posicao_cache2: int, cache1: list[BlocoDeMemoria], cache2: list[BlocoDeMemoria]) -> BlocoDeMemoria:
        global tempo_global_de_execucao

        if len(cache1) < self.tamanhoCache1:
            cache1.append(cache2[posicao_cache2])
            cache2.pop(posicao_cache2)
            posicao_cache1 = len(cache1) - 1
        else:
            posicao_cache1 = 0
            acesso_mais_antigo = cache1[0].ultimo_acesso
            for i in range(1, len(cache1)):
                if cache1[i].ultimo_acesso < acesso_mais_antigo:
                    acesso_mais_antigo = cache1[i].ultimo_acesso
                    posicao_cache1 = i

            aux = cache1[posicao_cache1]
            cache1[posicao_cache1] = cache2[posicao_cache2]
            cache2[posicao_cache2] = aux
            cache1[posicao_cache1].ultimo_acesso = tempo_global_de_execucao

        tempo_global_de_execucao += 1
        return cache1[posicao_cache1]

    def mov_cache3_cache2(self, posicao_cache3: int, cache1: list[BlocoDeMemoria], cache2: list[BlocoDeMemoria], cache3: list[BlocoDeMemoria]):

        if len(cache2) < self.tamanhoCache2:
            cache2.append(cache3[posicao_cache3])
            cache3.pop(posicao_cache3)
            posicao_cache2 = len(cache2) - 1
        else:
            posicao_cache2 = 0
            acesso_mais_antigo = cache2[0].ultimo_acesso
            for i in range(1, len(cache2)):
                if cache2[i].ultimo_acesso < acesso_mais_antigo:
                    acesso_mais_antigo = cache2[i].ultimo_acesso
                    posicao_cache2 = i

            aux = cache2[posicao_cache2]
            cache2[posicao_cache2] = cache3[posicao_cache3]
            cache3[posicao_cache3] = aux

        return self.mov_cache2_cache1(posicao_cache2, cache1, cache2)

    def mov_ram_cache3(self, cache1: list[BlocoDeMemoria], cache2: list[BlocoDeMemoria], cache3: list[BlocoDeMemoria], ram: MemoriaRAM, endereco: Endereco):
        posicao_cache3 = 0

        if len(cache3) < self.tamanhoCache3:
            cache3.append(ram.acessar_conteudo(endereco.endBloco))
            posicao_cache3 = len(cache3) - 1
        else:
            acesso_mais_antigo = cache3[0].ultimo_acesso
            for i in range(1, len(cache3)):
                if cache3[i].ultimo_acesso < acesso_mais_antigo:
                    acesso_mais_antigo = cache3[i].ultimo_acesso
                    posicao_cache3 = i
                
            
            blocoAtualizado = cache3[posicao_cache3]
            
            cache3[posicao_cache3] = ram.acessar_conteudo(endereco.endBloco)
            cache3[posicao_cache3].cacheHit = 0
            cache3[posicao_cache3].custo_de_acesso = 11110

            if cache3[posicao_cache3].atualizado == True:
                ram.definir_conteudo(posicao_cache3, blocoAtualizado)

        return self.mov_cache3_cache2(posicao_cache3, cache1, cache2, cache3)

class CPU:
    def __init__(self, tamanhoCache1: int, tamanhoCache2: int, tamanhoCache3: int) -> None:
        
        self.PC: int = 0 # contador para indicar a instrucao a ser executada
        self.opcode: int = 0
        self.programa: list[Instrucao] = []

        # contagem de custos e hits/misses nas caches
        self.custo_total_da_operacao: int = 0

        self.missC1: int = 0
        self.hitC1: int = 0

        self.missC2: int = 0
        self.hitC2: int = 0

        self.missC3: int = 0
        self.hitC3: int = 0

        self.cache1: list[BlocoDeMemoria] = self.__iniciar_cache()
        self.cache2: list[BlocoDeMemoria] = self.__iniciar_cache()
        self.cache3: list[BlocoDeMemoria] = self.__iniciar_cache()

        self.MMU = MMU(tamanhoCache1, tamanhoCache2, tamanhoCache3)

    def __iniciar_cache(self) -> list[BlocoDeMemoria]:
        cache: list[BlocoDeMemoria] = [] # a cache inicializa vazia
        return cache
    
    def set_programa(self, programa: list[Instrucao]) -> None:
        self.programa = programa
    
    def iniciar_processo_CPU(self, ram: MemoriaRAM) -> None:
        while self.opcode != -1: # enquanto nao encontrar a instrucao HALT, realizar ciclos de operacoes

            instrucao = self.programa[self.PC]
            self.opcode = instrucao.opcode

            blocoDeMemoria1: BlocoDeMemoria = self.MMU.buscar_nas_caches(instrucao.end1, ram, self.cache1, self.cache2, self.cache3)
            blocoDeMemoria2: BlocoDeMemoria = self.MMU.buscar_nas_caches(instrucao.end2, ram, self.cache1, self.cache2, self.cache3)
            blocoDeMemoria3: BlocoDeMemoria = self.MMU.buscar_nas_caches(instrucao.end3, ram, self.cache1, self.cache2, self.cache3)
            
            enderecoPalavra1 = instrucao.end1.endPalavra
            enderecoPalavra2 = instrucao.end2.endPalavra
            enderecoPalavra3 = instrucao.end3.endPalavra

            if blocoDeMemoria1.cache_hit == 1:
                self.hitC1 += 1
            elif blocoDeMemoria1.cache_hit == 2:
                self.missC1 += 1
                self.hitC2 += 1
            elif blocoDeMemoria1.cache_hit == 3:
                self.missC1 += 1
                self.missC2 += 1
                self.hitC3 += 1
            else: # teve que acessar a RAM
                self.missC1 += 1
                self.missC2 += 1
                self.missC3 += 1
            
           
            if blocoDeMemoria2.cache_hit == 1:
                self.hitC1 += 1
            elif blocoDeMemoria2.cache_hit == 2:
                self.missC1 += 1
                self.hitC2 += 1
            elif blocoDeMemoria2.cache_hit == 3:
                self.missC1 += 1
                self.missC2 += 1
                self.hitC3 += 1
            else: # teve que acessar a RAM
                self.missC1 += 1
                self.missC2 += 1
                self.missC3 += 1
            
            
            if blocoDeMemoria3.cache_hit == 1:
                self.hitC1 += 1
            elif blocoDeMemoria3.cache_hit == 2:
                self.missC1 += 1
                self.hitC2 += 1
            elif blocoDeMemoria3.cache_hit == 3:
                self.missC1 += 1
                self.missC2 += 1
                self.hitC3 += 1
            else: # teve que acessar a RAM
                self.missC1 += 1
                self.missC2 += 1
                self.missC3 += 1

            # Execucao da instrucao de acordo com o opcode:
            if self.opcode == 1: # SOMA
                blocoDeMemoria3.palavras[enderecoPalavra3] = blocoDeMemoria1.palavras[enderecoPalavra1] + blocoDeMemoria2.palavras[enderecoPalavra2]

                for bloco in self.cache1:
                    if bloco.endBloco == blocoDeMemoria3.endBloco:
                        bloco.atualizado = True

                self.custo_total_da_operacao += blocoDeMemoria1.custo_de_acesso + blocoDeMemoria2.custo_de_acesso + blocoDeMemoria3.custo_de_acesso

                print(f"Soma -> RAM posição {instrucao.end1.endBloco} com conteúdo da cache 1: {blocoDeMemoria2.palavras[enderecoPalavra2]}")
                print(f"Custo até o momento: {self.custo_total_da_operacao}")
                print(f"Hit C1: {self.hitC1} Miss C1: {self.missC1}")
                print(f"Hit C2: {self.hitC2} Miss C2: {self.missC2}")
                print(f"Hit C3: {self.hitC3} Miss C3: {self.missC3}")
            
            elif self.opcode == 2: # SUBTRACAO
                blocoDeMemoria3.palavras[enderecoPalavra3] = blocoDeMemoria1.palavras[enderecoPalavra1] - blocoDeMemoria2.palavras[enderecoPalavra2]

                for bloco in self.cache1:
                    if bloco.endBloco == blocoDeMemoria3.endBloco:
                        bloco.atualizado = True

                self.custo_total_da_operacao += blocoDeMemoria1.custo_de_acesso + blocoDeMemoria2.custo_de_acesso + blocoDeMemoria3.custo_de_acesso

                print(f"Subtração -> RAM posição {instrucao.end1.endBloco} com conteúdo da cache 1: {blocoDeMemoria2.palavras[enderecoPalavra2]}")
                print(f"Custo até o momento: {self.custo_total_da_operacao}")
                print(f"Hit C1: {self.hitC1} Miss C1: {self.missC1}")
                print(f"Hit C2: {self.hitC2} Miss C2: {self.missC2}")
                print(f"Hit C3: {self.hitC3} Miss C3: {self.missC3}")

            self.PC += 1


programa = Programas()
programa.programa_aleatorio_repeticoes()