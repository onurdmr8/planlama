import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, time
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from st_aggrid import AgGrid,GridOptionsBuilder,ColumnsAutoSizeMode
import streamlit.components.v1 as components
import locale
import time
import subprocess
import sqlite3


con3 = sqlite3.connect("recipe.db")
cursor = con3.cursor()
st.set_page_config(page_title="PLANLAMA")
st.sidebar.title("İŞ EMİRLERİ")
servers = st.sidebar.selectbox("Server", ["VSTRAPP", "TEST"])
menu_items = ["Ana sayfa", "Tüm Reçeteler","Yeni iş emri","İş Emri Düzenle",
              "Sezon dışı açık iş emirleri","Hatlardaki iş emirleri",
              "Marinasyon Reçete","Stok","Siparişler","Açık iş emirleri","Üretim stok hareketleri","Üretim Rapor"]
selected_option = st.sidebar.selectbox("Menu", menu_items)

yenisifre="2207"
editsifre="2207"
if servers == "TEST":
    server = "ONURPC"
    username = "ode"
    password = "mmm.123"
    database = "VSA2023"
elif servers == "VSTRAPP":
    server = "VSTRAPP"
    username = "DescomKasa"
    password = "D123456d*"
    database = "VSA2023"

connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC Driver 17 for SQL Server"
con = create_engine(connection_string)
if selected_option == "Ana sayfa":
    st.title("İŞ EMİRLERİ")
    st.write("Ana Sayfa")
    st.write("I?s? Emirleri")

    mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI ORDER BY TARIH DESC;"
    df = pd.read_sql(mainquery, con)
    def format_time(row):
        if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
            return '16:00-00:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
            return '08:00-16:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
            return '00:00-08:00'

    # 'ZAMAN' sütununu oluştur
    df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
    st.text_input("Arama", key="arama")  # Arama çubuğu

    def arama():
        if st.session_state.arama == "":
            return df
        else:
            return df[df['STOK_ADI'].str.contains(st.session_state.arama, case=False)]

    result = arama()

    sorted_result = result.sort_values(by='KAPALI', ascending=False)


    def highlight_rows(row):
        styles = [''] * len(row)
        if row['KAPALI'] == 'H':
            styles = ['background-color: #40128B'] * len(row)
        return styles

    results = sorted_result.style.apply(highlight_rows, axis=1)

    st.write(results, unsafe_allow_html=True)
elif selected_option=="Açık iş emirleri":
    st.title("İŞ EMİRLERİ")
    st.write("Açık I?s? Emirleri")

    mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE KAPALI = 'H';"
    df = pd.read_sql(mainquery, con)


    def format_time(row):
        if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
            return '16:00-00:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
            return '08:00-16:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
            return '00:00-08:00'

    # 'ZAMAN' sütununu oluştur
    df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))

    st.write(df, unsafe_allow_html=True)
elif selected_option=="Sezon dışı açık iş emirleri":
    st.title("İŞ EMİRLERİ")
    st.write("Ana Sayfa")
    st.write("I?s? Emirleri")


    mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '10' AND KAPALI = 'H';"
    df = pd.read_sql(mainquery, con)
    def format_time(row):
        if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
            return '16:00-00:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
            return '08:00-16:00'
        elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
            return '00:00-08:00'

    # 'ZAMAN' sütununu oluştur
    df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
    st.write(df)
elif selected_option == "Hatlardaki iş emirleri":
    hats = st.sidebar.selectbox("Hatlar",
                                    ["Reçel", "püre","ATÖLYE-2 YM MM", "ATÖLYE-1 YM MM", "seçme", "fırın", "yıkama", "IQF"])
    if selected_option=="Hatlardaki iş emirleri" and hats == "Reçel":
        st.title("Reçel")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '08' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        if df.empty:
            st.write("REÇEL HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            if vardiya:
                if vardiya=="Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="IQF":
        st.title("IQF")
        vardiya=st.selectbox("Vardiya",["Tüm gün","00:00-08:00","08:00-16:00","16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '06' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur


        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))


        if df.empty:
            st.write("IQF HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            if vardiya:
                if vardiya=="Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="püre":
        st.title("PÜRE")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '09' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("PÜRE HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            if vardiya:
                if vardiya=="Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="ATÖLYE-1 YM MM":
        st.title("ATÖLYE-1 YM MM")
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '10' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("ATÖLYE-1 YM MM HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            st.write(df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="seçme":
        st.title("SEÇME")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '03' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("SEÇME HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:

            if vardiya:
                if vardiya == "Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="fırın":
        st.title("FIRIN")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '05' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("FIRIN HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            if vardiya:
                if vardiya == "Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="yıkama":
        st.title("YIKAMA")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '20' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)
        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("YIKAMA HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
            if vardiya:
                if vardiya == "Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
    elif selected_option=="Hatlardaki iş emirleri" and hats=="ATÖLYE-2 YM MM":
        st.title("ATÖLYE-2")
        vardiya = st.selectbox("Vardiya", ["Tüm gün", "00:00-08:00", "08:00-16:00", "16:00-00:00"])
        mainquery = "SELECT ISEMRINO, TARIH, TBLISEMRI.STOK_KODU, (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU = TBLISEMRI.STOK_KODU) AS STOK_ADI, MIKTAR, KAPALI FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 2) = '07' AND KAPALI = 'H';"
        df = pd.read_sql(mainquery, con)


        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'


        # 'ZAMAN' sütununu oluştur
        df.insert(0, 'VARDİYA', df.apply(format_time, axis=1))
        if df.empty:
            st.write("ATÖLYE-2 HATTINDA ÜRETİM YAPILMAMAKTADIR")
        else:
           if vardiya:
                if vardiya == "Tüm gün":
                    filtered_df = df
                    st.dataframe(filtered_df)
                else:
                    filtered_df = df[df['VARDİYA'] == vardiya]
                    st.dataframe(filtered_df)
elif selected_option=="Yeni iş emri":
    sifre = st.sidebar.text_input("ŞİFRE", type="password")
    if sifre==yenisifre:
        st.title("Yeni iş emri")
        # İlk sütun
        col1, col2 = st.columns(2)
        # İlk sütun içeriği
        with col1:
            hattext = st.selectbox("Hattı seçiniz", ["ATÖLYE-2 YM MM","ATÖLYE-1 YM MM", "SEÇME", "FIRIN", "YIKAMA", "IQF", "REÇEL", "PÜRE"])
            vardiyatext = st.selectbox("Vardiya seçiniz", ["00:00-08:00", "08:00-16:00", "16:00-00:00"])

            def arama(aramatext):
                stokadiquery = """
                                   SELECT DISTINCT TBLSTSABIT.STOK_ADI
                                   FROM TBLSTSABIT
                                   INNER JOIN TBLSTOKURM ON TBLSTSABIT.STOK_KODU = TBLSTOKURM.MAMUL_KODU
                                   WHERE TBLSTSABIT.STOK_ADI LIKE ?;
                                   """
                # con nesnesi veritabanı bağlantınızı temsil eder
                dfad = pd.read_sql(stokadiquery, con, params=('%' + aramatext + '%',))
                return dfad

            aramatext = st.text_input("Ara")
            if aramatext:
                stok_adi_listesi = arama(aramatext)
            else:
                stok_adi_listesi=arama(aramatext)
            stokadi = st.selectbox("Stok adı seçiniz", stok_adi_listesi, index=0)
            stokkoduquery = "SELECT STOK_KODU FROM TBLSTSABIT WHERE STOK_ADI='" + stokadi + "'"
            dfkod = pd.read_sql(stokkoduquery, con)
            stoktext = st.selectbox("Stok kodu seçiniz", dfkod)
        # İkinci sütun içeriği
        with col2:
            miktar = st.text_input("Miktarı giriniz")
            depo_kodu = st.selectbox("Depo kodu", ["300", "400", "401", "402", "403"])
            tarihtext = st.date_input("Tarih seçiniz")
            projekodu = st.text_input("Proje kodu", "0")
            Kapali = st.selectbox("Kapalı", ["H", "E"])
        if hattext == "ATÖLYE-1 YM MM":
            hatt="10"
        elif hattext == "SEÇME":
            hatt="03"
        elif hattext == "FIRIN":
            hatt="05"
        elif hattext == "YIKAMA":
            hatt="20"
        elif hattext == "IQF":
            hatt="06"
        elif hattext == "REÇEL":
            hatt="08"
        elif hattext == "PÜRE":
            hatt="09"
        elif hattext == "ATÖLYE-2 YM MM":
            hatt="07"

        if vardiyatext == "00:00-08:00":
            vard="1"
        elif vardiyatext == "08:00-16:00":
            vard="2"
        elif vardiyatext == "16:00-00:00":
            vard="3"

        # Üçüncü sütun içeriği
        stok_kodu = stoktext

        tar=tarihtext
        # Tarih değerini parçalayarak gereken parçaları alın
        gun=str(tar.day).zfill(2)
        ay=str(tar.month).zfill(2)
        yil=str(tar.year)

        # Orta değerini hesaplama
        orta = str(gun) + str(ay)+str(yil[2:4])
        isno=str(str(hatt)+str(vard)+str(orta))
        isno_filled = isno.ljust(14, '0')
        konrolsira="SELECT MAX (ISEMRINO) FROM TBLISEMRI WHERE SUBSTRING(ISEMRINO, 1, 14)='" + isno_filled + "'"
        kotrolconn=pd.read_sql(konrolsira, con)
        bir=str(kotrolconn)

        if (bir)[-4:]=="None":
            iss=str(hatt)+str(vard)+str(orta)
            isem=iss.ljust(14, '0')
            isemrino=isem+"1"
            isemrinotext = st.text_input("İş emrini giriniz", isemrino)
            if len(isemrinotext) == 15:
                st.write("DOĞRU", unsafe_allow_html=True)
            else:
                st.write(isemrinotext)
        else:
            iki = ((bir)[-15:])
            dort = (iki)[-1:]
            bes = (dort)[-1:]
            isemrino1 = int(iki) + 1
            isemrino2 = str(isemrino1).zfill(15)
            isemrinotext = st.text_input("İş emrini giriniz", isemrino2)
            if len(isemrinotext) == 15:
                st.write("DOĞRU", unsafe_allow_html=False)

            else:
                st.write(isemrinotext)
                st.write("yanlış", unsafe_allow_html=True)

        noww = datetime.now()
        noww = noww.strftime("%Y-%m-%d %H:%M:%S")
        noww_str = noww
        tarstr = str(tarihtext)
        kaydet = st.button("İş Emrini Kaydet")
        def insert_work_order(con, isemrinotext, stok_kodu, miktar, tarihtext, Kapali, projekodu, depo_kodu, noww_str):

            kaydetquery = text("""
                INSERT INTO TBLISEMRI (
                    ISEMRINO, STOK_KODU, MIKTAR, TARIH, KAPALI, TESLIM_TARIHI, PROJE_KODU,
                    ONCELIK, DEPO_KODU, CIKIS_DEPO_KODU, KAYITYAPANKUL, KAYITTARIHI,
                    SIPKONT, TEPESIPKONT, ONAYTIPI, ONAYNUM, REWORK, ISEMRI_SIRA,
                    USK_STATUS, REZERVASYON_STATUS, SIRA_ONCELIK
                ) VALUES (
                    :isemrinotext, :stoktext, :miktar, :tarihtext, :Kapali, :tarihtext, :projekodu,
                    '0', :depo_kodu, :depo_kodu, 'ONUR', :noww_str, '0', '0', 'A', '0',
                    'H', '0', 'Y', 'Y', '0'
                )
            """)
            kaydet2query = text("""INSERT INTO TBLISEMRIEK (ISEMRI) VALUES (:isemrinotext);""")

            values = {
                "isemrinotext": isemrinotext,
                "stoktext": stok_kodu,
                "miktar": miktar,
                "tarihtext": tarstr,
                "Kapali": Kapali,
                "projekodu": projekodu,
                "depo_kodu": depo_kodu,
                "noww_str": noww_str
            }
            conn = con.connect()
            with conn as conn:
                conn.execute(kaydetquery, values)
                conn.execute(kaydet2query, values)
                conn.commit()

        if kaydet:
            insert_work_order(con, isemrinotext, stoktext, miktar, tarihtext, Kapali, projekodu, depo_kodu, noww_str)
            st.text("İŞ EMRİ KAYDEDİLDİ")
    else:
        st.write("SIFRE HATALI")
elif selected_option=="İş Emri Düzenle":
    sifre = st.sidebar.text_input("ŞİFRE", type="password")
    if sifre==editsifre:
        st.title("İş Emri Düzenle")
        isemriarama=st.text_input("Ara")
        aramaquery="""SELECT (SELECT STOK_ADI FROM TBLSTSABIT WHERE STOK_KODU=TBLISEMRI.STOK_KODU) AS STOK_ADI,ISEMRINO,KAPALI,TARIH, STOK_KODU, MIKTAR FROM TBLISEMRI WHERE ISEMRINO LIKE ? ORDER BY KAPALI DESC;"""
        dfara = pd.read_sql(aramaquery, con, params=('%' + isemriarama + '%',))

        def format_time(row):
            if len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '3':
                return '16:00-00:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '2':
                return '08:00-16:00'
            elif len(str(row['ISEMRINO'])) >= 3 and str(row['ISEMRINO'])[2] == '1':
                return '00:00-08:00'

        dfara.insert(0, 'VARDİYA', dfara.apply(format_time, axis=1))


        st.write(dfara, unsafe_allow_html=False)
        isemrino_text=st.write("İş Emri no:",dfara.iloc[0]['ISEMRINO'])
        stokadi_text=st.write("Stok Adı:",dfara.iloc[0]['STOK_ADI'])
        stokkodu_text=st.write("Stok Kodu:",dfara.iloc[0]['STOK_KODU'])
        miktar_text=st.write("Miktar:",format(dfara.iloc[0]['MIKTAR'],",.2f"))
        tarih_text=st.write("Tarih:",format(dfara.iloc[0]['TARIH'],"%d-%m-%Y"))
        vardiya_text=st.write("Vardiya:",dfara.iloc[0]['VARDİYA'])
        col1, col2,col3 = st.columns(3)
        with col1:
            kapali_select_slider=st.text_input("Kapalı",dfara.iloc[0]['KAPALI'])
        with col3:
            st.write(" ")
            st.write(" ")
            edit=st.button("Düzenle")
            noww = datetime.now()
            noww = noww.strftime("%Y-%m-%d %H:%M:%S")
            noww_str = noww
            def update_work_order(con, isemriarama, kapali_select_slider,noww_str):

                updatequery = text("""
                    UPDATE TBLISEMRI SET KAPALI=:Kapali, DUZELTMEYAPANKUL=:kullanıcı, DUZELTMETARIHI=:noww_str WHERE ISEMRINO=:isemrinotext""")
                values = {
                    "isemrinotext": isemriarama,
                    "Kapali": kapali_select_slider,
                    "noww_str": noww_str,
                    "kullanıcı": "ONUR"
                }

                conn = con.connect()
                with conn as conn:
                    conn.execute(updatequery, values)
                    conn.commit()

            if edit:
                if kapali_select_slider=="H" or kapali_select_slider=="E":
                    update_work_order(con, isemriarama, kapali_select_slider,noww_str)
                    st.write("İŞ EMRİ DÜZENLENDİ")
                else:
                    st.write("HATALI DEĞER GİRİLDİ !")
    else:
        st.write("SIFRE HATALI")
elif selected_option=="Stok":
    st.title("Stok Kontrolu?")
    aramastok = st.text_input("Ara")
    depo_kodlari = ['300', '400', '402', '401']
    stokquery = """
        SELECT
    SA.STOK_KODU,
    SA.STOK_ADI,
    SA.OLCU_BR1,
    COALESCE(
        SUM(CASE WHEN TH.DEPO_KODU = '300' THEN (CASE WHEN TH.STHAR_GCKOD = 'G' THEN TH.STHAR_GCMIK ELSE -TH.STHAR_GCMIK END) ELSE 0 END),
        0
    ) AS ÜRETİM_DEPO,
    COALESCE(
        SUM(CASE WHEN TH.DEPO_KODU = '400' THEN (CASE WHEN TH.STHAR_GCKOD = 'G' THEN TH.STHAR_GCMIK ELSE -TH.STHAR_GCMIK END) ELSE 0 END),
        0
    ) AS LOKAL_DEPO,
    COALESCE(
        SUM(CASE WHEN TH.DEPO_KODU = '401' THEN (CASE WHEN TH.STHAR_GCKOD = 'G' THEN TH.STHAR_GCMIK ELSE -TH.STHAR_GCMIK END) ELSE 0 END),
        0
    ) AS AMBALAJ_DEPO,
    COALESCE(
        SUM(CASE WHEN TH.DEPO_KODU = '402' THEN (CASE WHEN TH.STHAR_GCKOD = 'G' THEN TH.STHAR_GCMIK ELSE -TH.STHAR_GCMIK END) ELSE 0 END),
        0
    ) AS SEVKİYAT_DEPO,
    COALESCE(
        SUM(CASE WHEN TH.DEPO_KODU = '403' THEN (CASE WHEN TH.STHAR_GCKOD = 'G' THEN TH.STHAR_GCMIK ELSE -TH.STHAR_GCMIK END) ELSE 0 END),
        0
    ) AS DIŞ_DEPO
FROM TBLSTSABIT SA
LEFT JOIN TBLSTHAR TH ON SA.STOK_KODU = TH.STOK_KODU AND TH.DEPO_KODU IN ('300', '400', '401', '402', '403')
GROUP BY SA.STOK_KODU, SA.STOK_ADI, SA.OLCU_BR1
ORDER BY SA.STOK_KODU ASC;

    """

    dfstok = pd.read_sql(stokquery, con)

    dfarastok = dfstok[dfstok['STOK_ADI'].str.contains(aramastok, case=False)]
    # Görüntülemek istediğiniz sütunları seçin
    columns_to_show = ['STOK_KODU', 'STOK_ADI', 'OLCU_BR1', 'ÜRETİM_DEPO', 'LOKAL_DEPO', 'AMBALAJ_DEPO',
                       'SEVKİYAT_DEPO', 'DIŞ_DEPO']
    dfedit = dfarastok[columns_to_show]
    # "depo" sütunlarını tamsayıya çeviriyoruz
    depo_columns = ['ÜRETİM_DEPO', 'LOKAL_DEPO', 'AMBALAJ_DEPO', 'SEVKİYAT_DEPO', 'DIŞ_DEPO']

    for col in depo_columns:
        dfedit[col] = pd.to_numeric(dfedit[col], errors='coerce')

    def highlight_cells(val):
        if isinstance(val, (int, float)):
            if val < 0:
                return 'background-color: red; color: white'
        return ''


    st.dataframe(dfedit.style.applymap(highlight_cells, subset=columns_to_show))
elif selected_option=="Siparişler":
    st.title("Siparişler")
    sipquery = """SELECT
    T.FISNO,
    T.STOK_KODU,
    S.STOK_ADI,
    T.STHAR_GCMIK AS MIKTAR,
    T.STHAR_CARIKOD AS CARI_KOD,
    C.CARI_ISIM AS CARI_ADI,
    T.STHAR_TESTAR AS TESLIM_TARIHI
FROM
    TBLSIPATRA AS T
JOIN
    TBLSTSABIT AS S ON T.STOK_KODU = S.STOK_KODU
JOIN
    TBLCASABIT AS C ON T.STHAR_CARIKOD = C.CARI_KOD
WHERE
    NOT SUBSTRING(T.FISNO, 1, 1) = 'S' AND T.STHAR_FTIRSIP = '6' AND STHAR_HTUR = 'H' AND SUBSTRING(STHAR_CARIKOD, 1, 3) != '195'
    AND SUBSTRING(STHAR_CARIKOD, 1, 3) != '136'
ORDER BY
    T.FISNO;
"""

    df = pd.read_sql(sipquery, con)
    col1,col2=st.columns(2)
    with col1:
        siparay = st.text_input("Ürün Ara")
        testarara=st.date_input("Teslim Tarihi Seç")

    with col2:
        sipcarara=st.text_input("Cari Ara")
        st.write(" ")
        st.write(" ")
        check=st.checkbox("Tarih filtresi", value=False)

    if check==True:
        testarstr=str(testarara.strftime("%Y-%m-%d"))
        dfsipara = df[df['STOK_ADI'].str.contains(siparay, case=False)]
        dfcariara = dfsipara[dfsipara['CARI_ADI'].str.contains(sipcarara, case=False)]

        dftarara = df[df['TESLIM_TARIHI_STR'].str.contains(testarstr, case=False)]
        dftarara_no_date = dftarara.drop(columns=['TESLIM_TARIHI'])
        st.dataframe(dftarara_no_date, use_container_width=True)
    else:
        testarstr = str(testarara.strftime("%Y-%m-%d"))
        dfsipara = df[df['STOK_ADI'].str.contains(siparay, case=False)]
        dfcariara = dfsipara[dfsipara['CARI_ADI'].str.contains(sipcarara, case=False)]
        st.dataframe(dfcariara, use_container_width=True)
elif selected_option=="Marinasyon Reçete":


    st.title("Reçete")
    recipe_id = st.selectbox("Reçete", ["hb3", "hb2", "hb4", "hb17", "hb", "hb21", "hb9","paketleme"])
    production_amount = st.text_input("Üretim miktarı")
    stokadıara = st.text_input("Stok Adı Ara")

    def arama(stokadıara):
        stokadiquery = """
                       SELECT DISTINCT TBLSTSABIT.STOK_ADI
                       FROM TBLSTSABIT
                       INNER JOIN TBLSTOKURM ON TBLSTSABIT.STOK_KODU = TBLSTOKURM.MAMUL_KODU
                       WHERE TBLSTSABIT.STOK_ADI LIKE ? AND TBLSTSABIT.STOK_ADI LIKE ?;
                       """
        dfad = pd.read_sql(stokadiquery, con, params=('%' + stokadıara + '%','%'+recipe_id+'%',))
        return dfad

    stoklistesi = arama(stokadıara)
    urunid = st.selectbox("STOK ADI", stoklistesi)
    queryrec = "SELECT marinasyon,stokkodu,oran FROM recete WHERE marinasyon='"+str(recipe_id)+"'"

    result_df=pd.read_sql_query(queryrec,con3)
    result_df.dropna(inplace=True)
    # Üretim miktarını sayıya çevir
    try:
        production_amount = float(production_amount)
    except ValueError:
        production_amount = 1.0  # Default value

    result_df['oran']=result_df['oran'].str.replace(",",".").astype(float)
    result_df['miktar'] = (result_df['oran'] * production_amount)/100
    result_df.loc[result_df['stokkodu'] == 'ürün', urunid] = urunid
    stokadıquery = """
        SELECT STOK_KODU, STOK_ADI
        FROM TBLSTSABIT
    """
    # SQL sorgusunu çalıştır ve sonucu bir DataFrame'e yükle
    tblstabıt_df = pd.read_sql_query(stokadıquery, con)

    # Ana veri çerçevenizle (result_df) birleştirme işlemi
    result_df = result_df.merge(tblstabıt_df, left_on='stokkodu', right_on='STOK_KODU', how='left')
    result_df.loc[result_df['stokkodu'] == "ürün", 'STOK_ADI'] = urunid
    # Gereksiz sütunu düşürme
    result_df.drop(columns=['STOK_KODU'], inplace=True)

    # Sütun sırasını yeniden düzenleme
    result_df = result_df[['stokkodu', 'oran', 'STOK_ADI', 'miktar']]

    # Sonuçları görüntüleme


    st.write(result_df)
    col1, col2 ,col3= st.columns(3)
    with col3:
        summing=sum(result_df['miktar'])
        st.write(str(summing)+str(" kg"))
    with col1:
        st.write("AMBALAJ MALZEMELERİ")
        st.write("to be continue")
elif selected_option=="Tüm Reçeteler":
    st.title("TÜM REÇETE")
    stokadıara=st.text_input("Stok Adı Ara")
    selectadıquery = ("""
        SELECT MAMUL_KODU, (
            SELECT STOK_ADI FROM TBLSTSABIT
            WHERE TBLSTOKURM.MAMUL_KODU = TBLSTSABIT.STOK_KODU
        ) AS MAMUL_ADI
        FROM TBLSTOKURM
    """)
    dfrec = pd.read_sql(selectadıquery, con)
    #FİLTER BY stokadıara
    stokadlistesi = dfrec[dfrec['MAMUL_ADI'].str.contains(stokadıara, case=False)]
    stokadlistesik=stokadlistesi['MAMUL_ADI'].unique().tolist(

    )
    stokadı = st.selectbox("Stok Adı Ara", stokadlistesik)

    col1,col2 = st.columns(2)

    with col2:
        carpan=st.text_input("Çarpan",1)


    mamulkodu="""SELECT STOK_KODU FROM TBLSTSABIT WHERE STOK_ADI=?"""
    dfmamul = pd.read_sql(mamulkodu, con, params=(stokadı,))
    mamukodu = st.text_input("Mamul Kodu",dfmamul['STOK_KODU'].iloc[0])
    bacthmiktarquery="""SELECT batchmiktar FROM batch WHERE stokkodu=?"""
    dfbatchmiktar = pd.read_sql(bacthmiktarquery, con3, params=(str(mamukodu),))


    with col1:
        sdf="""SELECT stokkodu FROM batch WHERE stokkodu=? """
        sbf=con3.execute(sdf,(str(mamukodu),))


        try:
            batchmiktar = dfbatchmiktar['batchmiktar'].iloc[0]
            üretimmiktar = st.text_input("Üretim Miktarı", batchmiktar)
        except IndexError:
            üretimmiktar = st.text_input("Üretim Miktarı",1)

    if üretimmiktar == "" and carpan == 1:
        ürmiktar = 1
    elif üretimmiktar != "" and carpan != 1:
        ürmiktar = float(üretimmiktar) * float(carpan)
    elif üretimmiktar == None and carpan == 1:
        ürmiktar = " "
    else:
        ürmiktar = üretimmiktar

    querryreçete="""SELECT MAMUL_KODU,HAM_KODU,(SELECT STOK_ADI FROM TBLSTSABIT 
        WHERE TBLSTOKURM.HAM_KODU=TBLSTSABIT.STOK_KODU) AS STOK_ADI, 
        MIKTAR,OPR_BIL FROM TBLSTOKURM WHERE MAMUL_KODU=? AND (OPR_BIL='B' OR OPR_BIL='O')"""

    dfreçete = pd.read_sql(querryreçete, con, params=(mamukodu,))
    # Create a new column 'Üretim Miktarı Çarpımı'
    try:

        ürmiktar = float(ürmiktar)
    except ValueError:
        ürmiktar = 1



    dfreçete['GEREKEN'] = dfreçete['MIKTAR'] * float(ürmiktar)

    # Tüm HAM_KODU'ları alın
    ham_kodlari = dfreçete['HAM_KODU'].unique()

    # HAM_KODU'ları üzerinde dönün ve SQL sorgusunu bir kez çalıştırın
    for ham_kodu in ham_kodlari:
        stokdurumquery = """
        SELECT 
            STOK_KODU,
            SUM(
                CASE 
                    WHEN (DEPO_KODU = '401' OR DEPO_KODU = '400') AND STHAR_GCKOD = 'G' THEN STHAR_GCMIK
                    WHEN (DEPO_KODU = '401' OR DEPO_KODU = '400') AND STHAR_GCKOD <> 'G' THEN -STHAR_GCMIK
                    ELSE 0
                END
            ) AS AMB_DEPO
        FROM 
            TBLSTHAR
        WHERE
            STOK_KODU = ?
        GROUP BY 
            STOK_KODU
        """
        dısdepodurumquery = """
        SELECT 
            STOK_KODU,
            SUM(
                CASE 
                    WHEN DEPO_KODU = '403' AND STHAR_GCKOD = 'G' THEN STHAR_GCMIK
                    WHEN  DEPO_KODU = '403' AND STHAR_GCKOD <> 'G' THEN -STHAR_GCMIK
                    ELSE 0
                END
            ) AS DIS_DEPO
        FROM 
            TBLSTHAR
        WHERE
            STOK_KODU = ?
        GROUP BY 
            STOK_KODU
        """
        dfdısdepodurum = pd.read_sql(dısdepodurumquery, con, params=(ham_kodu,))

        # SQL sorgusunu çalıştırın ve sonucu alın
        dfstokdurum = pd.read_sql(stokdurumquery, con, params=(ham_kodu,))
        try:
            dfreçete.loc[dfreçete['HAM_KODU'] == ham_kodu, 'DIS_DEPO_STOK'] = dfdısdepodurum['DIS_DEPO'].values[0]
            dfreçete.loc[dfreçete['HAM_KODU'] == ham_kodu, 'STOK'] = dfstokdurum['AMB_DEPO'].values[0]
        except IndexError:
            dfreçete.loc[dfreçete['HAM_KODU'] == ham_kodu, 'DIS_DEPO_STOK'] = 0
            dfreçete.loc[dfreçete['HAM_KODU'] == ham_kodu, 'STOK'] = 0
    st.write(stokadı)
    st.write("BİLEŞENLER")
    dfreçete=dfreçete[['HAM_KODU','STOK_ADI','GEREKEN','MIKTAR','STOK','DIS_DEPO_STOK']]
    st.dataframe(dfreçete)
    st.write("ÇIKAN ÜRÜN")
    cıkanurunquery = """SELECT MAMUL_KODU,HAM_KODU,(SELECT STOK_ADI FROM TBLSTSABIT 
        WHERE TBLSTOKURM.HAM_KODU=TBLSTSABIT.STOK_KODU) AS STOK_ADI, 
        MIKTAR,OPR_BIL FROM TBLSTOKURM WHERE MAMUL_KODU=? AND OPR_BIL='Y' ORDER BY MAMUL_KODU DESC"""
    dfcıkanurun = pd.read_sql(cıkanurunquery, con, params=(mamukodu,))

    dfcıkanurun['ÇIKAN_ÜRÜN'] = dfcıkanurun['MIKTAR'] * float(ürmiktar)
    dfcıkanurun=dfcıkanurun[['MAMUL_KODU','STOK_ADI','MIKTAR','ÇIKAN_ÜRÜN']]
    st.dataframe(dfcıkanurun)
elif selected_option=="Üretim stok hareketleri":
    st.title("Üretim Stok Hareketleri")
    urmstokharquery="""SELECT
                        kayittarihi,
                        uretimid,
                        stokkodu,
                        (SELECT STOK_ADI FROM TBLSTSABIT WHERE TBLSTSABIT.STOK_KODU = dsc_uretimhareket.stokkodu) AS STOK_ADI,
                        giriscikis,
                        miktar,
                        serino,
                        girisserino,
                        kullanicikodu,
                        SUM(miktar) OVER (PARTITION BY kayittarihi) AS total_miktar
                    FROM
                        dsc_uretimhareket
                    ORDER BY
                        uretimid ASC, kayittarihi;"""
    dfstokhar = pd.read_sql(urmstokharquery, con)

    # Tarih sütununu belirli bir biçimde göster
    dfstokhar['formatted_kayittarihi'] = dfstokhar['kayittarihi'].dt.strftime('%d/%m/%Y')

    dfstokhar=dfstokhar[['formatted_kayittarihi','uretimid','stokkodu','STOK_ADI','giriscikis','miktar','serino','girisserino','kullanicikodu','total_miktar']]
    st.write(dfstokhar)
elif selected_option=="Üretim Rapor":
    st.title("Üretim Rapor")
    uretimyeriquery="""SELECT DISTINCT uretimyeri FROM dsc_rpr_uretimizleme"""
    dfuretimyeri = pd.read_sql(uretimyeriquery, con)
    uretimyeri=st.selectbox("Üretimyeri", dfuretimyeri['uretimyeri'].unique().tolist())
    urmraporquery="""SELECT surec, stokkodu, stokadi,serino,giriscikis,miktar,birim,uretimyeri FROM dsc_rpr_uretimizleme"""
    dfurmizleme = pd.read_sql(urmraporquery, con)
    #filter dfurmizleme with uretimyeri
    dfurmizleme = dfurmizleme[dfurmizleme['uretimyeri'] == uretimyeri]

    st.dataframe(dfurmizleme)