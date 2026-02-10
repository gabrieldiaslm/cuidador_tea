# Cuidador TEA - Plataforma de Acompanhamento Longitudinal

O **Cuidador TEA** é uma aplicação web desenvolvida em Django, projetada para auxiliar pais, tutores e profissionais no monitoramento do desenvolvimento de crianças e adolescentes no Espectro Autista. A ferramenta transforma dados brutos em informações pedagógicas acionáveis através de uma interface intuitiva e visual.

---

## Funcionalidades Principais

* **Gestão de Perfis Múltiplos:** Um único cuidador (User) pode gerir diferentes dependentes (Profiles) de forma independente, ideal para famílias com mais de uma criança ou terapeutas.
* **Avaliações Especializadas:** Questionários estruturados por seções, com pontuação baseada na escala de 0 a 2 pontos por resposta.
* **Dashboard de Evolução:**
    * **Gráfico de Linha Interativo:** Visualização cronológica da pontuação total para identificação de progressos ou regressões ao longo do tempo.
    * **Barras de Progresso Coloridas:** Feedback visual imediato usando a lógica de semáforo:
        * **Crítico:** 0 a 3 pontos.
        * **Atenção:** 4 a 6 pontos.
        * **Consolidado:** 7 a 10 pontos.
* **Dicas Pedagógicas Contextuais:** Sistema de *feedback* que exibe orientações específicas para cada seção dependendo da nota obtida, organizadas em abas expansíveis.
* **Design Responsivo:** Interface otimizada para dispositivos móveis (*Mobile-First*).


