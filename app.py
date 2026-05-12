import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from PIL import Image
import io

# 1. Configuração da IA (Lendo a chave que você salvou no Secrets)
CHAVE_API = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Configuração da Página no Streamlit
st.set_page_config(page_title="Agente AKAUT", page_icon="📅")
st.title("📅 Extrator de Agenda")
st.write("Envie o print da sua agenda para gerar o PDF personalizado.")

# 3. Interface de Upload
arquivo_imagem = st.file_uploader("Selecione o print da agenda", type=['png', 'jpg', 'jpeg'])

def criar_pdf(dados_agenda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Título do Documento
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 15, "MINHA AGENDA SEMANAL", ln=True, align='C')
    pdf.ln(5)

    for evento in dados_agenda:
        # Lógica para garantir que temos os 4 campos
        linhas = evento.strip().split('\n')
        if len(linhas) >= 4:
            campos = ["Horário", "Título", "Local", "Descrição"]
            
            for i in range(4):
                # Rótulo (Verde com fonte preta)
                pdf.set_fill_color(144, 238, 144) # Verde claro elegante
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", style='B', size=10)
                pdf.cell(40, 8, f" {campos[i]}:", border=1, fill=True)
                
                # Informação (Branco com fonte preta)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_font("Arial", style='', size=10)
                pdf.cell(0, 8, f" {linhas[i].split(':', 1)[-1].strip()}", border=1, ln=True, fill=True)
            
            pdf.ln(5) # Espaço entre eventos

    return pdf.output(dest='S').encode('latin-1')

if arquivo_imagem:
    img = Image.open(arquivo_imagem)
    st.image(img, caption="Imagem carregada", use_container_width=True)
    
    if st.button("🚀 Gerar PDF Elegante"):
        with st.spinner("IA analisando a imagem..."):
            # Prompt específico para a ordem que você pediu
            prompt = """
            Analise esta imagem de agenda. Para cada evento, extraia exatamente:
            1. Horário
            2. Título do evento
            3. Local (se não houver, escreva 'Não informado')
            4. Descrição curta
            Organize cada evento em 4 linhas, uma para cada item acima.
            Separe cada evento por uma linha vazia.
            """
            
            response = model.generate_content([prompt, img])
            texto_ia = response.text
            
            # Divide o texto da IA em blocos de eventos
            eventos_lista = [e for e in texto_ia.split('\n\n') if len(e) > 10]
            
            try:
                pdf_bytes = criar_pdf(eventos_lista)
                st.success("PDF gerado com sucesso!")
                st.download_button(
                    label="📥 Baixar Agenda em PDF",
                    data=pdf_bytes,
                    file_name="agenda_semanal.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}. Tente novamente.")
