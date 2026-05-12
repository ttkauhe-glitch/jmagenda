import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# ==========================================
# 1. SEGURANÇA E CONFIGURAÇÃO DA IA
# ==========================================
# Lendo a chave que você salvou com segurança no "cofre" (Secrets) do Streamlit.
try:
    CHAVE_API = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("ERRO: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.info("Por favor, adicione sua chave no painel de controle do Streamlit em Settings > Secrets.")
    st.stop() # Para a execução do app aqui se não houver chave.

genai.configure(api_key=CHAVE_API)
# Usando o modelo flash que é rápido e eficiente para leitura de imagem
model = genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 2. DESIGN DA INTERFACE (STREAMLIT)
# ==========================================
st.set_page_config(
    page_title="Agente AKAUT - Agenda",
    page_icon="📅",
    layout="centered" # Centraliza o conteúdo, ideal para celular
)

# Estilização básica para o título ficar mais bonito
st.markdown("""
    <style>
    .title-text {
        text-align: center;
        color: #2e7d32; /* Um verde mais escuro para o título */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title-text">📅 Extrator de Agenda Semanal</h1>', unsafe_allow_html=True)
st.write("Tire um print da sua agenda e envie aqui. A IA vai organizá-la em um PDF elegante para você baixar e compartilhar.")

# Componente de upload - No celular ele permite abrir a Câmera ou Galeria
arquivo_imagem = st.file_uploader("Selecione o print da agenda", type=['png', 'jpg', 'jpeg'])

# ==========================================
# 3. FUNÇÃO PARA GERAR O PDF ELEGANTE
# ==========================================
def criar_pdf(eventos_texto):
    pdf = FPDF()
    pdf.add_page()
    
    # Configurações de fonte (Arial é segura e limpa)
    pdf.set_font("Arial", size=11)
    
    # --- Cabeçalho do PDF ---
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 0, 0) # Preto
    pdf.cell(0, 15, "MINHA AGENDA SEMANAL", ln=True, align='C')
    
    # Linha decorativa verde abaixo do título
    pdf.set_draw_color(144, 238, 144) # Verde claro elegante
    pdf.set_line_width(1)
    pdf.line(10, 25, 200, 25)
    pdf.ln(10) # Espaço após o cabeçalho

    # --- Corpo da Agenda ---
    # Processa o texto da IA (que definimos para separar eventos por '---')
    eventos_lista = eventos_texto.strip().split('---')
    
    for evento in eventos_lista:
        linhas = [linha.strip() for linha in evento.strip().split('\n') if linha.strip()]
        
        # Só processa se tivermos as 4 informações solicitadas
        if len(linhas) >= 4:
            # Lista de rótulos na ordem exata solicitada
            rotulos = ["Horário", "Título", "Local", "Descrição"]
            # Pega as informações reais (removendo os rótulos que a IA pode ter colocado)
            infos = [linha.split(':', 1)[-1].strip() if ':' in linha else linha for linha in linhas[:4]]
            
            # Cria o "cartão" do evento (Tabela)
            for i in range(4):
                # Rótulo (Célula Verde com fonte preta negrito)
                pdf.set_fill_color(144, 238, 144) # Verde claro ('menta')
                pdf.set_text_color(0, 0, 0) # Preto
                pdf.set_font("Arial", style='B', size=10)
                pdf.set_draw_color(200, 200, 200) # Borda cinza clara
                pdf.cell(40, 9, f" {rotulos[i]}:", border=1, fill=True, align='L')
                
                # Informação (Célula Branca com fonte preta)
                pdf.set_fill_color(255, 255, 255) # Branco
                pdf.set_text_color(0, 0, 0) # Preto
                pdf.set_font("Arial", style='', size=10)
                # multi_cell permite que o texto quebre linha se for muito grande (ótimo para descrição)
                pdf.multi_cell(0, 9, f" {infos[i]}", border=1, fill=True, align='L')
            
            # Espaço elegante entre um evento e outro
            pdf.ln(6) 

    # --- Rodapé ---
    pdf.set_y(-25) # Vai para o final da página
    pdf.set_font("Arial", style='I', size=8)
    pdf.set_text_color(150, 150, 150) # Cinza claro
    pdf.cell(0, 10, "Gerado automaticamente pelo Agente AKAUT", align='C')

    # Retorna o PDF como dados binários
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ==========================================
# 4. LÓGICA PRINCIPAL DO APP
# ==========================================
if arquivo_imagem:
    # Mostra a imagem carregada para o usuário confirmar
    img = Image.open(arquivo_imagem)
    st.image(img, caption="Print carregado com sucesso", use_container_width=True)
    
    # O botão que aciona todo o processo
    if st.button("🚀 Gerar PDF da Minha Agenda", use_container_width=True):
        with st.spinner("A IA do Google está 'lendo' sua agenda... Aguarde."):
            try:
                # --- Prompt Mestre para o Gemini ---
                # Definimos a ordem exata e o formato de saída (JSON ou Markdown limpo)
                prompt_mestre = """
                Analise esta imagem de uma agenda semanal.
                Identifique e extraia todos os eventos, organizando-os estritamente nesta ordem:
                1. Horário
                2. Título do evento
                3. Local (Se não houver, escreva 'Não informado')
                4. Descrição (Se não houver, escreva 'Não informado')
                Organize cada evento em 4 linhas, uma para cada item acima.
                Mantenha a resposta limpa e direta. Separe cada evento por três hífens: ---
                """
                
                response = model.generate_content([prompt_mestre, img])
                texto_extraido = response.text
                
                # Para depuração (mostra o que a IA leu na tela - pode ser removido depois)
                # st.text_area("Texto extraído pela IA:", value=texto_extraido, height=150)
                
                # --- Geração do PDF ---
                pdf_bytes = criar_pdf(texto_extraido)
                
                # --- Sucesso e Botão de Download ---
                st.balloons() # Efeito visual de festa!
                st.success("Tudo pronto! Seu PDF foi gerado com o layout solicitado.")
                
                # No celular, isso abre as opções nativas de compartilhamento
                st.download_button(
                    label="📥 Baixar / Compartilhar PDF",
                    data=pdf_bytes,
                    file_name="agenda_semanal_elegante.pdf",
                    mime="application/pdf",
                    use_container_width=True # Botão grande no celular
                )
                
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")
                st.info("Isso pode acontecer se a imagem estiver muito ilegível ou se a API estiver ocupada. Tente novamente.")

# ==========================================
# 5. INSTRUÇÕES PARA O INICIANTE (Sidebar)
# ==========================================
st.sidebar.header("Como usar?")
st.sidebar.markdown("""
1.  Abra a agenda no site/app original.
2.  Tire um **Print** da tela.
3.  Volte aqui e clique em **Browse files**.
4.  Selecione o print.
5.  Clique em **Gerar PDF**.
6.  Baixe e compartilhe o arquivo!
""")
st.sidebar.info("Este app é responsivo. Salve o link na tela inicial do seu celular para usar como um aplicativo real.")
