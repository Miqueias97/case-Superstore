import requests, json, time, locale
import streamlit as st
import pandas as pd


class ManipulacaoDados():

    def constroiDataFrame():

        url = 'https://script.google.com/macros/s/AKfycbyYo4sOwpw5E0PyOflHz95ly5q8H_8rrkIJip_Oxas76mZUwPe4w6vfIUndHgCpuRZjEA/exec'
        response = requests.get(url).json()['status']
        
        data = []
        for i in response: 
            try:
                i['Sales'] = float(i['Sales'])
            except:
                a = str(i['Sales']).split('.')
                valor = ''
                for index, num in enumerate(a):
                    if index == len(a) - 1:
                        valor += f'.{num}'
                    else:
                        valor += f'{num}'
                
                i['Sales'] = float(valor)

            i['Quantity'] = int(i['Quantity'])
            i['Discount'] = float(i['Discount'])
            
            try:
                i['Profit'] = float(i['Profit'])
            except:
                a = str(i['Profit']).split('.')
                valor = ''
                for index, num in enumerate(a):
                    if index == len(a) - 1:
                        valor += f'.{num}'
                    else:
                        valor += f'{num}'
                
                i['Profit'] = float(valor)
            
            data.append(i)
                        
        return pd.DataFrame.from_dict(data)
    
    def ResumoGeralCategorias(df):
        resumoSomas = df.pivot_table(index='Category', values=['Profit', 'Sales', 'Quantity'], aggfunc='sum')
        resumoCount = df.pivot_table(index='Category', values=['Order ID'], aggfunc='count')
        resumoCategory = pd.merge(resumoSomas, resumoCount, on='Category')
        resumoCategory['Profit'] = resumoCategory['Profit'].round(2)
        resumoCategory['Sales'] = resumoCategory['Sales'].round(2)
        
        return resumoCategory
        
        

class DataView():

    def tituloResumo():
        resumo = """
        Esta análise foi realizada utilizando o Superstore Dataset disponivel no Kaggle.
        """
        st.title("SuperStore")
        def stream_data():
            for word in resumo.split(" "):
                yield word + " "
                time.sleep(0.05)

        
        if st.button("Descrição da análise"):
            st.write_stream(stream_data)
            st.html('link: <a href="https://www.kaggle.com/datasets/vivek468/superstore-dataset-final">Superstore Dataset</a>')

    def cardsResumo(dfResumoCategorias):

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        salesSum = dfResumoCategorias['Sales'].sum()
        lucro = dfResumoCategorias['Profit'].sum()
        custo = salesSum - lucro
        margem = round((lucro / salesSum) * 100, 2)
        salesSum = locale.currency(salesSum, grouping=True, symbol=None)
        lucro = locale.currency(lucro, grouping=True, symbol=None)
        custo = locale.currency(custo, grouping=True, symbol=None)

        cabecalho = f'''
        <div style="display: flex; flex-direction: row;">
            <table style="font-size: 30px; padding: 0.5rem; text-align: center; width: 25rem; background-color: #07074E; color : white; border-radius: 0.5rem">
                <thead >
                    <th>Faturamento</th>
                </thead>
                <tbody >
                    <td style="background-color: white ;border: 0.1rem solid rgb(170, 170, 170); border-radius: 0.5rem; color : black">
                        R$ {salesSum}
                    </td>
                </tbody>
            </table>

            <div style="width : 1rem"></div>

            <table style="font-size: 30px; padding: 0.5rem; text-align: center; width: 25rem; background-color: #07074E; color : white; border-radius: 0.5rem">
                <thead >
                    <th>Custo</th>
                </thead>
                <tbody >
                    <td style="background-color: white ;border: 0.1rem solid rgb(170, 170, 170); border-radius: 0.5rem; color : black">
                        R$ {custo}
                    </td>
                </tbody>
            </table>
            
            <div style="width : 1rem"></div>

            <table style="font-size: 30px; padding: 0.5rem; text-align: center; width: 25rem; background-color: #07074E; color : white; border-radius: 0.5rem">
                <thead >
                    <th>Lucro</th>
                </thead>
                <tbody >
                    <td style="background-color: white ;border: 0.1rem solid rgb(170, 170, 170); border-radius: 0.5rem; color : black">
                        R$ {lucro}
                    </td>
                </tbody>
            </table>

            <div style="width : 1rem"></div>

            <table style="font-size: 30px; padding: 0.5rem; text-align: center; width: 25rem; background-color: #07074E; color : white; border-radius: 0.5rem">
                <thead >
                    <th>Margem</th>
                </thead>
                <tbody >
                    <td style="background-color: white ;border: 0.1rem solid rgb(170, 170, 170); border-radius: 0.5rem; color : black">
                        {margem} %
                    </td>
                </tbody>
            </table>
        </div>
        '''
        st.html(cabecalho)
        
    def barChart(dfResumoCategorias):

        lista = []
        for i in dfResumoCategorias.index:
            lista.append(i)
        
        dic = {'Categoria' : [], 'Margem' : [] }
        
        info = ['', 0]
        for a, i in enumerate(dfResumoCategorias):
            try:
                cat = dic['Categoria']
                cat.append(lista[a])
                dic['Categoria'] = cat
                lucro = dic['Margem']
                valor = dfResumoCategorias[dfResumoCategorias.index == lista[a]]['Profit'].sum() / dfResumoCategorias[dfResumoCategorias.index == lista[a]]['Sales'].sum()
                lucro.append(round((valor * 100), 2))
                if round((valor * 100), 2) > info[1]:
                    info = [lista[a], round((valor * 100), 2)]
                dic['Margem'] = lucro
            except:
                pass
        
        chart_data = pd.DataFrame(dic)

        text = f'A categoria que possui maior margem de lucro é {info[0]} com {info[1]}%.'
        st.write(text)
        st.html('<br>')

        st.bar_chart(
            chart_data,
            x="Categoria",
            y="Margem",
            y_label='Margem',
            x_label="Categoria",
            color=["#07074E"],  # Optional
        )
        
    def chartCity(df):
        col1, col2 = st.columns(2, vertical_alignment='center')
        with col1:
            st.html('<p>Top <strong>20</strong> estados com maior faturamento.</p>')
            faturamento = df.pivot_table(index='State', values=['Sales','Profit', 'Quantity'], aggfunc='sum')
            faturamento = faturamento.sort_values(by=['Profit'], ascending=False).head(20)
            faturamento = faturamento.reset_index()
            st.bar_chart(faturamento.sort_values('Profit'), x="State", y="Profit", color="#07074E", horizontal=True)

            
            

        with col2:
            dfMap = df[:] 
            df_final=dfMap[['lat','lon', 'State']]
            df_final['lat'] = pd.to_numeric(df_final['lat'])
            df_final['lon'] = pd.to_numeric(df_final['lon'])
            st.map(df_final, size="Profit")
        
    def subCategoria(df):
        df = df.pivot_table(index=['Region', 'Category'], values=['Sales','Profit', 'Quantity'], aggfunc='sum')
        df = df.reset_index()
        st.bar_chart(df, x="Region", y="Profit", color="Category", stack=False)

class Aplicativo():
    def __init__(self):
        st.set_page_config(layout="wide")
        st.html('<h5>Em desenvolvimento... 👷</h5>')
        st.html("<br>")
        DataView.tituloResumo()

        df = ManipulacaoDados.constroiDataFrame()
        resumoCategorias = ManipulacaoDados.ResumoGeralCategorias(df)
        DataView.cardsResumo(resumoCategorias)
        st.html("<br>")
        st.subheader("Profit por Categoria do Produto", divider="gray")
        st.html("<br>")
        DataView.barChart(resumoCategorias)

        st.subheader("Profit por Estado", divider="gray")
        st.html("<br>")

        DataView.chartCity(df)

        st.subheader("Profit Categoria x Região", divider="gray")
        st.html("<br>")

        DataView.subCategoria(df)
    

Aplicativo()
        

