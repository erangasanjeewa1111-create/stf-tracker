import streamlit as st
import hydralit as hy
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import io
import datetime

# --- CONFIGURATIONS ---
FOLDER_ID = "1SfHyrJmMSNQL7saTN_XH-bo6umc5y69b"
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

# --- Auth Function (Cloud Version) ---
def get_credentials():
    # කෙලින්ම Streamlit Cloud එකේ Secrets වලින් යතුර ගන්නවා
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return creds
    else:
        st.error("Secrets not found! Please configure Streamlit Secrets.")
        return None

# --- App Setup ---
app = hy.HydraApp(
    title='STF Ops Tracker',
    favicon="👮‍♂️",
    hide_streamlit_markers=True,
    use_navbar=True, 
    navbar_sticky=True,
    navbar_theme={'txc_inactive': '#FFFFFF','menu_background':'#111c2d','txc_active':'#4CAF50','option_active':'white'},
)

# --- FULL Technician List ---
TECHS = [
    "W.M.S.WICKRAMA BANDARA (72264)", "L.P.L.K.JAYALATH (73304)", "P.G.C.P.KUMARA (72355)",
    "U.A.N. PRIYALAL (74431)", "W.K.NANDASIRI (74240)", "W.R.N.MADUSANKA (74352)",
    "J.C.KODITHUWAKKU (10895)", "R.W.M.C.AJITH (12809)", "G.R.GAMAGE (13434)",
    "S.K. UDAWATTHA (13780)", "H.W.C.LOLITHA (33703)", "D.R.B.R. KARUNATHILAKA (40360)",
    "M.G.H.P.RAJAPAKSHA (53412)", "R.M.G.RATHNAYAKA (53443)", "H.M.J.D.BANDARA (53709)",
    "B.A.S.PUSHPA KUMARA (53712)", "M.P.H.L.RATHNAYAKA (53720)", "T.D.N.KUMARA (53721)",
    "T.A.N.S. RANATHILAKA (53764)", "M.T.N.SAMARATUNGA (53819)", "H.R.S. FERNANDO (53774)",
    "W.G.G.C.DAYANANDA (66025)", "G.R.M.PREMALAL (66977)", "T.R.M.HAYASIRI (69270)",
    "H.M.M.D.HERATH (69285)", "M.H.E.S.MAPA (70251)", "P.V.U.B.KARUNATHILAKA (70924)",
    "P.K.S.SUBASINGHA (74722)", "M.M.S.A.MUHANDIRAM (76073)", "K.C.LAKMAL (26313)",
    "D.M. ANANDA PREMATHILAKA (39663)", "S.T.HEWAGE (10117)", "P.L.J.P.GUNAWARDANA (75388)",
    "M.D.A.S.MANAWASINGHE (75886)", "G.W.D.P.CHANDIKA (77662)", "W.P.M.P. SRI WICKRAMA (78538)",
    "N.I.KUMARAWADU (78570)", "U.HETTIWATHTHA (78890)", "P.M.G.D.SUBASINGHE (79023)",
    "W.A.K.M.CHATHURANGA (79285)", "N.G.N.P.K.NAWAGAMUWA (79372)", "W.P.N. CHATHURANGA (79418)",
    "P.K.N.PUSHPA KUMARA (81408)", "M.P.R.CHATHURANGA (81458)", "W.S.K.WALPOLA (81559)",
    "D.L.N.WATHTHASINGHE (81918)", "D.M.J.S.BANDARA (82787)", "G.D.S.WEERARATNE (82828)",
    "P.G.W.PIYARATHNA (83009)", "K.N.L.GUNASEKARA (83047)", "D.M.S.S.DASANAYAKA (85532)",
    "E.K.K.SUJEEWA (83598)", "A.D.C.M.JAYARATHNE (84114)", "M.H.C.PRASANGA (84545)",
    "A.N.K.WITHANA (85113)", "P.K.H.MADURANGA (85706)", "U.J.RATHNAYAKA (86808)",
    "I.C.P.PERERA (86831)", "K.G.N.LAKMAL (86867)", "R.M.L.PRIYANTHA (86939)",
    "K.M.E.W.K.ABEYRATHNE (86947)", "W.V.N.NANDASENA (87048)", "W.S.S.KUMARA (87706)",
    "W.M.R.WIJESUNDARA (90763)", "E.H.G.T.D.EKANAYAKA (94226)", "Other / වෙනත් අය"
]

# =========================================
# 🏠 DASHBOARD
# =========================================
@app.addapp(title='Dashboard', icon="fa fa-tachometer")
def home():
    try:
        creds = get_credentials()
        if not creds: return
        gc = gspread.authorize(creds)
        sheet = gc.open("STF_Tech_Tracker").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame()

    st.markdown("## 📊 Situation Report")
    st.markdown("---")

    if not df.empty:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        today = pd.Timestamp.now().normalize()
        
        # Metrics
        if 'Date' in df.columns:
            today_data = df[df['Date'] == today]
            today_count = len(today_data)
            active_locs = len(today_data['Location'].unique()) if 'Location' in df.columns else 0
        else:
            today_count = 0
            active_locs = 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.info(f"Today Jobs: **{today_count}**")
        with c2:
            st.success(f"Today Locations: **{active_locs}**")
        with c3:
            st.warning(f"Total History: **{len(df)}**")
        with c4:
            st.error(f"Last Update: **{datetime.datetime.now().strftime('%H:%M')}**")

        st.markdown("### 📅 Weekly Progress")
        col_chart, col_recent = st.columns([2, 1])
        
        with col_chart:
            if 'Date' in df.columns and 'Location' in df.columns:
                seven_days_ago = today - pd.Timedelta(days=7)
                weekly_data = df[df['Date'] >= seven_days_ago]
                if not weekly_data.empty:
                    st.bar_chart(weekly_data['Location'].value_counts())
                else:
                    st.info("No recent data.")

        with col_recent:
            st.markdown("##### 🕒 Recent Updates")
            if not df.empty:
                cols_to_show = [c for c in ['Location', 'Progress'] if c in df.columns]
                if cols_to_show:
                    recent = df.tail(5)[cols_to_show]
                    st.dataframe(
                        recent,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Progress": st.column_config.ProgressColumn(
                                "Status", format="%d%%", min_value=0, max_value=100
                            ),
                        }
                    )
    else:
        st.error("No Data Found! Check Sheet Headers.")

# =========================================
# 📝 ENTRY MODE
# =========================================
@app.addapp(title='Entry', icon="fa fa-plus-circle")
def entry():
    st.markdown("## 📝 Mission Entry Log")
    creds = get_credentials()
    if not creds: return
    
    mode = st.radio("Select Mode:", ["🆕 Start New Job", "🔄 Update Ongoing Job"], horizontal=True)
    st.markdown("---")
    
    selected_date = datetime.date.today()
    selected_tech = ""
    location = ""
    team_str = ""
    task = ""
    progress = 0
    
    with st.container():
        with st.form("tech_form", clear_on_submit=True):
            
            if mode == "🔄 Update Ongoing Job":
                try:
                    gc = gspread.authorize(creds)
                    sheet = gc.open("STF_Tech_Tracker").sheet1
                    data = sheet.get_all_records()
                    df = pd.DataFrame(data)
                    
                    if not df.empty and 'Location' in df.columns and 'Task' in df.columns:
                        df['Job_Label'] = df['Location'] + " | " + df['Task'].astype(str).str[:30] + "..."
                        unique_jobs = df.drop_duplicates(subset=['Location', 'Task'], keep='last')
                        
                        job_selection = st.selectbox("Select Ongoing Job:", unique_jobs['Job_Label'].tolist())
                        job_data = df[df['Job_Label'] == job_selection].iloc[-1]
                        
                        selected_tech = job_data['Technician']
                        location = job_data['Location']
                        team_str = job_data['Team']
                        task = job_data['Task']
                        try:
                            prev_prog = int(job_data['Progress'])
                        except:
                            prev_prog = 0
                        
                        st.info(f"📍 Location: **{location}** | 👤 Lead: **{selected_tech}**")
                        st.text(f"🛠 Task: {task}")
                        
                        st.markdown("#### 👇 Update Details")
                        c_u1, c_u2 = st.columns(2)
                        with c_u1:
                            selected_date = st.date_input("Update Date", datetime.date.today())
                        with c_u2:
                            progress = st.slider("Work Progress (%)", 0, 100, prev_prog, step=10)
                        
                    else:
                        st.warning("No previous records found to update.")
                        
                except Exception as e:
                    st.error(f"Error fetching data: {e}")

            else:
                c1, c2 = st.columns(2)
                with c1:
                    selected_date = st.date_input("Date")
                    selected_tech = st.selectbox("Lead Technician", TECHS)
                    progress = st.slider("Work Progress (%)", 0, 100, 0, step=10)
                with c2:
                    location = st.text_input("Location (ස්ථානය)")
                    team_selection = st.multiselect("Support Team", TECHS)
                    team_str = ", ".join(team_selection)
                task = st.text_area("Task Description (කරපු කාර්යය)")

            uploaded_file = st.file_uploader("Evidence Photo 📷", type=["jpg", "png", "jpeg"])
            
            submitted = st.form_submit_button("🚀 Upload Update")
            
            if submitted:
                drive_service = build('drive', 'v3', credentials=creds)
                gc = gspread.authorize(creds)
                sheet = gc.open("STF_Tech_Tracker").sheet1
                
                image_link = "No Image"
                
                if uploaded_file:
                    with st.spinner('Uploading Photo...'):
                        try:
                            image = Image.open(uploaded_file).convert('RGB')
                            image.thumbnail((1024, 1024))
                            img_byte_arr = io.BytesIO()
                            image.save(img_byte_arr, format='JPEG', quality=65) 
                            img_byte_arr.seek(0)
                            
                            safe_tech_name = str(selected_tech).replace("/", "-") 
                            file_name = f"{selected_date}_{location}_{safe_tech_name}.jpg"
                            file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
                            media = MediaIoBaseUpload(img_byte_arr, mimetype='image/jpeg', resumable=True)
                            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
                            image_link = file.get('webViewLink')
                        except Exception as e:
                            st.error(f"Image Error: {e}")

                new_data = [str(selected_date), selected_tech, location, task, team_str, image_link, progress]
                
                try:
                    sheet.append_row(new_data)
                    st.success("✅ Update Added Successfully!")
                    st.code(f"*STF DAILY UPDATE*\n📅 {selected_date}\n📍 {location}\n📊 Progress: {progress}%\n🖼 {image_link}", language="text")
                except Exception as e:
                    st.error(f"Sheet Error: {e}")

# =========================================
# 📂 HISTORY
# =========================================
@app.addapp(title='Records', icon="fa fa-database")
def history():
    st.markdown("## 📂 Full Operations History")
    creds = get_credentials()
    if not creds: return
    
    gc = gspread.authorize(creds)
    sheet = gc.open("STF_Tech_Tracker").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    if not df.empty:
        if 'Date' in df.columns:
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "Progress": st.column_config.ProgressColumn(
                    "Status", format="%d%%", min_value=0, max_value=100
                ),
                "Image": st.column_config.LinkColumn("Evidence")
            }
        )

if __name__ == '__main__':
    app.run()