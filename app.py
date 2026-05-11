import streamlit as st

st.set_page_config(page_title="Agente de Agenda", layout="centered")

st.title("📅 Extrator de Agenda")
st.write("Tire um print da agenda e receba o PDF.")

# O uploader no celular permite abrir a câmera ou a galeria
arquivo_imagem = st.file_uploader("Envie o print da agenda", type=['png', 'jpg', 'jpeg'])

if arquivo_imagem:
    st.image(arquivo_imagem, caption="Agenda carregada", use_column_width=True)
    
    if st.button("✨ Gerar PDF Agora"):
        with st.spinner("IA processando e criando PDF..."):
            # Aqui entraria a lógica de enviar para a API que discutimos
            st.success("PDF pronto!")
            st.download_button("📥 Baixar PDF", data="conteudo_do_pdf", file_name="agenda_semanal.pdf")
