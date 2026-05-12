# ... (início do código permanece igual)

genai.configure(api_key=CHAVE_API)

# Mudamos para 'gemini-1.5-flash-latest' para garantir que o servidor encontre a versão certa
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# ... (restante do código permanece igual)
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# ==========================================
# 1. SEGURANÇA E CONFIGURAÇÃO DA IA
# ==========================================
try:
    CHAVE_API = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("ERRO: Chave 'GEMINI_API_KEY' não encontrada nos Secrets.")
    st.stop()

genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 2. DESIGN DA INTERFACE (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Agente AKAUT - VIP", page_icon="📅", layout="centered")

st.markdown("""
    <style>
    .title-text { text-align: center; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title-text">📅 Extrator de Agenda Pro</h1>', unsafe_allow_html=True)
st.write("Extraia horários, equipes e detalhes automaticamente para PDF.")

arquivo_imagem = st.file_uploader("Selecione o print da agenda", type=['png', 'jpg', 'jpeg'])

# ==========================================
# 3. FUNÇÃO PARA GERAR O PDF
# ==========================================
def criar_pdf(eventos_texto):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Cabeçalho
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 15, "RELATÓRIO DE AGENDA E EQUIPE", ln=True, align='C')
    pdf.set_draw_color(144, 238, 144)
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)

    eventos_lista = eventos_texto.strip().split('---')
    
    for evento in eventos_lista:
        linhas = [l.strip() for l in evento.strip().split('\n') if l.strip()]
        
        # Agora esperamos 5 campos: Horário, Título, Local, Equipe, Descrição
        if len(linhas) >= 5:
            rotulos = ["Horário", "Título", "Local", "Equipe", "Descrição"]
            # Limpa o texto vindo da IA
            infos = [l.split(':', 1)[-1].strip() if ':' in l else l for l in linhas[:5]]
            
            for i in range(5):
                # Rótulo Verde
                pdf.set_fill_color(144, 238, 144) 
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", style='B', size=9)
                pdf.set_draw_color(200, 200, 200)
                pdf.cell(35, 9, f" {rotulos[i]}:", border=1, fill=True)
                
                # Info Branca (com multi_cell para descrições longas)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_font("Arial", style='', size=9)
                pdf.multi_cell(0, 9, f" {infos[i]}", border=1, fill=True)
            
            pdf.ln(6) 

    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ==========================================
# 4. LÓGICA PRINCIPAL
# ==========================================
if arquivo_imagem:
    img = Image.open(arquivo_imagem)
    st.image(img, caption="Imagem carregada", use_container_width=True)
    
    if st.button("🚀 Gerar PDF Completo", use_container_width=True):
        with st.spinner("IA processando equipe e detalhes..."):
            try:
                # PROMPT ATUALIZADO: Foco em Equipe e Lógica de Sobras
                prompt_mestre = """
                Analise esta imagem de agenda. Extraia as informações e organize EXATAMENTE nestes 5 campos para cada evento:
                1. Horário: (ex: 14:00)
                2. Título: (nome da atividade)
                3. Local: (onde ocorrerá)
                4. Equipe: (Identifique nomes de pessoas, profissionais ou grupos mencionados)
                5. Descrição: (Inclua aqui todas as outras informações, detalhes técnicos, observações e QUALQUER dado que não se encaixou nos campos acima)

                Se algum campo (exceto descrição) não for encontrado, escreva 'Não informado'.
                Mantenha cada evento separado por: ---
                """
                
                response = model.generate_content([prompt_mestre, img])
                texto_extraido = response.text
                
                pdf_bytes = criar_pdf(texto_extraido)
                
                st.balloons()
                st.success("PDF gerado com sucesso!")
                
                st.download_button(
                    label="📥 Baixar PDF com Equipe",
                    data=pdf_bytes,
                    file_name="agenda_equipe_akaut.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Erro: {e}")

st.sidebar.info("O campo 'Equipe' agora busca automaticamente por nomes próprios no seu print.")
