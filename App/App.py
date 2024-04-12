#Packages
import streamlit as st
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
from streamlit_pdf_viewer import pdf_viewer
import mysql.connector

#Preprocessing

#data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    #bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


#reads pdf file and check extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    #close open handles
    converter.close()
    fake_file_handle.close()
    return text


# Session state setup
if 'state' not in st.session_state:
    st.session_state.state = None


#show uploaded file path to view pdf display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


#course recommendations(data already loaded from Courses.py)
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations**")
    c = 0
    rec_course = []
    #slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


#Database

#sql connector
connection = pymysql.connect(host='localhost',user='root',password='Shubham@2507',db='cv')
cursor = connection.cursor()


def establish_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cv',
            user='root',
            password='Shubham@2507'
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to retrieve pdf_name based on ID from database
def get_pdf_name_by_id(connection, id):
    cursor = connection.cursor()
    query = "SELECT pdf_name FROM user_data WHERE ID = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

# Function to display PDF for a given ID
def display_pdf_for_id():
    st.title("Display PDF for ID")

    # Establish database connection
    connection = establish_connection()

    if connection:
        # Input ID from the user
        id_input = st.text_input("Enter ID:")

        if st.button("Submit"):
            try:
                id_value = int(id_input)
            except ValueError:
                st.error("Please enter a valid ID.")
                return

            # Retrieve pdf_name corresponding to the ID
            pdf_name = get_pdf_name_by_id(connection, id_value)

            if pdf_name:
                st.success(f"Found PDF for ID: {id_value}")

                # Display the PDF below the submit button
                pdf_file_path = os.path.join('Uploaded_Resumes/', pdf_name)
                if os.path.exists(pdf_file_path):
                    show_pdf(pdf_file_path)
                else:
                    st.error(f"PDF file '{pdf_name}' not found.")
            else:
                st.warning(f"No PDF found for ID: {id_value}")

        connection.close()

# Function to show PDF using base64 encoding
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def insert_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country, act_name, act_mail, act_mob, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "INSERT INTO " + DB_table_name + " VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    #check if email is provided, insert a placeholder if not
    if not email:
        email = "N/A"
    
    rec_values = (
        str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, str(latlong),
        city, state, country, act_name, act_mail, act_mob, name, email, str(res_score),
        timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
        courses, pdf_name
    )
    
    try:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
        print("Data inserted successfully!")
    except pymysql.Error as e:
        connection.rollback()
        print(f"Error inserting data: {e}")

#inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()

# Initialize plotfeed_data as None
plotfeed_data = None

#Page Configuration
st.set_page_config(
   page_title="Resume Insight",
   page_icon='./Logo/recommend.png',
)

#Main function

def run():
    
    # Logo and Heading
    img = Image.open('./Logo/RESUME.png')
    st.image(img)
    st.title("Resume Insight")

    #Dropdown menu
    selection = st.selectbox(" ", ("", "User", "Admin"))
    
    #Buttons for User and Admin
    if selection == "User":
        if st.session_state.state != 'feedback':
            #Collecting Information
            act_name = st.text_input('Name*')
            act_mail = st.text_input('Mail*')
            act_mob  = st.text_input('Mobile Number*')
            sec_token = secrets.token_urlsafe(12)
            host_name = socket.gethostname()
            ip_add = socket.gethostbyname(host_name)
            dev_user = os.getlogin()
            os_name_ver = platform.system() + " " + platform.release()
            g = geocoder.ip('me')
            latlong = g.latlng
            geolocator = Nominatim(user_agent="http")
            location = geolocator.reverse(latlong, language='en')
            address = location.raw['address']
            cityy = address.get('city', '')
            statee = address.get('state', '')
            countryy = address.get('country', '')  
            city = cityy
            state = statee
            country = countryy


            #Upload Resume
            st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
            
            #file upload in pdf format
            pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
            if pdf_file is not None:
                with st.spinner('Processing...'):
                    time.sleep(4)
        
                #saving the uploaded resume to folder
                save_image_path = './Uploaded_Resumes/'+pdf_file.name
                pdf_name = pdf_file.name
                with open(save_image_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                show_pdf(save_image_path)

                #parsing and extracting whole resume 
                resume_data = ResumeParser(save_image_path).get_extracted_data()
                if resume_data:
                
                    #get the whole resume data into resume_text
                    resume_text = pdf_reader(save_image_path)

                    #showing Analyzed data from (resume_data)
                    st.header("**Resume Analysis**")
                    st.success("Hello "+ resume_data['name'])
                    st.subheader("**Basic Information:**")
                    try:
                        st.text('Name: '+resume_data['name'])
                        st.text('Email: ' + resume_data['email'])
                        st.text('Contact: ' + resume_data['mobile_number'])
                        st.text('Degree: '+str(resume_data['degree']))                    
                        st.text('Resume pages: '+str(resume_data['no_of_pages']))

                    except:
                        pass
                    #Predicting Candidate Experience Level 

                    #Trying with different possibilities
                    cand_level = ''
                    if resume_data['no_of_pages'] < 1:                
                        cand_level = "NA"
                        st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                    
                    #if internship then intermediate level
                    elif 'INTERNSHIP' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'INTERNSHIPS' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'Internship' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'Internships' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    
                    #if Work Experience/Experience then Experience level
                    elif 'EXPERIENCE' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'WORK EXPERIENCE' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'Experience' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'Work Experience' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    else:
                        cand_level = "Fresher"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                    #Skills Analyzing and Recommendation
                    st.subheader("**Skills Recommendation**")
                    
                    #Current Analyzed Skills
                    keywords = st_tags(label='### Your Current Skills',
                    text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                    #Keywords for Recommendation
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                    n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                    #Skill Recommendation              
                    recommended_skills = []
                    reco_field = ''
                    rec_course = ''

                    #condition starts to check skills from keywords and predict field
                    for i in resume_data['skills']:
                    
                        #Data science recommendation
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = 'Data Science'
                            st.success("** Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '2')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = course_recommender(ds_course)
                            break

                        #Web development recommendation
                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field = 'Web Development'
                            st.success("** Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '3')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = course_recommender(web_course)
                            break

                        #Android App Development
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field = 'Android Development'
                            st.success("** Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = course_recommender(android_course)
                            break

                        #IOS App Development
                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field = 'IOS Development'
                            st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '5')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = course_recommender(ios_course)
                            break

                        #Ui-UX Recommendation
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field = 'UI-UX Development'
                            st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = course_recommender(uiux_course)
                            break

                        #For No Recommendations
                        elif i.lower() in n_any:
                            print(i.lower())
                            reco_field = 'NA'
                            st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                            recommended_skills = ['No Recommendations']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Currently No Recommendations',value=recommended_skills,key = '6')
                            st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                            #course recommendation
                            rec_course = "Sorry! Not Available for this Field"
                            break


                    #Resume Scorer & Resume Writing Tips
                    st.subheader("**Resume Tips & Ideas**")
                    resume_score = 0
                    
                    if 'Objective' or 'Summary' in resume_text:
                        resume_score = resume_score+6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                    if 'Education' or 'School' or 'College'  in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                    if 'EXPERIENCE' in resume_text:
                        resume_score = resume_score + 16
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                    elif 'Experience' in resume_text:
                        resume_score = resume_score + 16
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                    if 'INTERNSHIPS'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'INTERNSHIP'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internships'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internship'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                    if 'SKILLS'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'SKILL'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'Skills'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'Skill'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                    if 'HOBBIES' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    elif 'Hobbies' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                    if 'INTERESTS'in resume_text:
                        resume_score = resume_score + 5
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                    elif 'Interests'in resume_text:
                        resume_score = resume_score + 5
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                    if 'ACHIEVEMENTS' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    elif 'Achievements' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                    if 'CERTIFICATIONS' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certifications' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certification' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                    if 'PROJECTS' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'PROJECT' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Projects' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Project' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #ffffff;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                    st.subheader("**Resume Score**")
                    
                    st.markdown(
                        """
                        <style>
                            .stProgress > div > div > div > div {
                                background-color: #d73b5c;
                            }
                        </style>""",
                        unsafe_allow_html=True,
                    )

                    #Score Bar
                    my_bar = st.progress(0)
                    score = 0
                    for percent_complete in range(resume_score):
                        score +=1
                        time.sleep(0.1)
                        my_bar.progress(percent_complete + 1)

                    #Score
                    st.success('** Your Resume Writing Score: ' + str(score)+'**')
                    st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                    #print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                    #Getting Current Date and Time
                    ts = time.time()
                    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    timestamp = str(cur_date+'_'+cur_time)


                    #Calling insert_data to add all the data into user_data                
                    insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                    #Recommending Resume Writing Video
                    st.header("**Bonus Video for Resume Writing Tips**")
                    resume_vid = random.choice(resume_videos)
                    st.video(resume_vid)

                    #Recommending Interview Preparation Video
                    st.header("**Bonus Video for Interview Tips**")
                    interview_vid = random.choice(interview_videos)
                    st.video(interview_vid)

                else:
                    st.error('Something went wrong!')                


                    st.write(" ")

        # CODE FOR FEEDBACK SIDE
        if st.session_state.state != 'feedback':
            if st.button('Feedback'):
                st.session_state.state = 'feedback'         
        #CODE FOR FEEDBACK SIDE
        else:   
            #timestamp 
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date+'_'+cur_time)

            #Feedback Form
            with st.form("my_form"):
                st.write("Feedback form")            
                feed_name = st.text_input('Name')
                feed_email = st.text_input('Email')
                feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
                comments = st.text_input('Comments')
                Timestamp = timestamp        
                submitted = st.form_submit_button("Submit")
                if submitted:
                    #add data into user feedback
                    insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                    #success
                    st.success("Thanks! Your Feedback was recorded.") 

            #fetch data from user feedback table
            #query = 'select * from user_feedback'        
            #plotfeed_data = pd.read_sql(query, connection)                        
            try:
            # Example: Fetching data from a database
                query = 'SELECT * FROM user_feedback'
                cursor.execute(query)
                plotfeed_data = cursor.fetchall()  # Assign fetched data to plotfeed_data
    
            except Exception as e:
                st.error(f"Error fetching data: {e}")
                plotfeed_data = []  # Assign an empty list if data retrieval fails

            if plotfeed_data:
                # Extract feed_score values from plotfeed_data tuples
                feed_scores = [row[3] for row in plotfeed_data]  # Assuming feed_score is at index 2

                # Create a Pandas Series from the extracted feed_scores
                feed_scores_series = pd.Series(feed_scores)

                # Calculate value counts to prepare for plotting
                value_counts = feed_scores_series.value_counts()

                # Plotting pie chart for user ratings
                st.subheader("**Past User Ratings**")
                fig = px.pie(
                    values=value_counts.values, 
                    names=value_counts.index, 
                    title="User Rating Scores (1-5)", 
                    color_discrete_sequence=px.colors.sequential.Aggrnyl
                )
                st.plotly_chart(fig)

                # Fetching comment history
                comments = [(row[1], row[4]) for row in plotfeed_data]  # Assuming feed_name at index 0 and comments at index 3

                st.subheader("**User Comments**")
                dff = pd.DataFrame(comments, columns=['User', 'Comment'])
                st.dataframe(dff, width=1000)
            else:
                # Handle case where plotfeed_data is empty or not retrieved successfully
                st.warning("No user feedback data available.")

                                
    if selection == "Admin":
        if st.session_state.state != 'admin_logged_in':
            #Admin Login
            st.title("Admin Login")
            ad_user = st.text_input("Username")
            ad_password = st.text_input("Password", type='password')

            if st.button('Login'):
                #Credentials 
                if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                    st.success('Welcome to Admin Side')
                    st.session_state.state = 'admin_logged_in'
                else:
                    st.error("Wrong ID & Password Provided")  
                    
        elif st.session_state.state == 'admin_logged_in':
                connection = establish_connection()
                if connection:
                    

                    # Implement your admin dashboard logic here
                    #cursor = connection.cursor()
                    # Fetch user data based on filter option 
                    cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                    datanalys = cursor.fetchall()
                    plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                        
                    cursor.execute('''SELECT act_name, ID, act_mail, act_mob, convert(Predicted_Field using utf8), Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country from user_data''')
                    data = cursor.fetchall()                

                    st.header("**User's Data**")
                    df = pd.DataFrame(data, columns=['Name', 'ID', 'Mail', 'Mobile Number', 'Predicted Field',
                                                    'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                    'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                    'City', 'State', 'Country'])
                    
                    #View the dataframe
                    st.dataframe(df)
                    
                    #Downloading Report 
                    st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                    cursor.execute('''SELECT * from user_feedback''')
                    data = cursor.fetchall()


                    display_pdf_for_id()
                    
                    
                    st.header("**User's Feedback Data**")
                    df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                    st.dataframe(df)

                    #fetch data from user_feedback
                    query = 'select * from user_feedback'
                    plotfeed_data = pd.read_sql(query, connection)                        

                    #Analyzing All the Data in pie charts

                    labels = plotfeed_data.feed_score.unique()
                    values = plotfeed_data.feed_score.value_counts()
                    
                    #Pie chart for user ratings
                    st.subheader("**User Rating's**")
                    fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 ", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                    st.plotly_chart(fig)
                    
                    labels = plot_data.Predicted_Field.unique()
                    values = plot_data.Predicted_Field.value_counts()

                    #Pie chart for predicted field recommendations
                    st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                    fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills ', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                    st.plotly_chart(fig)
                
                    labels = plot_data.User_Level.unique()
                    values = plot_data.User_Level.value_counts()

                    #Pie chart for User's Experienced Level
                    st.subheader("**Pie-Chart for User's Experienced Level**")
                    fig = px.pie(df, values=values, names=labels, title="Pie-Chart for User's Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig)
                
                    labels = plot_data.resume_score.unique()                
                    values = plot_data.resume_score.value_counts()

                    #Pie chart for Resume Score
                    st.subheader("**Pie-Chart for Resume Score**")
                    fig = px.pie(df, values=values, names=labels, title='From 1 to 100', color_discrete_sequence=px.colors.sequential.Agsunset)
                    st.plotly_chart(fig)

                    labels = plot_data.City.unique()
                    values = plot_data.City.value_counts()

                    #Pie chart for City
                    st.subheader("**Pie-Chart for City**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based On City', color_discrete_sequence=px.colors.sequential.Jet)
                    st.plotly_chart(fig)

                    labels = plot_data.State.unique()
                    values = plot_data.State.value_counts()

                    #Pie chart for State
                    st.subheader("**Pie-Chart for State**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based on State ', color_discrete_sequence=px.colors.sequential.PuBu_r)
                    st.plotly_chart(fig)

                    # Fetch user data based on filter option
                    filter_option = st.selectbox("Filter by:", ['Resume Score', 'Predicted Field', 'User Level'])

                    if filter_option == 'Resume Score':
                        cursor.execute('''
                            SELECT  act_name, ID, act_mail, act_mob,
                            convert(User_level using utf8),  convert(Predicted_Field using utf8), resume_score,
                            convert(Actual_skills using utf8), convert(Recommended_skills using utf8)
                            FROM user_data
                            ORDER BY resume_score DESC
                        ''')
                        data = cursor.fetchall()
                        
                        columns = ['Name', 'ID', 'Email',' Mobile', 'User Level', 'Predicted Field', 'Resume Score',
                                'Actual Skills', 'Recommended Skills'
                                ]

                    elif filter_option == 'Predicted Field':
                        cursor.execute('''
                            SELECT  act_name, ID, act_mail, act_mob,
                            convert(User_level using utf8),  convert(Predicted_Field using utf8), resume_score,
                            convert(Actual_skills using utf8), convert(Recommended_skills using utf8)
                            FROM user_data
                            ORDER BY convert(Predicted_Field using utf8)
                        ''')
                        data = cursor.fetchall()
                        
                        columns = ['Name', 'ID', 'Email',' Mobile', 'User Level', 'Predicted Field', 'Resume Score',
                                'Actual Skills', 'Recommended Skills']

                    elif filter_option == 'User Level':
                        cursor.execute('''
                            SELECT  act_name, ID, act_mail, act_mob,
                            convert(User_level using utf8),  convert(Predicted_Field using utf8), resume_score,
                            convert(Actual_skills using utf8), convert(Recommended_skills using utf8)
                            FROM user_data
                            ORDER BY FIELD(convert(User_level using utf8), 'Experience', 'Intermediate', 'Fresher')
                        ''')
                        data = cursor.fetchall()
                        
                        columns = ['Name', 'ID', 'Email',' Mobile', 'User Level', 'Predicted Field', 'Resume Score',
                                'Actual Skills', 'Recommended Skills']

                    # Create DataFrame from fetched data
                    df = pd.DataFrame(data, columns=columns)

                    # Display DataFrame
                    st.header(f"User's Data - Sorted by {filter_option}")
                    st.dataframe(df)


                    #connection.close()
                    
    
    #About button in top right corner
    if st.button("About"):
        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the dropdown menu choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            <br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        ''',unsafe_allow_html=True)  
   
    #Creating Database and Table


    #Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    #Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)

run()
