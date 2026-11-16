# SISMONITORA

Desenvolva uma aplicação web profissional para a Secretaria de Estado de Saúde do Distrito Federal – SES/DF destinada ao monitoramento dos indicadores do Plano Distrital de Saúde – PDS.

A aplicação deverá automatizar a transformação dos relatórios quadrimestrais extraídos do sistema SESPLAN em banco de dados estruturado, consolidar a série histórica dos indicadores e gerar um painel gerencial para acompanhamento, análise e tomada de decisão.

O sistema será utilizado institucionalmente e deverá priorizar confiabilidade, rastreabilidade, facilidade de atualização, visualização executiva e possibilidade de expansão futura.

1. OBJETIVO GERAL

Criar um sistema de monitoramento do Plano Distrital de Saúde que permita:

Fazer upload dos relatórios extraídos do SESPLAN em PDF.

Identificar automaticamente os indicadores presentes no documento.

Extrair os dados estruturados de cada indicador.

Permitir revisão humana antes da gravação.

Transformar cada relatório em banco de dados.

Incorporar automaticamente novos quadrimestres ao histórico.

Construir séries históricas por indicador.

Calcular automaticamente o desempenho em relação à meta.

Gerar status padronizado de desempenho.

Produzir dashboards gerenciais.

Disponibilizar página detalhada para cada indicador.

Realizar análises automáticas com inteligência artificial.

Preservar as análises originais informadas pelas áreas técnicas.

Identificar inconsistências ou alterações no cadastro dos indicadores.

Exportar o banco consolidado em Excel e CSV.

O sistema deverá inicialmente atender ao PDS 2024–2027, mas sua arquitetura deve permitir a inclusão de outros ciclos de planejamento futuramente.

2. CONTEXTO DO SISTEMA

A SES/DF monitora os indicadores do Plano Distrital de Saúde por meio do SESPLAN.

Periodicamente é gerado um relatório em PDF com os resultados dos indicadores.

O relatório contém uma estrutura hierárquica semelhante a:

EIXO

→ PERSPECTIVA

→ DIRETRIZ

→ OBJETIVO ESTRATÉGICO

→ INDICADORES

Para cada indicador podem aparecer informações como:

código do indicador;

nome do indicador;

meta anual;

periodicidade de monitoramento;

informação se é acumulativo;

polaridade;

área responsável;

análise do resultado;

resultados registrados;

responsável pelo registro.

O PDF não é um banco de dados estruturado. A aplicação deverá transformar automaticamente esse documento em dados relacionais utilizáveis para monitoramento.

3. FLUXO PRINCIPAL DO SISTEMA

O fluxo deverá ser:

UPLOAD DO PDF

→ IDENTIFICAÇÃO DO ANO E QUADRIMESTRE

→ PROCESSAMENTO

→ EXTRAÇÃO DOS INDICADORES

→ CONFERÊNCIA DOS DADOS

→ IDENTIFICAÇÃO DE INCONSISTÊNCIAS

→ CONFIRMAÇÃO DO USUÁRIO

→ GRAVAÇÃO NO BANCO

→ ATUALIZAÇÃO AUTOMÁTICA DO DASHBOARD

→ ATUALIZAÇÃO DAS SÉRIES HISTÓRICAS

→ RECÁLCULO DOS INDICADORES DERIVADOS

→ GERAÇÃO DAS ANÁLISES AUTOMÁTICAS

4. QUADRIMESTRES

No momento do upload, solicitar:

ANO

e

QUADRIMESTRE

Opções:

1º quadrimestre

2º quadrimestre

3º quadrimestre

Utilizar como referência:

1º quadrimestre → abril

2º quadrimestre → agosto

3º quadrimestre → dezembro

Criar automaticamente:

Ano

Período

Mês de referência

Exemplo:

Ano: 2026

Período: 1º quadrimestre

Mês de referência: Abril

5. REGRA PARA RESULTADO DO PERÍODO

Considerar como resultado do quadrimestre o resultado registrado no mês correspondente ao fechamento:

Abril → 1º quadrimestre

Agosto → 2º quadrimestre

Dezembro → 3º quadrimestre

Quando houver resultado:

Apurado no período = Sim

Quando não houver:

Apurado no período = Não

Nunca inventar valores.

Nunca preencher automaticamente um resultado ausente com zero.

NULL, vazio e zero são conceitos diferentes e devem ser preservados.

6. INDICADORES ANUAIS

Indicadores com periodicidade:

Anual

podem não possuir resultado nos primeiros quadrimestres.

Nesses casos:

Resultado do período = NULL

Apurado no período = Não

Status de desempenho = Não apurado

Percentual de alcance da meta = NULL

Não interpretar ausência de apuração como baixo desempenho.

7. BANCO DE DADOS PRINCIPAL

Criar uma tabela principal:

indicadores_pds_resultados

Cada linha deverá representar:

UM INDICADOR EM UM DETERMINADO PERÍODO.

A estrutura deverá conter:

ID

Ano

Período

Número do quadrimestre

Mês de referência

Eixo código

Eixo

Perspectiva código

Perspectiva

Diretriz código

Diretriz

Objetivo

Código indicador

Indicador

Meta anual

Unidade

Monitoramento

Acumulativo

Polaridade

Área responsável

Resultado do período

Apurado no período

Registrado por

Análise do resultado

Meta anual original

Resultado original

Percentual de alcance da meta

Status de desempenho

Diferença absoluta para a meta

Resultado do período anterior

Variação absoluta

Variação percentual

Tendência

Data da importação

ID da importação de origem

8. CAMPOS QUE NÃO DEVEM FAZER PARTE DO BANCO PRINCIPAL

Não incluir:

Meta parcial;

Meta parcial original;

Objetivo código;

Nº PDS;

Status original do SESPLAN.

O sistema utilizará um STATUS PRÓPRIO calculado automaticamente.

9. VALORES ORIGINAIS E NORMALIZADOS

Sempre que possível, manter:

VALOR ORIGINAL

e

VALOR NUMÉRICO NORMALIZADO.

Exemplo:

Meta original:

74,5%

Meta normalizada:

74.5

Outro exemplo:

R$ 681.262.864,01

deve gerar:

Meta original:

R$ 681.262.864,01

Meta numérica:

681262864.01

Outro exemplo:

6.833

quando o contexto demonstrar que representa seis mil oitocentos e trinta e três:

6833

Preservar o campo original para auditoria.

10. UNIDADE DO INDICADOR

Criar o campo:

Unidade

Identificar quando possível:

%

R$

dias

minutos

litros

número absoluto

taxa

coeficiente

razão

proporção

índice

Não inventar unidade quando não houver segurança.

11. CHAVE LÓGICA

Utilizar como chave lógica:

Ano + Período + Código indicador

Exemplo:

2026

1º quadrimestre

SAIS143

Caso seja feito novo upload para período já existente, verificar duplicidade.

Não sobrescrever silenciosamente.

Mostrar:

“Já existem informações deste indicador para este período.”

Oferecer:

Manter registro atual

Substituir pelo novo registro

Comparar alterações

Cancelar

12. CÁLCULO DO PERCENTUAL DE ALCANCE DA META

Criar automaticamente:

Percentual de alcance da meta

O cálculo deverá considerar obrigatoriamente a polaridade.

13. POLARIDADE MAIOR - MELHOR

Para indicadores cuja polaridade seja:

Maior - melhor

calcular:

Percentual de alcance da meta =

(Resultado do período / Meta anual) × 100

Exemplo:

Meta = 80

Resultado = 72

Percentual de alcance = 90%

Outro exemplo:

Meta = 100

Resultado = 65

Percentual de alcance = 65%

Permitir valores acima de 100%.

Exemplo:

Meta = 30

Resultado = 40

Percentual de alcance = 133,33%

Nesse caso:

Status = Ótimo

14. POLARIDADE MENOR - MELHOR

Para indicadores cuja polaridade seja:

Menor - melhor

Se:

Resultado <= Meta

considerar:

Percentual de alcance = 100%

Status = Ótimo

Se:

Resultado > Meta

calcular:

Percentual de alcance =

(Meta / Resultado) × 100

Exemplo:

Meta = 10

Resultado = 20

Percentual de alcance = 50%

Exemplo:

Meta = 10

Resultado = 8

Percentual de alcance = 100%

Status = Ótimo

15. META IGUAL A ZERO

Nunca executar divisão por zero.

Para:

Meta = 0

Polaridade = Menor - melhor

usar:

Resultado = 0

→ Percentual de alcance = 100%

→ Status = Ótimo

Resultado > 0

→ Percentual de alcance = 0%

→ Status = Insuficiente

Se Meta = 0 ocorrer em situação diferente e a regra não puder ser tecnicamente aplicada:

Percentual de alcance = Não calculável

Status = Não calculável

e sinalizar para revisão.

16. CLASSIFICAÇÃO DO DESEMPENHO

Utilizar exclusivamente:

INSUFICIENTE

Percentual de alcance < 50%

MÉDIO

Percentual de alcance >= 50% e < 70%

BOM

Percentual de alcance >= 70% e < 90%

ÓTIMO

Percentual de alcance >= 90%

Portanto:

0 até <50% → Insuficiente

50 até <70% → Médio

70 até <90% → Bom

=90% → Ótimo

Adicionar:

NÃO APURADO

quando não houver resultado.

Adicionar:

NÃO CALCULÁVEL

quando houver impossibilidade matemática ou metodológica de cálculo.

17. APRESENTAÇÃO DO STATUS

Nunca apresentar apenas o nome da categoria.

Mostrar preferencialmente:

STATUS + PERCENTUAL DE ALCANCE

Exemplos:

Ótimo — 103,4% da meta

Ótimo — 96,8% da meta

Bom — 82,4% da meta

Médio — 64,7% da meta

Insuficiente — 38,2% da meta

Não apurado

Isso é importante porque indicadores dentro da mesma categoria podem apresentar desempenhos bastante diferentes.

18. STATUS NÃO DEVE SER EDITÁVEL MANUALMENTE

Status deve ser campo calculado.

Não permitir edição manual direta.

Sempre que forem alterados:

Meta

Resultado

Polaridade

recalcular automaticamente:

Percentual de alcance

Status

Diferença para a meta

19. DIFERENÇA PARA A META

Criar:

Diferença absoluta para a meta

Para Maior - melhor:

Resultado - Meta

Para Menor - melhor:

Meta - Resultado

Apresentar de forma que valores positivos representem situação favorável quando possível.

20. COMPARAÇÃO COM PERÍODO ANTERIOR

Quando existir período anterior para o mesmo código de indicador:

Resultado atual

Resultado anterior

Diferença absoluta

Variação percentual

Tendência

Calcular:

Variação percentual =

((Resultado atual - Resultado anterior) / Resultado anterior) × 100

Não calcular percentual quando resultado anterior = 0.

21. TENDÊNCIA

A tendência deverá respeitar a polaridade.

Para:

Maior - melhor

Resultado atual > anterior → Melhora

Resultado atual < anterior → Piora

Para:

Menor - melhor

Resultado atual < anterior → Melhora

Resultado atual > anterior → Piora

Quando iguais:

Estabilidade

Quando não houver período comparável:

Sem comparação

22. EVOLUÇÃO DO STATUS

Criar hierarquia:

Insuficiente

→ Médio

→ Bom

→ Ótimo

Comparar a classificação atual com a anterior.

Exemplo:

Médio → Bom

= Melhora de classificação

Bom → Ótimo

= Melhora de classificação

Ótimo → Bom

= Piora de classificação

Não apurado não deve ser considerado melhora ou piora.

23. KPI GERENCIAL PRINCIPAL

Criar como um dos KPIs centrais:

INDICADORES COM DESEMPENHO BOM OU ÓTIMO

Exibir:

Quantidade

e

Percentual entre os indicadores apurados.

Fórmula:

Indicadores classificados como Bom + Ótimo

dividido pelo

Total de indicadores apurados

× 100

Exemplo:

48 de 62 indicadores

77,4%

Apresentar em destaque no painel principal.

24. OUTROS CARDS DO DASHBOARD

Criar cards:

Total de indicadores

Indicadores apurados

Indicadores não apurados

% de indicadores apurados

Ótimo

Bom

Médio

Insuficiente

Não apurado

% Bom + Ótimo

% Ótimo

Indicadores com melhora

Indicadores com piora

Indicadores estáveis

Cada card deverá ser clicável e funcionar como filtro.

25. DASHBOARD PRINCIPAL

Criar página:

PAINEL DE MONITORAMENTO DO PDS

Título:

Monitoramento do Plano Distrital de Saúde

Subtítulo:

PDS 2024–2027 | SES/DF

Mostrar inicialmente o período mais recente.

26. FILTROS

Criar filtros:

Ano

Quadrimestre

Eixo

Perspectiva

Diretriz

Objetivo

Área responsável

Periodicidade

Polaridade

Status

Apurado / Não apurado

Código do indicador

Nome do indicador

Faixa de percentual de alcance

Os filtros devem atuar sobre todos os componentes do dashboard.

27. GRÁFICO PRINCIPAL DE STATUS

Criar gráfico de distribuição dos indicadores:

Ótimo

Bom

Médio

Insuficiente

Não apurado

Mostrar:

quantidade

e percentual.

Permitir clicar em cada categoria para filtrar o dashboard.

28. DISTRIBUIÇÃO DE DESEMPENHO POR EIXO

Criar gráfico mostrando, para cada Eixo:

Ótimo

Bom

Médio

Insuficiente

Pode utilizar barra horizontal empilhada.

Permitir comparação visual entre os eixos do PDS.

29. DISTRIBUIÇÃO POR DIRETRIZ

Criar visualização semelhante para:

Diretriz

Mostrar proporção dos status dentro de cada diretriz.

30. DISTRIBUIÇÃO POR OBJETIVO ESTRATÉGICO

Criar visualização por Objetivo.

Permitir ordenar por:

% Bom + Ótimo

do maior para o menor ou vice-versa.

31. DESEMPENHO POR ÁREA RESPONSÁVEL

Criar gráfico ou tabela mostrando:

Área responsável

Total de indicadores

Apurados

Ótimo

Bom

Médio

Insuficiente

% Bom + Ótimo

Permitir ordenação.

32. VISUALIZAÇÃO DO PERCENTUAL DE ALCANCE

Criar gráfico de distribuição dos indicadores segundo o:

Percentual de alcance da meta

Exemplo:

0–49,99%

50–69,99%

70–89,99%

90–99,99%

100% ou mais

33. TABELA GERENCIAL PRINCIPAL

Criar tabela contendo:

Código

Indicador

Eixo

Diretriz

Objetivo

Área responsável

Meta anual

Resultado atual

Polaridade

Percentual de alcance

Status

Resultado anterior

Variação

Tendência

Apurado

Exibir status como:

“Bom — 78,4% da meta”

Permitir:

busca

ordenação

paginação

filtros

exportação

34. PÁGINA INDIVIDUAL DO INDICADOR

Ao clicar em qualquer indicador, abrir página exclusiva.

Mostrar no cabeçalho:

Código

Nome

Eixo

Perspectiva

Diretriz

Objetivo

Área responsável

Periodicidade

Acumulativo

Polaridade

35. CARDS DO INDICADOR

Exibir:

RESULTADO ATUAL

META ANUAL

% DE ALCANCE DA META

STATUS

RESULTADO ANTERIOR

VARIAÇÃO

TENDÊNCIA

Exemplo:

Resultado atual

74,86%

Meta anual

70%

Percentual de alcance

106,94%

Status

Ótimo — 106,94% da meta

36. SÉRIE HISTÓRICA

Mostrar tabela:

Ano

Quadrimestre

Resultado

Meta

% de alcance

Status

Criar também gráfico de linha.

Exemplo:

2024 Q1

2024 Q2

2024 Q3

2025 Q1

2025 Q2

2025 Q3

2026 Q1

etc.

37. META NO GRÁFICO HISTÓRICO

Quando tecnicamente possível, adicionar uma linha de referência representando:

Meta anual

Isso permitirá observar visualmente a distância entre resultado e meta.

38. HISTÓRICO DO STATUS

Mostrar:

2025 Q1 → Médio — 63%

2025 Q2 → Bom — 79%

2025 Q3 → Bom — 84%

2026 Q1 → Ótimo — 93%

Criar representação visual da evolução.

39. ANÁLISES ORIGINAIS DO SESPLAN

Criar seção:

ANÁLISES REGISTRADAS PELA ÁREA TÉCNICA

Organizar cronologicamente.

Exemplo:

1º quadrimestre de 2026

[texto integral da análise]

2º quadrimestre de 2026

[texto integral]

Preservar o conteúdo original.

40. ANÁLISE AUTOMÁTICA POR INTELIGÊNCIA ARTIFICIAL

Criar seção:

ANÁLISE AUTOMÁTICA DO INDICADOR

A IA deverá considerar:

código;

nome;

objetivo;

meta anual;

resultado atual;

percentual de alcance;

status;

polaridade;

resultado anterior;

tendência;

série histórica;

periodicidade;

análise registrada pela área técnica;

alterações metodológicas registradas;

área responsável.

41. ESTRUTURA DA ANÁLISE AUTOMÁTICA

Organizar em:

SÍNTESE DO RESULTADO

DESEMPENHO EM RELAÇÃO À META

EVOLUÇÃO EM RELAÇÃO AO PERÍODO ANTERIOR

TENDÊNCIA HISTÓRICA

PRINCIPAIS FATORES MENCIONADOS PELA ÁREA TÉCNICA

GARGALOS OU RISCOS IDENTIFICADOS

AÇÕES INFORMADAS PELA ÁREA

PONTOS PARA ACOMPANHAMENTO NO PRÓXIMO QUADRIMESTRE

42. FRASES DE DESEMPENHO

A IA poderá gerar frases como:

“O indicador alcançou 82,4% da meta anual e foi classificado como Bom.”

“O resultado representa 96,8% da meta, correspondendo ao status Ótimo.”

“Considerando a polaridade Menor - melhor, o resultado observado encontra-se abaixo do limite definido como meta e foi classificado como Ótimo.”

“Apesar da melhora em relação ao quadrimestre anterior, o indicador alcançou 64,7% da meta e permanece classificado como Médio.”

43. SEPARAÇÃO ENTRE FATO E INTERPRETAÇÃO

A IA deve separar claramente:

DADOS OBJETIVOS

INFORMAÇÕES RELATADAS PELA ÁREA TÉCNICA

INTERPRETAÇÃO AUTOMÁTICA

Nunca apresentar uma inferência como se estivesse presente no relatório original.

44. NÃO INVENTAR CAUSAS

Se a análise original não explicar o motivo do resultado, escrever:

“A análise registrada pela área técnica não informa os fatores associados ao resultado.”

Não inventar:

causas;

ações;

problemas;

resultados futuros.

45. ALTERAÇÕES METODOLÓGICAS

A IA deverá procurar no texto expressões relacionadas a:

mudança metodológica;

alteração do cálculo;

mudança de denominador;

mudança de fonte;

nova metodologia;

revisão da ficha;

mudança de escopo.

Quando identificado, destacar:

ATENÇÃO À COMPARABILIDADE DA SÉRIE

“Houve alteração metodológica registrada para este indicador. A comparação direta com períodos anteriores deve ser realizada com cautela.”

46. QUALIDADE DOS DADOS

Criar página:

QUALIDADE DOS DADOS

Mostrar:

Indicadores sem resultado

Indicadores sem meta

Indicadores sem área responsável

Indicadores sem análise

Indicadores sem polaridade

Indicadores duplicados

Valores não reconhecidos

Possíveis alterações de nome

Alterações da meta anual

Alterações da polaridade

Alterações da periodicidade

Alterações da área responsável

Possíveis alterações metodológicas

47. COMPARAÇÃO DO CADASTRO

O principal identificador longitudinal deverá ser:

Código do indicador

Quando o mesmo código aparecer novamente, comparar:

Nome

Meta anual

Polaridade

Área responsável

Periodicidade

Objetivo

Unidade

Caso haja alteração, gerar alerta.

48. EXEMPLO DE ALERTA

“Foi identificada alteração na descrição do indicador SAIS145 entre os períodos.”

“Meta anual alterada de 65% para 70%.”

“Polaridade modificada.”

“Área responsável alterada.”

49. TELA DE IMPORTAÇÃO

Criar página:

IMPORTAR RELATÓRIO SESPLAN

Campos:

Arquivo PDF

Ano

Quadrimestre

Botão:

PROCESSAR RELATÓRIO

50. PROCESSAMENTO

Após processamento, mostrar:

Indicadores encontrados

Indicadores com resultado

Indicadores sem resultado

Possíveis inconsistências

Tempo de processamento

Não gravar imediatamente.

51. TELA DE CONFERÊNCIA

Exibir tabela com:

Código

Indicador

Eixo

Objetivo

Meta anual

Resultado

Polaridade

% de alcance

Status

Área responsável

Apurado

Permitir edição dos campos extraídos antes da confirmação.

52. VALIDAÇÃO VISUAL

Sinalizar:

Código não reconhecido

Meta ausente

Resultado não reconhecido

Polaridade ausente

Área vazia

Possível duplicidade

Formato numérico duvidoso

Alteração cadastral

53. BOTÕES DA CONFERÊNCIA

CONFIRMAR IMPORTAÇÃO

SALVAR RASCUNHO

CANCELAR

EXPORTAR PRÉVIA

54. PROCESSAMENTO DO PDF

Implementar extração robusta.

O relatório apresenta blocos repetitivos.

Um indicador normalmente começa após:

“Nome do indicador”

seguido do código e nome.

Exemplos de códigos podem possuir prefixos como:

SAIS

SVS

CRDF

SULOG

SUPLANS

SUAG

FHB

entre outros.

Não limitar o parser aos prefixos conhecidos.

Identificar genericamente o código antes do separador “ - ”.

55. DELIMITAÇÃO DO BLOCO DO INDICADOR

O bloco deverá terminar quando ocorrer:

novo “Nome do indicador”;

novo Objetivo;

nova Diretriz;

nova Perspectiva;

novo Eixo;

ou final do documento.

56. HERANÇA DA HIERARQUIA

O PDF não repete toda a estrutura antes de cada indicador.

Por isso, manter em memória o último:

Eixo

Perspectiva

Diretriz

Objetivo

Quando surgir novo indicador, associá-lo aos últimos valores válidos até que uma nova hierarquia seja encontrada.

57. EXTRAÇÃO DA ANÁLISE

O campo:

Análise do resultado

pode ter várias linhas e atravessar páginas.

Capturar integralmente o conteúdo.

Não truncar.

Remover apenas elementos que façam parte do layout, como:

Meta Parcial:

Status:

Resultado:

Registrado Por:

Não incorporar esses rótulos ao texto da análise.

58. RESPONSÁVEL PELO REGISTRO

Capturar:

Registrado Por

como campo textual.

Preservar nome conforme relatório.

59. TABELA DE IMPORTAÇÕES

Criar tabela:

importacoes_sesplan

Campos:

ID

Nome do arquivo

Ano

Quadrimestre

Data do upload

Data de processamento

Usuário

Indicadores encontrados

Indicadores apurados

Indicadores não apurados

Registros novos

Registros substituídos

Inconsistências

Status da importação

Observações

60. AUDITORIA

Registrar todas as alterações manuais após extração.

Manter:

Campo alterado

Valor extraído

Valor corrigido

Usuário

Data

Motivo, quando informado

61. NÃO APAGAR HISTÓRICO

Nunca excluir silenciosamente versões anteriores.

Caso um dado seja substituído, registrar histórico da alteração.

62. EXPORTAÇÃO

Permitir exportar:

Banco completo Excel

Banco completo CSV

Banco filtrado Excel

Banco filtrado CSV

Histórico de um indicador

Indicadores de um objetivo

Indicadores de uma diretriz

Indicadores de uma área responsável

Relatório gerencial do quadrimestre

63. ORDEM DAS COLUNAS NA EXPORTAÇÃO PRINCIPAL

Ano

Período

Mês de referência

Eixo código

Eixo

Perspectiva código

Perspectiva

Diretriz código

Diretriz

Objetivo

Código indicador

Indicador

Meta anual

Unidade

Monitoramento

Acumulativo

Polaridade

Área responsável

Resultado do período

Apurado no período

Percentual de alcance da meta

Status de desempenho

Resultado anterior

Variação absoluta

Variação percentual

Tendência

Registrado por

Análise do resultado

Meta anual original

Resultado original

64. ARQUITETURA

Utilizar preferencialmente:

Supabase

PostgreSQL

Autenticação Supabase

Storage para PDFs

Banco relacional persistente

Não utilizar apenas localStorage.

65. TABELAS SUGERIDAS

indicadores_pds_resultados

importacoes_sesplan

usuarios

logs_importacao

alteracoes_registros

inconsistencias

analises_ia

66. AUTENTICAÇÃO

Criar perfis:

ADMINISTRADOR

ANALISTA

VISUALIZADOR

Administrador:

importar

editar

confirmar

substituir

excluir

gerenciar usuários

Analista:

importar

revisar

confirmar

consultar

exportar

Visualizador:

consultar

filtrar

exportar quando autorizado

67. MENU PRINCIPAL

Visão Geral

Importar SESPLAN

Indicadores

Objetivos Estratégicos

Diretrizes

Série Histórica

Análises

Qualidade dos Dados

Importações

Exportar Dados

Configurações

68. DESIGN

Criar interface institucional, moderna e limpa.

Características:

fundo claro;

cards brancos;

tons de azul como cor institucional predominante;

cinza neutro;

boa hierarquia de informação;

espaçamento adequado;

tipografia limpa;

visualização executiva.

Evitar excesso de cores.

69. CORES DO STATUS

Utilizar convenção visual consistente.

Ótimo → verde

Bom → azul ou verde-claro

Médio → amarelo/âmbar

Insuficiente → vermelho

Não apurado → cinza

Não calculável → cinza ou roxo neutro

Entretanto, não depender apenas da cor.

Sempre mostrar o texto.

70. EXEMPLO VISUAL

Em vez de apenas:

BOM

mostrar:

BOM

82,4% da meta

Ou:

Bom — 82,4% da meta

71. KPI BOM + ÓTIMO

Na Visão Geral, destacar fortemente:

DESEMPENHO SATISFATÓRIO

Bom + Ótimo

Exemplo:

77,4%

48 de 62 indicadores apurados

Permitir comparar esse KPI entre quadrimestres.

Exemplo:

2025 Q3 → 70,8%

2026 Q1 → 77,4%

Variação:

+6,6 pontos percentuais

72. EVOLUÇÃO GLOBAL

Criar gráfico mostrando ao longo do tempo:

% Ótimo

% Bom + Ótimo

% Médio

% Insuficiente

% Não apurado

Isso deverá permitir acompanhar se o desempenho global do PDS está melhorando.

73. COMPARAÇÃO ENTRE QUADRIMESTRES

Criar página ou seção para comparar dois períodos.

Exemplo:

2025 Q3

versus

2026 Q1

Mostrar:

Total apurado

% Bom + Ótimo

% Ótimo

% Insuficiente

Número de indicadores que melhoraram

Número que pioraram

Número estáveis

Novos indicadores

Indicadores sem apuração

74. ANÁLISE GERENCIAL AUTOMÁTICA DO QUADRIMESTRE

Criar uma análise por IA para o conjunto dos indicadores.

Estruturar:

VISÃO GERAL

DESEMPENHO GLOBAL

DESTAQUES POSITIVOS

INDICADORES QUE MERECEM ATENÇÃO

ÁREAS COM MAIOR CONCENTRAÇÃO DE RESULTADOS INSUFICIENTES OU MÉDIOS

PRINCIPAIS GARGALOS MENCIONADOS NAS ANÁLISES TÉCNICAS

EVOLUÇÃO EM RELAÇÃO AO QUADRIMESTRE ANTERIOR

PONTOS PRIORITÁRIOS PARA O PRÓXIMO MONITORAMENTO

75. REGRA PARA A ANÁLISE GLOBAL

A IA não deverá avaliar apenas quantidade absoluta.

Deverá considerar:

polaridade;

percentual de alcance;

status;

variação histórica;

quantidade de indicadores por área;

periodicidade;

existência de dados não apurados.

Evitar conclusões baseadas em amostras muito pequenas.

76. RELATÓRIO GERENCIAL

Permitir gerar automaticamente relatório com:

Capa

Período

Resumo executivo

Indicadores apurados

Distribuição por status

% Bom + Ótimo

Análise por Eixo

Análise por Diretriz

Principais evoluções

Principais pioras

Indicadores não apurados

Análise automatizada

Tabela completa

77. REGRAS DE CONFIABILIDADE

Nunca:

inventar resultado;

transformar campo vazio em zero;

atribuir causas não mencionadas;

alterar análise original;

sobrescrever histórico sem registro;

considerar indicador não apurado como insuficiente;

ignorar polaridade no cálculo.

78. SEPARAÇÃO ENTRE DADOS

Identificar no banco e na interface três grupos:

DADOS EXTRAÍDOS DO SESPLAN

DADOS CALCULADOS PELO SISTEMA

ANÁLISES GERADAS POR IA

Essa separação deverá ficar evidente.

79. MVP

Desenvolver inicialmente:

autenticação;

banco de dados;

upload do PDF;

processamento;

parser dos indicadores;

conferência;

gravação;

cálculo do % da meta;

cálculo do status;

dashboard;

tabela gerencial;

página individual;

série histórica;

exportação Excel;

análise automática por IA.

80. CRITÉRIOS DE ACEITE DO MVP

O MVP estará funcional quando permitir:

Subir um PDF do SESPLAN.

Selecionar ano e quadrimestre.

Extrair automaticamente os indicadores.

Reconhecer a hierarquia do PDS.

Extrair meta e resultado.

Preservar análise textual.

Permitir revisão.

Salvar os dados.

Calcular percentual de alcance.

Calcular status respeitando a polaridade.

Gerar dashboard.

Mostrar % Bom + Ótimo.

Abrir página individual.

Subir novo quadrimestre.

Relacionar resultados pelo Código do indicador.

Construir série histórica.

Comparar períodos.

Gerar análise automática.

Exportar banco consolidado em Excel.

81. DESENVOLVIMENTO EM ETAPAS

Não tentar implementar toda a aplicação em um único passo.

Executar nesta ordem:

FASE 1

Arquitetura

Banco de dados

Autenticação

Menu

Layout principal

FASE 2

Upload

Leitura do PDF

Extração

Parser

Tela de conferência

FASE 3

Gravação

Validação

Cálculos

Status

Percentual de alcance

FASE 4

Dashboard

Filtros

Gráficos

Tabela gerencial

KPI Bom + Ótimo

FASE 5

Página individual

Série histórica

Comparação entre períodos

FASE 6

IA

Análise individual

Análise global

Qualidade dos dados

FASE 7

Exportações

Auditoria

Relatórios gerenciais

82. DADOS DE TESTE

Durante o desenvolvimento, não preencher a aplicação final com dados fictícios.

Criar estrutura preparada para importar o PDF real.

Caso dados simulados sejam necessários apenas para testar componentes de interface, mantê-los claramente identificados como DEMONSTRAÇÃO e removê-los antes da versão operacional.

83. PREPARAÇÃO PARA ANOS FUTUROS

Não fixar regras de negócio exclusivamente em 2026.

A aplicação deve aceitar:

2024

2025

2026

2027

e anos futuros.

O ciclo do PDS também deve ser configurável futuramente.

84. OBJETIVO FINAL

O resultado deverá ser uma plataforma institucional de monitoramento que transforme automaticamente os relatórios do SESPLAN em informação gerencial.

O usuário deverá conseguir sair de um PDF quadrimestral para:

BANCO ESTRUTURADO

DASHBOARD

SÉRIE HISTÓRICA

STATUS DE DESEMPENHO

ANÁLISE AUTOMÁTICA

RELATÓRIO GERENCIAL

sem necessidade de reconstruir manualmente a base a cada quadrimestre.

A aplicação deverá funcionar como um instrumento permanente de monitoramento do Plano Distrital de Saúde da SES/DF.

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://sismonitora.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/420d8d27-a840-4ac9-a525-810997f4b04d).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
