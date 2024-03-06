from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox, Progressbar
import pytube
from PIL import Image, ImageTk
from io import BytesIO
import requests
import urllib3
import threading
from tqdm import tqdm
import youtube_dl

# Desabilitar os avisos de solicitação HTTPS não verificada
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#--------------------------------------------------------------------------------------------------------------
# aqui Vamos criar O nosso Backend-----------------------------------------------------------------------------
# aqui Vamos Criar a Função thread para a Função mostrar e Baixar
def iniciar_definir_qualidade():
    # Esta é a função que será chamada pela UI. Ela inicia a thread.
    thread = threading.Thread(target=mostrar)
    thread = threading.Thread(target=baixar)
    thread.start()

# Aqui Vamos criar a Função Mostrar
def mostrar():
    url = Eurl.get()
    if not url:
        Limagem.config(text="Por favor, insira uma URL válida")
        return

    yt = pytube.YouTube(url)
    imagem_url = yt.thumbnail_url
    imagem_bytes = requests.get(imagem_url, verify=False).content
    imagem = Image.open(BytesIO(imagem_bytes)).resize((670, 390))
    imagem = ImageTk.PhotoImage(imagem)
    Limagem.config(image=imagem)
    Limagem.image = imagem

    if Mp3_var.get():
        audio_streams = yt.streams.filter(only_audio=True)
        available_audio_streams = [stream.abr for stream in audio_streams if stream.abr]
        Qualidade['values'] = available_audio_streams
    else:
        # Inclua todas as qualidades disponíveis, inclusive de streams adaptativos
        video_streams = yt.streams.filter(progressive=True).order_by('resolution')
        video_streams_adaptive = yt.streams.filter(adaptive=True).order_by('resolution')
        available_qualities = {stream.resolution for stream in video_streams} | {stream.resolution for stream in video_streams_adaptive}
        Qualidade['values'] = sorted(available_qualities, key=lambda x: int(x[:-1]), reverse=True)

# Aqui Vamos Criar a Função Baixar
def baixar():
    url = Eurl.get()
    qualidade = Qualidade.get()

    if not url or not qualidade:
        messagebox.showerror("Erro", "Por favor, insira uma URL válida e selecione uma qualidade")
        return

    yt = pytube.YouTube(url)

    try:
        if Mp3_var.get():  # Para MP3, a abordagem permanece a mesma
            stream = yt.streams.filter(only_audio=True, abr=qualidade).first()
            file_extension = 'mp3'  # Definindo a extensão do arquivo como MP3
        else:
            # Tenta encontrar um stream progressivo que contenha vídeo e áudio
            stream = yt.streams.filter(progressive=True, resolution=qualidade, file_extension='mp4').first()

            if not stream:
                # Se não encontrou um stream progressivo, tenta com streams adaptativos
                for s in yt.streams:
                    if s.includes_video_track and s.includes_audio_track:
                        stream = s
                        break
            file_extension = 'mp4'  # Definindo a extensão do arquivo como MP4

        if stream:
            file_path = filedialog.asksaveasfilename(defaultextension=f'.{file_extension}', filetypes=[(f"{file_extension.upper()} files", f"*.{file_extension}")])  # Atualizando tipos de arquivo
            Avanco.start()
            if file_path:
                stream.download(filename=file_path)
                messagebox.showinfo("Sucesso", "Download concluído com sucesso!")
                Avanco.stop()
            else:
                messagebox.showinfo("Cancelado", "Operação de download cancelada pelo usuário")
        else:
            messagebox.showerror("Erro", "Não foi possível encontrar o stream adequado para download.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao fazer o download: {e}")

# aqui vamos criar a Função Limpar
def limpar_campos():
    Eurl.delete(0, 'end')  # Limpar campo de entrada
    Mp3_var.set(False)      # Desmarcar botões de opção
    Limagem.config(image=None)  # Limpar a imagem
    Limagem.image = None  # Limpar a referência à imagem para libertar a memória
    Avanco.stop()           # Parar a barra de progresso
    Qualidade.set('Selecione a Qualidade')  # Definir a qualidade de volta ao texto padrão


# criar a Função fechar
def fechar_aplicacao():
    if messagebox.askyesno("Fechar Aplicação", "Deseja realmente fechar a aplicação? sim/Não"):
        Janela.destroy()

# Aqui vamos defenir as Cores a Usar 
Co1 = "#CADAD7"
co2 = "#0AAAFF"
co3 = "#FFFFFF"


#--------------------------------------------------------------------------------------------------------------
# aqui Vamos configurar a Nossa Janela ------------------------------------------------------------------------
Janela = Tk()
Janela.geometry('700x580+100+100')
Janela.resizable(False, False)
Janela.title('Youtube Downloader V3 DevJoel Portugal 2024 ©')
Janela.config(bg=Co1)
Janela.iconbitmap("C:\\Users\\HP\\Desktop\\Projectos\\DownloadV3\\icon.ico")
#--------------------------------------------------------------------------------------------------------------
# criar O fornte end ------------------------------------------------------------------------------------------
# criar a Entry para Introduzir a Url
Eurl = Entry(Janela, font=('arial 14 bold'), width=61)
Eurl.place(x=10, y=5)

# criar os radiobuton
Mp3_var = BooleanVar(value=False)
Mp3 = Radiobutton(Janela, text='Formato Mp3', font=('arial 15 bold'),background=Co1,variable=Mp3_var, value=True)
Mp3.place(x=10, y=40)
Mp4 = Radiobutton(Janela, text='Formato Mp4', font=('arial 15 bold'),background=Co1,variable=Mp3_var, value=False)
Mp4.place(x=185, y=40)
# criar a combobox
Qualidade = Combobox(Janela, font=('Arial 14'))
Qualidade.set('Selecione a Qualidade')
Qualidade.place(x=350, y=40)
# criar Os Botões ----------------------------------------------------------------
Bdownload = Button(Janela, text='Download', font=('arial 12 bold'), bg=co2,fg=co3,relief=RAISED, overrelief=RIDGE, command=baixar)
Bdownload.place(x=10, y=85)
BMostrar = Button(Janela, text='Mostrar', font=('arial 12 bold'), bg=co2,fg=co3,relief=RAISED, overrelief=RIDGE, command=mostrar)
BMostrar.place(x=110, y=85)
BLimpar = Button(Janela, text='Limpar dados', font=('arial 12 bold'), bg=co2,fg=co3,relief=RAISED, overrelief=RIDGE, command=limpar_campos)
BLimpar.place(x=195, y=85)
Bfechar = Button(Janela, text='Fechar Aplicação', font=('arial 12 bold'), bg=co2,fg=co3,relief=RAISED, overrelief=RIDGE, command=fechar_aplicacao)
Bfechar.place(x=325, y=85)
#----------------------------------------------------------------------------------
# criar um label para a Imagem ----------------------------------------------------
Limagem = Label(Janela, bg='White')
Limagem.place(x=10, y=130)
#----------------------------------------------------------------------------------
# criar Uma barra de progresso ----------------------------------------------------
Avanco = Progressbar(Janela, length=670)
Avanco.place(x=10, y=530)
#----------------------------------------------------------------------------------
# iniciar a Nossa Janela ----------------------------------------------------------
Janela.mainloop()
#----------------------------------------------------------------------------------
